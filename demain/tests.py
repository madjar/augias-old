import unittest
import transaction
import re

from pyramid import testing
import warnings

from .models import DBSession

# Cached because this may take some time
# TODO : cache this on the disk
_email_assertion = None
def get_email_and_assertion(audience):
    global _email_assertion
    if not _email_assertion:
        import requests
        from urllib.parse import quote_plus
        r = requests.get('http://personatestuser.org/email_with_assertion/%s'%quote_plus(audience))
        _email_assertion = r.json['email'], r.json['assertion']
    return _email_assertion


def create_and_populate(engine=None, email=None):
    from .models import Base, Task, Page, User
    Base.metadata.create_all(engine)
    with transaction.manager:
        page = Page(name='some page')
        task = Task(name='some task', periodicity=7, page=page)
        DBSession.add_all([page, task])
        if email:
            user = User(email=email, pages=[page])
            DBSession.add(user)


class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        create_and_populate(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import page
        from .models import Page
        p = Page.query().get(1)
        request = testing.DummyRequest()
        result = page(p, request)
        self.assertEqual(list(result['tasks'])[0].name, 'some task')

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from demain import main
        config = {
            'sqlalchemy.url': 'sqlite://',
            'persona.audiences': 'http://example.com',
            'persona.secret': 'Testing secret',
            'persona.verifier': 'browserid.LocalVerifier',
            'mako.directories': 'demain:templates',
            'pyramid.debug_authorization': 'true',
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
        token = re.findall(r'csrf_token:\s"([0-9a-f]*)"', res.unicode_body)[0]
        self.testapp.post('/login', {'assertion': self.assertion, 'csrf_token': token})

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
        form = res.form
        form['length'] = 15
        form['collective'] = 0
        res = form.submit(status=302)
        res = res.follow()
        self.assertIn('for 15 minutes', res.unicode_body)
        self.assertIn('by %s'%self.email, res.unicode_body)