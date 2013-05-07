import warnings
import logging
from webtest import TestApp
from augias import main
from augias.models import Base, DBSession

# Somehow, basicConfig gets called by behave. Make a bug report ?
logging.root.addHandler(logging.NullHandler())


class ModelsContainer(dict):
    def __getitem__(self, item):
        return DBSession.merge(super().__getitem__(item))


def before_scenario(context, step):
    import augias.tests
    config = {
        'sqlalchemy.url': 'sqlite://',
        'persona.audiences': 'http://example.com',
        'persona.secret': 'Testing secret',
        'persona.verifier': 'browserid.LocalVerifier',
        'mako.directories': 'augias:templates',
        'cache.backend': 'null',
        }
    with warnings.catch_warnings():  # For browserid.LocalVerifier
        warnings.simplefilter("ignore")
        app = main({}, **config)
    Base.metadata.create_all()
    context.app = TestApp(app)

    context.last = ModelsContainer()


def after_scenario(context, step):
    Base.metadata.drop_all()
    DBSession.remove()

    from augias.utils import cache
    del cache.backend
