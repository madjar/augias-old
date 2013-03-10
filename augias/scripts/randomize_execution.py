import datetime
import random
import sys
from pyramid.paster import setup_logging, get_appsettings
from sqlalchemy import engine_from_config
import transaction
from augias.models import Task, DBSession, get_user

def main(argv=sys.argv):
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    with transaction.manager:
        user = get_user('tagada@example.com')
        for t in DBSession.query(Task).all():
            if random.random() < 0.2:
                t.last_execution = None
            else:
                exec_time = datetime.datetime.now() - datetime.timedelta(days=t.periodicity * random.random() * 1.5)
                t.execute(user, 10, exec_time)

if __name__ == '__main__':
    main()
