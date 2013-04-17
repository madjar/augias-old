import transaction
from augias.models import DBSession, Notebook, Task

@given('a notebook named "{name}"')
def step(context, name):
    with transaction.manager:
        notebook = Notebook(name=name)
        DBSession.add(notebook)
    context.last['notebook'] = notebook

@given("the user's email is invited to the notebook")
def step(context):
    with transaction.manager:
        notebook = context.last['notebook']
        notebook.invites.append(context.last['user'].email)

@given('I have a task named "{name}"')
def step(context, name):
    notebook = DBSession.query(Notebook).one()
    with transaction.manager:
        task = Task(name=name, periodicity=42, notebook=notebook)
        DBSession.add(task)
    context.last['task'] = task
