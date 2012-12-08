from operator import attrgetter
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from demain.utils import FlashMessage

from .models import (
    DBSession,
    Task, Page, Root)

@view_config(context=Root)
def home(request):
    if not request.user:
        raise Forbidden()
    pages = request.user.pages
    if len(pages) == 1:
        return HTTPFound(request.resource_path(pages[0]))
    else:
        raise Exception('Multiple pages : not handled yet')


@view_config(context=Page, renderer='page.mako', permission='access')
def page(context, request):
    tasks = list(context)
    urgent_tasks = [t for t in tasks if t.emergency >= 0.8]
    urgent_tasks.sort(key=attrgetter('emergency'), reverse=True)
    return {'tasks': tasks, 'urgent_tasks': urgent_tasks}


@view_config(context=Task, name='execute', permission='access')
def execute(context, request):
    try:
        if not request.params['length']:
            length = None
        else:
            length = int(request.params['length'])
    except ValueError:
        request.session.flash('Invalid length "%s"'%request.params['length'])
    else:
        executor = request.user if not request.params.get('collective') else None
        context.execute(executor, length)
        request.session.flash(FlashMessage('Task executed', 'success'))
    return HTTPFound(request.resource_url(context))

@view_config(context=Task, renderer='task.mako', permission='access')
def task(context, request):
    return {'task': context}