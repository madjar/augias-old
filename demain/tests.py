import unittest
import transaction
import re

from pyramid import testing
import warnings

from .models import DBSession

# Cached because this may take some time
_email_assertion = None
def get_email_and_assertion(audience):
    global _email_assertion
    if not _email_assertion:
        import requests
        from urllib.parse import quote_plus
        r = requests.get('http://personatestuser.org/email_with_assertion/%s'%quote_plus(audience))
        _email_assertion = r.json['email'], r.json['assertion']
    return _email_assertion


def create_and_populate(engine=None):
    from .models import Base, Task
    Base.metadata.create_all(engine)
    with transaction.manager:
        task = Task(name='some task', periodicity=7)
        DBSession.add(task)

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
        from .views import index
        from .resources import TaskContainer
        request = testing.DummyRequest()
        result = index(TaskContainer(request), request)
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
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            app = main({}, **config)
        create_and_populate()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        DBSession.remove()

    def _login(self):
        email, assertion = get_email_and_assertion('http://example.com')
        res = self.testapp.get('/')
        token = re.findall(r'csrf_token:\s"([0-9a-f]*)"', res.unicode_body)[0]
        self.testapp.post('/login', {'assertion': assertion, 'csrf_token': token})
        return email

    def test_index(self):
        res = self.testapp.get('/', status=200)
        self.assertIn('some task', res.unicode_body)

    def test_task(self):
        res = self.testapp.get('/1')
        self.assertIn('<h2>some task</h2>', res.unicode_body)

    def test_execute_unauthorized(self):
        res = self.testapp.get('/1')
        res = res.form.submit(status=403)

    def test_execute(self):
        email = self._login()
        res = self.testapp.get('/1')
        form = res.form
        form['length'] = 15
        form['collective'] = 0
        res = form.submit(status=302)
        res = res.follow()
        self.assertIn('for 15 minutes by %s'%email, res.unicode_body)