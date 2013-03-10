from demain.models import Notebook, Task, DBSession, Execution
from demain.tests import TestCase

# TODO : fill this

class NoteBookTest(TestCase):
    def test_deleting_a_notebook_deletes_the_tasks(self):
        notebook = Notebook(name='tagada', users=[])
        task = Task(notebook=notebook, name='stuff', periodicity=42)
        DBSession.add_all([notebook, task])
        DBSession.flush()

        DBSession.delete(notebook)

        self.assertEqual(Task.query().count(), 0)

class TaskTest(TestCase):
    def test_deleting_a_task_deletes_the_executions(self):
        notebook = Notebook(name='tagada', users=[])
        task = Task(notebook=notebook, name='stuff', periodicity=42)
        DBSession.add_all([notebook, task])
        DBSession.flush()
        task.execute(None, 12)
        self.assertEqual(Execution.query().count(), 1)

        DBSession.delete(task)

        self.assertEqual(Execution.query().count(), 0)
