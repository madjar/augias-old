import sys
from alembic.config import Config
from pyramid.scripts.common import parse_vars
import configparser
from alembic import command
from pyramid.paster import setup_logging


def main(argv=sys.argv):
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)

    alembic_cfg = Config(config_uri)
    alembic_cfg.file_config = configparser.SafeConfigParser(options)
    alembic_cfg.file_config.read([alembic_cfg.config_file_name])
    command.upgrade(alembic_cfg, "head")
