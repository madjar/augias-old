import datetime
from operator import attrgetter
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sqlalchemy import func, or_
from demain.utils import FlashMessage

from .models import (
    DBSession,
    Task, Page, Root, User, Execution)

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


@view_config(context=Root, name='new_page', permission='access',
             request_method='POST', check_csrf=True)
def new_page(context, request):
    page = Page(name=request.params['name'], users=[request.user])
    DBSession.add(page)
    DBSession.flush()
    return HTTPFound(request.resource_url(page))

@view_config(context=Page, name='delete', permission='access',
             request_method='GET', renderer='page_delete.mako')
def page_delete(context, request):
    return {'page': context}


@view_config(context=Page, name='delete', permission='access',
             request_method='POST', check_csrf=True)
def page_delete_post(context, request):
    if len(context.users) == 1:
        DBSession.delete(context)
    else:
        context.users.remove(request.user)
    return HTTPFound('/')


@view_config(context=Page, renderer='page.mako', permission='access')
def page(context, request):
    tasks = list(context)
    urgent_tasks = [t for t in tasks if t.emergency >= 0.8]
    urgent_tasks.sort(key=attrgetter('emergency'), reverse=True)

    time_spend_today = (DBSession.query(func.sum(Execution.length))
                        .filter(or_(Execution.executor==request.user,
                                    Execution.executor==None))
                        .filter(func.date(Execution.time) == datetime.date.today())
                        .scalar()) or 0
    # TODO this could be configurable
    time_left = 15 - time_spend_today
    suggested_something = False
    for t in urgent_tasks:
        if time_left <= 0:
            break
        t.suggested = True
        time_left -= t.mean_execution
        suggested_something = True

    last_executions = Execution.query().order_by(Execution.time.desc()).limit(5).all()
    return {
        'page': context,
        'tasks': tasks,
        'urgent_tasks': urgent_tasks,
        'last_executions': last_executions,
        'suggested_something': suggested_something,
        }


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
