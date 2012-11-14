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


@view_config(context=Task, name='execute', permission='execute')
def execute(context, request):
    try:
        length = int(request.params['length'])
    except ValueError:
        request.session.flash('Invalid length "%s"'%request.params['length'])
    else:
        context.execute(request.user, length)
    return HTTPFound(request.resource_url(context))

@view_config(context=Task, renderer='task.mako')
def task(context, request):
    return {'task': context}