import datetime
from operator import attrgetter
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
    tasks = list(context)
    urgent_tasks = [t for t in tasks if t.emergency >= 0.8]
    urgent_tasks.sort(key=attrgetter('emergency'), reverse=True)
    return {'tasks': tasks, 'urgent_tasks': urgent_tasks}


@view_config(context=Task, name='execute', permission='execute')
def execute(context, request):
    try:
        length = int(request.params['length'])
    except ValueError:
        request.session.flash('Invalid length "%s"'%request.params['length'])
    else:
        executor = request.user if not request.params.get('collective') else None
        context.execute(executor, length)
        request.session.flash('Task executed')
    return HTTPFound(request.resource_url(context))

@view_config(context=Task, renderer='task.mako')
def task(context, request):
    return {'task': context}