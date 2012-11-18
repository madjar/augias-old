import unittest
import transaction
import re

from pyramid import testing
import warnings

from .models import DBSession

# Cached because this may take some time
_email_assertion = None
_email_assertion = ('sallaberry8303@personatestuser.org', 'eyJhbGciOiJSUzI1NiJ9.eyJwdWJsaWMta2V5Ijp7ImFsZ29yaXRobSI6IlJTIiwibiI6IjEzMzkyMjQ2MzcxNTI1ODc0NjE4MDA1NjYzMjY5MTkyNDgwMjcyODc1MzY2ODQ5MjkwNDY1MDcyNzAzNzk4Njk5MDE0NDcxNDY3NDkxMjQ1NDUxNjg5NTQ3MTE1MzA1MDg5ODU5MjE4MTQyODIzNjkwMDc1ODgzMzg2NTQ4MzM2MTcxMzIwNDc5MzY3NDQzMjExMjYwMDA3NjY1MTg2MjY3NjE1MTI1NDgzMjUwMTAzNjgyNjQ2MDEzOTc1MDYzODMzMjU3Nzg2MDYyOTQyOTIwNDQxNjA0NTY5MjQ0MjA2MjIyMDg2ODQzMDgyMzUwMDU3MzE0NjcxODI1NDA1ODIzNDQ1MDE2MDE0ODA5MTA1MDMyOTkxNTM0Nzg3MTE0ODQ0OTQ3NzkzMDUwOTM1MDEyMDI1NjEzNTg1MDg3NDk2NDU2NTgyNDAwODAwNzA0Mjk0NzcyMjUzNDU3NzA3NTYxNTEwODM4MDM5MjUzODE4MDM3Njk5MDk5MTM3NjM3MTE1ODgwMTg0MDEzODU3NTQ2MzAwNzU4Mjk2NTU5NjIxMzEyNjM2MTAxNTU0MTU2MjE3MzIzODQxNTkwMTI4OTE2ODk2MTM2MTIxODg5NDYwNjU5Njg1NDk1NDI1NTAxMDA3NDI2MTgxNzQyMzU1NDc1NjI0NDA3NzgxNjQ1NTgxMTM3NjA3NTk4NzU1MDIyMzk3NzQ5Njk1NjE1MTkzNDMwMTAzODk4MTgzNTExMzYzNjkxNTExMTk2MTI2ODY0NDAxMzQ5OTU3NTgxNzIzNzE0NDUwNjI4MDAwMzU5ODkyNzk3OTQyMDUzIiwiZSI6IjY1NTM3In0sInByaW5jaXBhbCI6eyJlbWFpbCI6InNhbGxhYmVycnk4MzAzQHBlcnNvbmF0ZXN0dXNlci5vcmcifSwiaWF0IjoxMzUzMjQ5NzEwMTY4LCJleHAiOjEzNTMzMzYxMTAxNjgsImlzcyI6ImxvZ2luLnBlcnNvbmEub3JnIn0.hNRQQg7WgY9doQm3muNKzdmhK-uAAoTBYuQB-gDtT-f_320B4ARge_FngUAmlTDEq89bcXpz8UQvTBKePP5yJu5JJX0nnQyZbRKlDfMGMny1M5uG3tjbLaeGGIi6HpQSCT2_PupP14cIeRgW-u0b4ob-PcTTwhi55SjASHRHcznfidGGn0d2fHkOBEUQ9K7f8TNWED6r9bmlf-btenuNe4e8QhC9HUoaZYE-2Jrc20Coe5PByqhffcdEmzE9lg_9RPf2U_tKRhunGc5DJKQGcABq0ZUQ3kpC9dgbfhL3aRJMC3WojYOs3wzO04xuxNvGNwrgF4DqrWCZyfwKLeL-WQ~eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjEzNTMyNTMzMDgwMDAsImF1ZCI6Imh0dHA6Ly9leGFtcGxlLmNvbSJ9.IB5vfLZEJyyqesvnCdp1kW9BpHlRUrBjzt5xdZmOA55lKhX4XXfD0r-X6s2lfRjQeoTFEpo2S-c6vpe7t1ZQ925IyJsd33z9zU6FQYzCZ8t6prdUs3Idn5nrOcNaGyvU52y49s5vyqBzZHUQPl-g92k6WjZIkf_BNu4VSSQ7fWWY83hpUcpjswASkdafLX4Zkqtsdd2-b4JWhmuyqAwKMYq-C4mOAeGlaff9aKXtJrJR4GWgeVMafYJSPPfUIE5EwY1X4uckAthkgqMnS4qzd1mqTNHzqJPacIOcCKi08D3wKc6FrrJdqaL8p3nyGfQ8m3P7dqOXioqiPtj1nopOvA')
def get_email_and_assertion(audience):
    global _email_assertion
    if not _email_assertion:
        import requests
        from urllib.parse import quote_plus
        r = requests.get('http://personatestuser.org/email_with_assertion/%s'%quote_plus(audience))
        _email_assertion = r.json['email'], r.json['assertion']
        print(_email_assertion)
    return _email_assertion


def create_and_populate(engine=None):
    from .models import Base, Task
    Base.metadata.create_all(engine)
    with transaction.manager:
        task = Task(name='some task', length=15, periodicity=7)
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
        self.assertIn('<h2>Logs for some task</h2>', res.unicode_body)

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