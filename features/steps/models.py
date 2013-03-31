import transaction
from augias.models import DBSession, Notebook, Task

@given('I have a task named "{name}"')
def step(context, name):
    notebook = DBSession.query(Notebook).one()
    with transaction.manager:
        task = Task(name=name, periodicity=42, notebook=notebook)
        DBSession.add(task)
