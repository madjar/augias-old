import re
import transaction
from augias.models import DBSession, User


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



    def _login(self):
        res = self.testapp.get('/', status=403)

step_matcher('re')

@given('a logged-in user named "(?P<name>\w*)"')
def step(context, name):
    email, assertion = get_email_and_assertion('http://example.com')
    with transaction.manager:
        user = User(email=email, name=name)
        DBSession.add(user)

    result = context.app.get('/', status = 403)
    token = re.findall(r"value='([0-9a-f]*)'", result.unicode_body)[0]
    context.app.post('/login', {'assertion': assertion,
                                'csrf_token': token,
                                'came_from': '/'})

step_matcher('parse')
