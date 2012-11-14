import datetime
import random
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from demain import TaskContainer

from .models import (
    DBSession,
    Task)

@view_config(context=TaskContainer, renderer='index.mako')
def index(context, request):
    return {'tasks': context}


@view_config(context=Task, name='execute')
def execute(request):
    if not request.user:
        raise Forbidden()
    length = int(request.params['length']) # TODO validation (ValueError)
    task = DBSession.query(Task).get(request.matchdict['task_id'])
    task.execute(request.user, length)
    return HTTPFound(request.route_path('index'))

@view_config(context=Task, renderer='task.mako')
def task(context, request):
    return {'task': context}