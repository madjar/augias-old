import unittest
import re
import transaction
import warnings
from augias.models import DBSession


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


def populate(email):
    from augias.models import Base, Task, Notebook, User
    notebook = Notebook(name='some notebook')
    task = Task(name='some task', periodicity=7, notebook=notebook)
    DBSession.add_all([notebook, task])
    if email:
        user = User(email=email, notebooks=[notebook])
        DBSession.add(user)

from augias.tests import TestCase
class FunctionalTests(TestCase):
    def setUp(self):
        from augias import main
        config = {
            'sqlalchemy.url': self.db_url,
            'persona.audiences': 'http://example.com',
            'persona.secret': 'Testing secret',
            'persona.verifier': 'browserid.LocalVerifier',
            'mako.directories': 'augias:templates',
            }
        with warnings.catch_warnings():  # For browserid.LocalVerifier
            warnings.simplefilter("ignore")
            app = main({}, **config)
        super().setUp()  # This overide the app db engine

        self.email, self.assertion = get_email_and_assertion('http://example.com')
        populate(email=self.email)

        from webtest import TestApp
        self.testapp = TestApp(app)


    def _login(self):
        res = self.testapp.get('/', status=403)
        token = re.findall(r"value='([0-9a-f]*)'", res.unicode_body)[0]
        self.testapp.post('/login', {'assertion': self.assertion,
                                     'csrf_token': token,
                                     'came_from': '/'})

    def test_index(self):
        self._login()
        res = self.testapp.get('/')
        res = res.follow()

        self.assertIn('some task', res)

    def test_task(self):
        self._login()
        res = self.testapp.get('/')
        res = res.follow()
        res = res.click('some task')

        self.assertIn('<h2>some task</h2>', res)

    def test_unauthorized(self):
        res = self.testapp.get('/', status=403)

    def test_execute(self):
        self._login()
        res = self.testapp.get('/')
        res = res.follow()
        res = res.click('some task')

        form = res.forms['execution']
        form['length'] = 15
        res = form.submit(status=302)
        res = res.follow()
        self.assertIn('(15 mins)', res)
        self.assertIn(self.email, res)
