from pyramid.view import view_config

from .models import (
    DBSession,
    Task)

@view_config(route_name='index', renderer='index.mako')
def index(request):
    tasks = DBSession.query(Task).all()
    return {'tasks': tasks}
