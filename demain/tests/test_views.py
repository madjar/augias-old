import unittest
from unittest.mock import create_autospec
from pyramid import testing
from demain.tests import TestCase
from demain.models import Root, User, Page, Task, DBSession, Execution
from demain.tests.test_functional import create_and_populate

class UserTest(TestCase):
    def test_change_username(self):
        from demain.views import change_username

        request = testing.DummyRequest({'username': 'new_username'})
        request.user = User(email='tagada@example.com')
        request.referer = '/came-from'

        result = change_username(Root(request), request)

        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, '/came-from')
        self.assertEqual(request.user.name, 'new_username')


class PageTest(TestCase):
    def test_page(self):
        from demain.views import page
        p = Page(name='some page')
        task = Task(name='some task', page=p)
        request = testing.DummyRequest()

        result = page(p, request)

        self.assertEqual(list(result['tasks'])[0].name, 'some task')


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