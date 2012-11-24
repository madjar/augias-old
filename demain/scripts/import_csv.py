import csv
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
    Base.metadata.create_all(engine)
    with transaction.manager:
        with open('/files/taches.csv', encoding='latin1') as f:
            reader = csv.reader(f, delimiter=';')
            for name, length, periodicity in reader:
                task = Task(name=name, length=length, periodicity=periodicity)
                DBSession.add(task)
