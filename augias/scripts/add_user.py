import sys
from augias.models import User, DBSession
from pyramid.paster import bootstrap, setup_logging
from pyramid.scripts.common import parse_vars
import transaction


def main(argv=sys.argv):
    config_uri = argv[1]
    options = [arg for arg in argv[2:] if '=' in arg]
    options = parse_vars(options)
    env = bootstrap(config_uri, options=options)
    setup_logging(config_uri)
    emails = [arg for arg in argv[2:] if '=' not in arg]
    with transaction.manager:
        for email in emails:
            print('Adding user {}'.format(email))
            user = User(email=email)
            DBSession.add(user)

    env['closer']()

if __name__ == '__main__':
    main()
