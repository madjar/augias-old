import datetime
from unittest.mock import create_autospec
from pyramid import testing
from demain.tests import TestCase
from demain.models import Root, User, Page, Task, DBSession, Execution

class UserTest(TestCase):
    def test_change_username(self):
        from demain.views import change_username

        request = testing.DummyRequest({'username': 'new_username'},
                                       user=User(email='tagada@example.com'),
                                       referer='/came-from')

        result = change_username(Root(request), request)

        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, '/came-from')
        self.assertEqual(request.user.name, 'new_username')


class PageTest(TestCase):
    def test_page(self):
        from demain.views import page
        p = Page(name='some page')
        task = Task(name='some task', page=p)
        request = testing.DummyRequest(user=None)

        result = page(p, request)

        self.assertEqual(list(result['tasks'])[0].name, 'some task')

    def test_last_executions(self):
        from demain.views import page
        p = Page(name='some page')
        task = Task(name='some task', page=p, periodicity=12)
        user = User(email='tagada@example.com')
        task.execute(user, 5)
        task.execute(user, 10)
        request = testing.DummyRequest(user=user)

        result = page(p, request)

        last_executions = result['last_executions']
        self.assertEqual(len(last_executions), 2)
        self.assertEqual(last_executions[0].length, 10)

    def _create_task_and_execute(self, page, user, length, time=None):
        t = Task(name='some task', page=page, periodicity=42)
        t.execute(user, length, time)
        return t

    def test_suggestions(self):
        from demain.views import page
        p = Page(name='some page')
        user = User(email='tagada@example.com')
        long_ago = datetime.datetime.utcfromtimestamp(0)
        self._create_task_and_execute(p, user, 10, long_ago)
        self._create_task_and_execute(p, user, 10, long_ago)
        self._create_task_and_execute(p, user, 10, long_ago)

        request = testing.DummyRequest(user=user)
        result = page(p, request)

        tasks = result['tasks']
        self.assertEqual(tasks[0].suggested, True)
        self.assertEqual(tasks[1].suggested, True)
        self.assertEqual(tasks[2].suggested, False)

    def test_suggest_even_when_someone_else_did_something(self):
        from demain.views import page
        p = Page(name='some page')
        user1 = User(email='tagada@example.com')
        user2 = User(email='sir_foobar@example.com')
        long_ago = datetime.datetime.utcfromtimestamp(0)
        self._create_task_and_execute(p, user1, 10, long_ago)
        self._create_task_and_execute(p, user2, 60)

        request = testing.DummyRequest(user=user1)
        result = page(p, request)

        urgent = result['urgent_tasks']
        self.assertEqual(len(urgent), 1)
        self.assertEqual(urgent[0].suggested, True)


class TaskTest(TestCase):
    def _get_task(self):
        page = Page(name='some page')
        task = Task(name='some task', page=page)
        DBSession.add_all([page, task])
        return task

    def test_task(self):
        from demain.views import task
        t = self._get_task()

        result = task(t, testing.DummyRequest())

        self.assertEqual(result['task'], t)

    def test_execute(self):
        from demain.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = testing.DummyRequest({'length': '15', 'executor': user.email})
        request.flash_success = create_autospec(lambda x: None)

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.executor, user)
        self.assertEqual(execution.length, 15)
        request.flash_success.assert_called_once_with('Task executed')

    def test_execute_collective(self):
        from demain.views import execute
        task = self._get_task()
        request = testing.DummyRequest({'length': '15', 'executor': ''})
        request.flash_success = create_autospec(lambda x: None)

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.executor, None)
        self.assertEqual(execution.length, 15)
        request.flash_success.assert_called_once_with('Task executed')

    def test_execute_without_duration(self):
        from demain.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = testing.DummyRequest({'length': '', 'executor': user.email})
        request.flash_success = create_autospec(lambda x: None)

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.executor, user)
        self.assertEqual(execution.length, None)
        request.flash_success.assert_called_once_with('Task executed')

    def test_execute_invalid_duration(self):
        from demain.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = testing.DummyRequest({'length': 'this is no integer', 'executor': user.email})
        request.flash_error = create_autospec(lambda x: None)

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        request.flash_error.assert_called_once_with('Invalid length "this is no integer"')

    def test_execute_with_colon_duration(self):
        from demain.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = testing.DummyRequest({'length': '1:30:41', 'executor': user.email})
        request.flash_success = create_autospec(lambda x: None)

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.length, 91)
