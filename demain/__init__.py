from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    get_user, Root)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory=Root)
    config.include('pyramid_persona')
    authn_policy = AuthTktAuthenticationPolicy(settings['persona.secret'],
                                               hashalg='sha512',
                                               max_age=60*60*24*30) # 1 month
    config.set_authentication_policy(authn_policy)

    config.include('demain.utils.flash')
    config.add_request_method(get_user, 'user', reify=True)

    config.set_default_permission('access')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()

