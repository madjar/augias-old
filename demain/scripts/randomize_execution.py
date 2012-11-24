import csv
import datetime
import random
import sys
from pyramid.paster import setup_logging, get_appsettings
from sqlalchemy import engine_from_config
import transaction
from demain import DBSession, Base
from demain.models import Task

def main(argv=sys.argv):
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    with transaction.manager:
        for t in DBSession.query(Task).all():
            if random.random() < 0.2:
                t.last_execution = None
            else:
                t.last_execution = datetime.datetime.now() - datetime.timedelta(days=t.periodicity * random.random() * 1.5)

if __name__ == '__main__':
    main()