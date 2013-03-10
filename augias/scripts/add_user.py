import sys
from augias.models import User, DBSession
from pyramid.paster import bootstrap, setup_logging
import transaction


def main(argv=sys.argv):
    config_uri = argv[1]
    env = bootstrap(config_uri)
    setup_logging(config_uri)
    with transaction.manager:
        for email in argv[2:]:
            print('Adding user {}'.format(email))
            user = User(email=email)
            DBSession.add(user)

    env['closer']()

if __name__ == '__main__':
    main()
