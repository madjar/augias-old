import datetime
from unittest.mock import create_autospec
from pyramid import testing
from demain.tests import TestCase
from demain.models import Root, User, Page, Task, DBSession, Execution


class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.flash_success = create_autospec(lambda x: None)
        self.flash_error = create_autospec(lambda x: None)


class UserTest(TestCase):
    def test_change_username(self):
        from demain.views import change_username

        request = DummyRequest({'username': 'new_username'},
                                       user=User(email='tagada@example.com'),
                                       referer='/came-from')

        result = change_username(Root(request), request)

        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, '/came-from')
        self.assertEqual(request.user.name, 'new_username')


class HomeTest(TestCase):
    def _call_view(self, **kw):
        from demain.views import home
        request = DummyRequest(**kw)
        root = Root(request)
        return home(root, request)

    def test_create_page_if_user_has_none(self):
        user = User(email='tagada.tsoin@example.com')
        self.assertEqual(Page.query().count(), 0)

        result = self._call_view(user=user)

        self.assertEqual(Page.query().count(), 1)
        page = Page.query().one()
        self.assertEqual(page.users, [user])
        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, DummyRequest().resource_url(page))

    def test_redirect_to_page_if_user_has_one(self):
        user = User(email='tagada.tsoin@example.com')
        page = Page(name='some page', users=[user])
        DBSession.add_all([user, page])
        DBSession.flush()
        self.assertEqual(Page.query().count(), 1)

        result = self._call_view(user=user)

        self.assertEqual(Page.query().count(), 1)
        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, DummyRequest().resource_url(page))

    def test_list_pages_if_user_has_many(self):
        user = User(email='tagada.tsoin@example.com')
        page1 = Page(name='some page', users=[user])
        page2 = Page(name='some other page', users=[user])

        result = self._call_view(user=user)

        self.assertEqual(result['pages'], [page1, page2])


class PageTest(TestCase):
    def test_page(self):
        from demain.views import page
        p = Page(name='some page')
        task = Task(name='some task', page=p)
        request = DummyRequest(user=None)

        result = page(p, request)

        self.assertEqual(list(result['tasks'])[0].name, 'some task')

    def test_last_executions(self):
        from demain.views import page
        p = Page(name='some page')
        task = Task(name='some task', page=p, periodicity=12)
        user = User(email='tagada@example.com')
        task.execute(user, 5)
        task.execute(user, 10)
        request = DummyRequest(user=user)

        result = page(p, request)

        last_executions = result['last_executions']
        self.assertEqual(len(last_executions), 2)
        self.assertEqual(last_executions[0].length, 10)

    def _create_task_and_execute(self, page, user, length, time=None):
        t = Task(name='some task', page=page, periodicity=42)
        t.execute(user, length, time)
        return t

    def test_last_executions_from_other_pages_do_not_appear(self):
        from demain.views import page
        p1 = Page(name='some page')
        p2 = Page(name='another page')
        user = User(email='tagada@example.com')
        self._create_task_and_execute(p1, None, 10)
        request = DummyRequest(user=user)

        result = page(p2, request)
        self.assertEqual(len(result['last_executions']), 0)

    def test_suggestions(self):
        from demain.views import page
        p = Page(name='some page')
        user = User(email='tagada@example.com')
        long_ago = datetime.datetime.utcfromtimestamp(0)
        self._create_task_and_execute(p, user, 10, long_ago)
        self._create_task_and_execute(p, user, 10, long_ago)
        self._create_task_and_execute(p, user, 10, long_ago)

        request = DummyRequest(user=user)
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

        request = DummyRequest(user=user1)
        result = page(p, request)

        urgent = result['urgent_tasks']
        self.assertEqual(len(urgent), 1)
        self.assertEqual(urgent[0].suggested, True)

    def test_suggest_when_execution_in_other_page(self):
        from demain.views import page
        p1 = Page(name='some page')
        p2 = Page(name='other page')
        user = User(email='tagada@example.com')
        long_ago = datetime.datetime.utcfromtimestamp(0)
        self._create_task_and_execute(p1, user, 10, long_ago)
        self._create_task_and_execute(p2, user, 60)

        request = DummyRequest(user=user)
        result = page(p1, request)

        urgent = result['urgent_tasks']
        self.assertEqual(len(urgent), 1)
        self.assertEqual(urgent[0].suggested, True)


class InviteTest(TestCase):
    def test_add_invite(self):
        from demain.views import page_invite_post
        p = Page(name='some page')

        request = DummyRequest({'email': 'tagada@example.com'})
        page_invite_post(p, request)

        self.assertEqual(p.invites, ['tagada@example.com'])

    def test_add_invite_is_idempotent(self):
        from demain.views import page_invite_post
        p = Page(name='some page')

        request = DummyRequest({'email': 'tagada@example.com'})
        page_invite_post(p, request)
        page_invite_post(p, request)

        self.assertEqual(p.invites, ['tagada@example.com'])

    def test_accept_invite(self):
        from demain.views import page_join
        p = Page(name='some page', invites=['tagada@example.com'])
        user = User(email='tagada@example.com')

        request = DummyRequest(user=user)
        page_join(p, request)
        self.assertEqual(p.users, [user])
        self.assertEqual(p.invites, [])

    def test_cant_accept_not_invite(self):
        from demain.views import page_join
        p = Page(name='some page')
        user = User(email='tagada@example.com')

        request = DummyRequest(user=user)
        page_join(p, request)

        self.assertEqual(p.users, [])

class NewPageTest(TestCase):
    def test_new_page(self):
        from demain.views import new_page
        user = User(email='tagada@example.com')
        request = DummyRequest({'name': 'First page'},
                                       user=user)

        result = new_page(None, request)

        self.assertEqual(Page.query().count(), 1)
        p = Page.query().one()
        self.assertEqual(p.name, 'First page')
        self.assertEqual(p.users, [user])


class DeletePageTest(TestCase):
    def test_last_user_deletes_page(self):
        from demain.views import page_delete_post
        user = User(email='tagada@example.com')
        page = Page(name='wizzz', users=[user])
        DBSession.add_all([user, page])
        self.assertEqual(Page.query().count(), 1)
        request = DummyRequest(user=user)

        result = page_delete_post(page, request)

        self.assertEqual(Page.query().count(), 0)

    def test_non_last_user_leaves_page(self):
        from demain.views import page_delete_post
        user1 = User(email='tagada@example.com')
        user2 = User(email='tsoin@example.com')
        page = Page(name='wizzz', users=[user1, user2])
        DBSession.add_all([user1, user2, page])

        request = DummyRequest(user=user1)

        result = page_delete_post(page, request)

        self.assertEqual(Page.query().count(), 1)
        self.assertEqual(page.users, [user2])

class TaskTest(TestCase):
    def _get_task(self):
        page = Page(name='some page')
        task = Task(name='some task', page=page, periodicity=42)
        DBSession.add_all([page, task])
        return task

    def test_task(self):
        from demain.views import task
        t = self._get_task()

        result = task(t, DummyRequest())

        self.assertEqual(result['task'], t)

    def test_execute(self):
        from demain.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = DummyRequest({'length': '15', 'executor': user.email})

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.executor, user)
        self.assertEqual(execution.length, 15)
        request.flash_success.assert_called_once_with('Task executed')

    def test_execute_collective(self):
        from demain.views import execute
        task = self._get_task()
        request = DummyRequest({'length': '15', 'executor': ''})

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
        request = DummyRequest({'length': '', 'executor': user.email})

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
        request = DummyRequest({'length': 'this is no integer', 'executor': user.email})

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        request.flash_error.assert_called_once_with('Invalid length "this is no integer"')

    def test_execute_with_colon_duration(self):
        from demain.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = DummyRequest({'length': '1:30:41', 'executor': user.email})
        request.flash_success = create_autospec(lambda x: None)

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.length, 91)
