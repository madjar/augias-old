import os
import sys

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging
from alembic.config import Config
from alembic import command
from pyramid.scripts.common import parse_vars
import configparser

from ..models import DBSession, Base

# Backported from pyramid master (after 1.4)
from paste.deploy import loadapp, appconfig
from pyramid.paster import _getpathsec
def get_appsettings(config_uri, name=None, options=None):
    path, section = _getpathsec(config_uri, name)
    config_name = 'config:%s' % path
    here_dir = os.getcwd()
    return appconfig(config_name, name=section, relative_to=here_dir, global_conf=options)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    alembic_cfg = Config(config_uri)
    alembic_cfg.file_config = configparser.SafeConfigParser(options)
    alembic_cfg.file_config.read([alembic_cfg.config_file_name])
    command.stamp(alembic_cfg, "head")
