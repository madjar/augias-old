from operator import attrgetter
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from demain.utils import FlashMessage

from .models import (
    DBSession,
    Task, Page, Root, User)

@view_config(context=Root)
def home(request):
    if not request.user:
        raise Forbidden()
    pages = request.user.pages
    if len(pages) == 1:
        return HTTPFound(request.resource_path(pages[0]))
    else:
        raise Exception('Multiple pages : not handled yet')


@view_config(context=Root, name='change_username', check_csrf=True, request_method='POST')
def change_username(context, request):
    request.user.name = request.params['username']
    return HTTPFound(request.referer)


@view_config(context=Page, renderer='page.mako', permission='access')
def page(context, request):
    tasks = list(context)
    urgent_tasks = [t for t in tasks if t.emergency >= 0.8]
    urgent_tasks.sort(key=attrgetter('emergency'), reverse=True)
    return {'tasks': tasks, 'urgent_tasks': urgent_tasks}


@view_config(context=Task, renderer='task.mako', permission='access')
def task(context, request):
    return {'task': context}

@view_config(context=Task, name='execute', permission='access')
def execute(context, request):
    try:
        if not request.params['length']:
            length = None
        elif ':' in request.params['length']:
            parts = request.params['length'].split(':')
            if len(parts) > 3:
                raise ValueError()
            length = int(parts[-2])
            if int(parts[-1]) >= 30:
                length +=1
            if len(parts) == 3:
                length += 60 * int(parts[0])
        else:
            length = int(request.params['length'])
    except ValueError:
        request.flash_error('Invalid length "%s"'%request.params['length'])
    else:
        executor_email = request.params['executor']
        executor = DBSession.query(User).filter_by(email=executor_email).one() if executor_email else None
        context.execute(executor, length)
        request.flash_success('Task executed')
    return HTTPFound(request.resource_url(context))
