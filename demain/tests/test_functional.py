import unittest
import re
import transaction
import warnings
from demain.models import DBSession


# Cached because this may take some time
ASSERTION_CACHE_FILE = '/tmp/persona_email_assertion'
# TODO : I should make this more clean at some point, maybe in a library
_email_assertion = None
def get_email_and_assertion(audience):
    global _email_assertion
    if not _email_assertion:
        import pickle
        try:
            import datetime
            from browserid.utils import unbundle_certs_and_assertion, decode_json_bytes
            # Get one from the cache, and check it's expiration
            email_assertion = pickle.load(open(ASSERTION_CACHE_FILE, 'rb'))
            _, assertion = unbundle_certs_and_assertion(email_assertion[1])
            exp = decode_json_bytes(assertion.split('.')[1])['exp']
            expiration_date = datetime.datetime.utcfromtimestamp(exp/1000)
            if expiration_date > datetime.datetime.utcnow():
                # If it hasn't expired, return
                _email_assertion = email_assertion
                return email_assertion
        except FileNotFoundError:
            pass
            # If no good one is available, get a new one
        import requests
        from urllib.parse import quote_plus
        r = requests.get('http://personatestuser.org/email_with_assertion/%s'%quote_plus(audience))
        _email_assertion = r.json()['email'], r.json()['assertion']
        pickle.dump(_email_assertion, open(ASSERTION_CACHE_FILE, 'wb'))
    return _email_assertion


def create_and_populate(engine=None, email=None):
    from demain.models import Base, Task, Page, User
    Base.metadata.create_all(engine)
    with transaction.manager:
        page = Page(name='some page')
        task = Task(name='some task', periodicity=7, page=page)
        DBSession.add_all([page, task])
        if email:
            user = User(email=email, pages=[page])
            DBSession.add(user)


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from demain import main
        config = {
            'sqlalchemy.url': 'sqlite://',
            'persona.audiences': 'http://example.com',
            'persona.secret': 'Testing secret',
            'persona.verifier': 'browserid.LocalVerifier',
            'mako.directories': 'demain:templates',
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            app = main({}, **config)
        self.email, self.assertion = get_email_and_assertion('http://example.com')
        create_and_populate(email=self.email)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        DBSession.remove()

    def _login(self):
        res = self.testapp.get('/', status=403)
        token = re.findall(r"value='([0-9a-f]*)'", res.unicode_body)[0]
        self.testapp.post('/login', {'assertion': self.assertion,
                                     'csrf_token': token,
                                     'came_from': '/'})

    def test_index(self):
        self._login()
        res = self.testapp.get('/1', status=200)
        self.assertIn('some task', res.unicode_body)

    def test_task(self):
        self._login()
        res = self.testapp.get('/1/1')
        self.assertIn('<h2>some task</h2>', res.unicode_body)

    def test_unauthorized(self):
        res = self.testapp.get('/1', status=403)

    def test_execute(self):
        self._login()
        res = self.testapp.get('/1/1')
        form = res.forms['execution']
        form['length'] = 15
        res = form.submit(status=302)
        res = res.follow()
        self.assertIn('(15 mins)', res.unicode_body)
        self.assertIn(self.email, res.unicode_body)
