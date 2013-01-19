from demain.models import Page, Task, DBSession, Execution
from demain.tests import TestCase

# TODO : fill this

class PageTest(TestCase):
    def test_deleting_a_page_deletes_the_tasks(self):
        page = Page(name='tagada', users=[])
        task = Task(page=page, name='stuff', periodicity=42)
        DBSession.add_all([page, task])
        DBSession.flush()

        DBSession.delete(page)

        self.assertEqual(Task.query().count(), 0)

class TaskTest(TestCase):
    def test_deleting_a_task_deletes_the_executions(self):
        page = Page(name='tagada', users=[])
        task = Task(page=page, name='stuff', periodicity=42)
        DBSession.add_all([page, task])
        DBSession.flush()
        task.execute(None, 12)
        self.assertEqual(Execution.query().count(), 1)

        DBSession.delete(task)

        self.assertEqual(Execution.query().count(), 0)
