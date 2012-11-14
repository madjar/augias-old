import datetime
import random
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from .models import (
    DBSession,
    Task)

@view_config(route_name='index', renderer='index.mako')
def index(request):
    tasks = DBSession.query(Task).all()
    return {'tasks': tasks}


@view_config(route_name='execute')
def execute(request):
    if not request.user:
        raise Forbidden()
    length = int(request.params['length']) # TODO validation (ValueError)
    task = DBSession.query(Task).get(request.matchdict['task_id'])
    task.execute(request.user, length)
    return HTTPFound(request.route_path('index'))

@view_config(route_name='task', renderer='task.mako')
def task(request):
    task = DBSession.query(Task).get(request.matchdict['task_id'])
    return {'task': task}