import datetime
from operator import attrgetter
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import NO_PERMISSION_REQUIRED
from sqlalchemy import func, or_
from demain.utils import FlashMessage

from .models import (
    DBSession,
    Task, Page, Root, User, Execution, UserNotFound)

def redirect(request, *args):
    return HTTPFound(request.resource_url(*args))

@view_config(context=Root, renderer='page_list.mako')
def home(context, request):
    pages = request.user.pages
    if not pages:
        page = Page(name="%s's page"%request.user.__html__(), users=[request.user])
        DBSession.add(page)
        DBSession.flush()
        return redirect(request, page)
    elif len(pages) == 1:
        return redirect(request, pages[0])
    else:
        return {'pages': pages}


@view_config(context=UserNotFound, renderer='not_invited.mako', permission=NO_PERMISSION_REQUIRED)
def user_not_invited(context, request):
    return {'email': context.args[0]}

@view_config(context=Root, name='change_username', check_csrf=True, request_method='POST')
def change_username(context, request):
    request.user.name = request.params['username']
    return HTTPFound(request.referer)


@view_config(context=Root, name='new_page',
             request_method='POST', check_csrf=True)
def new_page(context, request):
    page = Page(name=request.params['name'], users=[request.user])
    DBSession.add(page)
    DBSession.flush()
    return redirect(request, page)

@view_config(context=Page, name='delete',
             request_method='GET', renderer='page_delete.mako')
def page_delete(context, request):
    return {'page': context}


@view_config(context=Page, name='delete',
             request_method='POST', check_csrf=True)
def page_delete_post(context, request):
    if len(context.users) == 1:
        DBSession.delete(context)
    else:
        context.users.remove(request.user)
    return HTTPFound('/')


@view_config(context=Page, renderer='page.mako')
def page(context, request):
    tasks = list(context)
    urgent_tasks = [t for t in tasks if t.emergency >= 0.8]
    urgent_tasks.sort(key=attrgetter('emergency'), reverse=True)

    time_spend_today = (DBSession.query(func.sum(Execution.length))
                        .join('task').filter(Task.page==context)
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

    last_executions = (Execution.query()
                       .join('task').filter(Task.page==context)
                       .order_by(Execution.time.desc()).limit(5).all())
    return {
        'page': context,
        'tasks': tasks,
        'urgent_tasks': urgent_tasks,
        'last_executions': last_executions,
        'suggested_something': suggested_something,
        }


@view_config(context=Page, name='manage', renderer='page_manage.mako')
def page_manage(context, request):
    return {'page': context}


@view_config(context=Page, name='invite', request_method='POST', check_csrf=True)
def page_invite_post(context, request):
    email = request.params['email']
    if not email in context.invites:
        context.invites.append(email)
    request.flash_success('%s invited Please note that no email has been sent.'%email)
    # TODO send email
    return redirect(request,context, 'manage')


@view_config(context=Page, name='join', permission='auth')
def page_join(context, request):
    if request.user.email in context.invites:
        context.invites.remove(request.user.email)
        context.users.append(request.user)
        request.flash_success('You have been added to %s'%context.name)
        return redirect(request, context)
    else:
        request.flash_error("You aren't invited to this page")
        return redirect(request, request.root)


@view_config(context=Task, renderer='task.mako')
def task(context, request):
    return {'task': context}

@view_config(context=Task, name='execute',
             request_method='POST', check_csrf=True)
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
    return redirect(request, context)
