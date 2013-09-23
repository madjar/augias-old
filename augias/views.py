import datetime
from operator import attrgetter
from markupsafe import Markup
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid.security import NO_PERMISSION_REQUIRED
from sqlalchemy import func, or_
from augias import helpers
from .utils import encode_google_datatable, raw_executions_graph, report_for_week

from .models import (
    DBSession,
    Task, Notebook, Root, User, Execution, UserNotFound, Invite)

def redirect(request, *args):
    return HTTPFound(request.resource_url(*args))

@view_config(context=Root, renderer='notebook_list.mako', permission=NO_PERMISSION_REQUIRED)
def home(context, request):
    if not request.user:
        return render_to_response('landing.mako', {}, request)

    notebooks = request.user.notebooks
    invites = Invite.query().filter_by(email=request.user.email).all()
    if not notebooks and not invites:
        notebook = Notebook(name="%s's notebook"%request.user.__html__(), users=[request.user])
        DBSession.add(notebook)
        DBSession.flush()
        return redirect(request, notebook)
    elif len(notebooks) == 1 and not invites:
        return redirect(request, notebooks[0])
    else:
        return {'notebooks': notebooks, 'invites': invites}

@view_config(context=UserNotFound, renderer='not_invited.mako', permission=NO_PERMISSION_REQUIRED)
def user_not_invited(context, request):
    return {'email': context.args[0]}

@view_config(context=Root, name='change_username', check_csrf=True, request_method='POST')
def change_username(context, request):
    request.user.name = request.params['username']
    for notebook in request.user.notebooks:
        notebook.name = notebook.name.replace(request.user.email,
                                              request.user.name)
    return HTTPFound(request.referer)


@view_config(context=Root, name='new_notebook',
             request_method='POST', check_csrf=True)
def new_notebook(context, request):
    notebook = Notebook(name=request.params['name'], users=[request.user])
    DBSession.add(notebook)
    DBSession.flush()
    return redirect(request, notebook)

@view_config(context=Notebook, name='delete',
             request_method='GET', renderer='notebook_delete.mako')
def notebook_delete(context, request):
    return {'notebook': context}


@view_config(context=Notebook, name='delete',
             request_method='POST', check_csrf=True)
def notebook_delete_post(context, request):
    if len(context.users) == 1:
        DBSession.delete(context)
    else:
        context.users.remove(request.user)
    return HTTPFound('/')


@view_config(context=Notebook, renderer='notebook.mako')
def notebook(context, request):
    tasks = Task.query().filter_by(notebook=context).order_by('name').all()
    urgent_tasks = [t for t in tasks if t.emergency >= Task.EMERGENCY_THRESHOLD]
    urgent_tasks.sort(key=attrgetter('emergency'), reverse=True)

    time_spend_today = (DBSession.query(func.sum(Execution.length))
                        .join('task').filter(Task.notebook==context)
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
                       .join('task').filter(Task.notebook==context)
                       .order_by(Execution.time.desc()).limit(5).all())
    return {
        'notebook': context,
        'tasks': tasks,
        'urgent_tasks': urgent_tasks,
        'urgent_tasks_time': int(sum(t.mean_execution for t in urgent_tasks)),
        'last_executions': last_executions,
        'suggested_something': suggested_something,
        }


@view_config(context=Notebook, name='manage', renderer='notebook_manage.mako')
def notebook_manage(context, request):
    return {'notebook': context}


@view_config(context=Notebook, name='invite', request_method='POST', check_csrf=True)
def notebook_invite_post(context, request):
    email = request.params['email']
    if not email in context.invites:
        context.inv.append(Invite(email, request.user))
    request.flash_success('%s invited Please note that no email has been sent.'%email)
    # TODO send email
    return redirect(request,context, 'manage')


@view_config(context=Notebook, name='join', request_method='POST',
             check_csrf=True, permission='auth')
def notebook_answer_invite(context, request):
    if not request.user.email in context.invites:
        request.flash_error("You aren't invited to this notebook")
        return redirect(request, request.root)

    if 'accept' in request.params:
        context.invites.remove(request.user.email)
        context.users.append(request.user)
        request.flash_success('You have been added to %s'%context.name)
        return redirect(request, context)
    elif 'decline' in request.params:
        context.invites.remove(request.user.email)
        request.flash_success('Invite to %s declined'%context.name)
    return redirect(request, request.root)

@view_config(context=Notebook, name='report', renderer='notebook_report.mako')
def notebook_report(context, request):
    weeks_ago = int(request.params.get('ago', 1))
    d = report_for_week(context, -weeks_ago)
    d['notebook'] = context
    d['ago'] = weeks_ago
    return d


@view_config(context=Task, renderer='task.mako')
def task(context, request):
    return {'task': context, 'data': raw_executions_graph(context)}

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
        exec = context.execute(executor, length)
        message = """<form style="display:inline" method="POST" action="{}">
            Task "{}" executed
            <input type="hidden" name="id" value="{}"/>
            {}
            <button class="btn btn-sm btn-warning" type="submit">Cancel</button>
        </form>""".format(request.resource_path(context, 'cancel'),
                          context.name,
                          exec.id,
                          helpers.csrf_token(request))
        request.flash_success(Markup(message))
    return redirect(request, context.notebook)


@view_config(context=Task, name='cancel',
             request_method='POST', check_csrf=True)
def cancel_exec(context, request):
    exec_id = int(request.params['id'])
    exec = Execution.query().get(exec_id)
    if not exec or exec.task != context:
        return HTTPBadRequest('Invalid execution')

    exec.cancel()
    request.flash_success('Task canceled')
    return redirect(request, context)


@view_config(context=Notebook, name='new_task',
             request_method='POST', check_csrf=True)
def new_task(context, request):
    task = Task(notebook=context,
                name=request.params['name'],
                periodicity=int(request.params['periodicity']))
    DBSession.add(task)
    return redirect(request, context)
