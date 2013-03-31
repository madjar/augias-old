import warnings
import logging
from webtest import TestApp
from augias import main
from augias.models import Base, DBSession

# Somehow, basicConfig gets called by behave. Make a bug report ?
logging.root.addHandler(logging.NullHandler())


def before_scenario(context, step):
    config = {
        'sqlalchemy.url': 'sqlite://',
        'persona.audiences': 'http://example.com',
        'persona.secret': 'Testing secret',
        'persona.verifier': 'browserid.LocalVerifier',
        'mako.directories': 'augias:templates',
        }
    with warnings.catch_warnings():  # For browserid.LocalVerifier
        warnings.simplefilter("ignore")
        app = main({}, **config)
    Base.metadata.create_all()
    context.app = TestApp(app)


def after_scenario(context, step):
    Base.metadata.drop_all()
    DBSession.remove()
