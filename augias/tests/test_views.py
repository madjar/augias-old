import datetime
from unittest.mock import create_autospec
from pyramid import testing
from augias.tests import TestCase
from augias.models import Root, User, Notebook, Task, DBSession, Execution


class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.flash_success = create_autospec(lambda x: None)
        self.flash_error = create_autospec(lambda x: None)


class UserTest(TestCase):
    def test_change_username(self):
        from augias.views import change_username

        request = DummyRequest({'username': 'new_username'},
                                       user=User(email='tagada@example.com'),
                                       referer='/came-from')

        result = change_username(Root(request), request)

        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, '/came-from')
        self.assertEqual(request.user.name, 'new_username')

    def test_adding_a_name_should_rename_default_notebook(self):
        from augias.views import change_username

        user = User(email='tagada@example.com')
        notebook = Notebook(name="tagada@example.com's notebook", users=[user])

        request = DummyRequest({'username': 'Tagada'},
                               user=user,
                               referer='/came-from')

        result = change_username(Root(request), request)

        self.assertEqual(result.code, 302)
        self.assertEqual(notebook.name, "Tagada's notebook")


class HomeTest(TestCase):
    def _call_view(self, **kw):
        from augias.views import home
        request = DummyRequest(**kw)
        root = Root(request)
        return home(root, request)

    def test_create_notebook_if_user_has_none_and_no_invites(self):
        user = User(email='tagada.tsoin@example.com')
        self.assertEqual(Notebook.query().count(), 0)

        result = self._call_view(user=user)

        self.assertEqual(Notebook.query().count(), 1)
        notebook = Notebook.query().one()
        self.assertEqual(notebook.users, [user])
        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, DummyRequest().resource_url(notebook))

    def test_redirect_to_notebook_if_user_has_one_and_no_invites(self):
        user = User(email='tagada.tsoin@example.com')
        notebook = Notebook(name='some notebook', users=[user])
        DBSession.add_all([user, notebook])
        DBSession.flush()
        self.assertEqual(Notebook.query().count(), 1)

        result = self._call_view(user=user)

        self.assertEqual(Notebook.query().count(), 1)
        self.assertEqual(result.code, 302)
        self.assertEqual(result.location, DummyRequest().resource_url(notebook))

    def test_list_notebooks_if_user_has_many(self):
        user = User(email='tagada.tsoin@example.com')
        notebook1 = Notebook(name='some notebook', users=[user])
        notebook2 = Notebook(name='some other notebook', users=[user])

        result = self._call_view(user=user)

        self.assertEqual(result['notebooks'], [notebook1, notebook2])

    def test_list_if_user_has_invites_and_no_notebook(self):
        user = User(email='tagada.tsoin@example.com')
        notebook = Notebook(name='some notebook', invites=[user.email])
        DBSession.add_all([user, notebook])

        result = self._call_view(user=user)

        self.assertEqual(result['notebooks'], [])
        self.assertEqual(result['invites'], [notebook])

    def test_list_if_user_has_invites_and_one_notebook(self):
        user = User(email='tagada.tsoin@example.com')
        notebook1 = Notebook(name='some notebook', users=[user])
        notebook2 = Notebook(name='some other notebook', invites=[user.email])
        DBSession.add_all([user, notebook1, notebook2])

        result = self._call_view(user=user)

        self.assertEqual(result['notebooks'], [notebook1])
        self.assertEqual(result['invites'], [notebook2])


class NotebookTest(TestCase):
    def test_notebook(self):
        from augias.views import notebook
        n = Notebook(name='some notebook')
        task = Task(name='some task', notebook=n)
        request = DummyRequest(user=None)

        result = notebook(n, request)

        self.assertEqual(list(result['tasks'])[0].name, 'some task')

    def test_last_executions(self):
        from augias.views import notebook
        n = Notebook(name='some notebook')
        task = Task(name='some task', notebook=n, periodicity=12)
        user = User(email='tagada@example.com')
        task.execute(user, 5)
        task.execute(user, 10)
        request = DummyRequest(user=user)

        result = notebook(n, request)

        last_executions = result['last_executions']
        self.assertEqual(len(last_executions), 2)
        self.assertEqual(last_executions[0].length, 10)

    def _create_task_and_execute(self, notebook, user, length, time=None):
        t = Task(name='some task', notebook=notebook, periodicity=42)
        t.execute(user, length, time)
        return t

    def test_last_executions_from_other_notebooks_do_not_appear(self):
        from augias.views import notebook
        p1 = Notebook(name='some notebook')
        p2 = Notebook(name='another notebook')
        user = User(email='tagada@example.com')
        self._create_task_and_execute(p1, None, 10)
        request = DummyRequest(user=user)

        result = notebook(p2, request)
        self.assertEqual(len(result['last_executions']), 0)

    def test_suggestions(self):
        from augias.views import notebook
        n = Notebook(name='some notebook')
        user = User(email='tagada@example.com')
        long_ago = datetime.datetime.utcfromtimestamp(0)
        self._create_task_and_execute(n, user, 10, long_ago)
        self._create_task_and_execute(n, user, 10, long_ago)
        self._create_task_and_execute(n, user, 10, long_ago)

        request = DummyRequest(user=user)
        result = notebook(n, request)

        tasks = result['tasks']
        self.assertEqual(tasks[0].suggested, True)
        self.assertEqual(tasks[1].suggested, True)
        self.assertEqual(tasks[2].suggested, False)

    def test_suggest_even_when_someone_else_did_something(self):
        from augias.views import notebook
        n = Notebook(name='some notebook')
        user1 = User(email='tagada@example.com')
        user2 = User(email='sir_foobar@example.com')
        long_ago = datetime.datetime.utcfromtimestamp(0)
        self._create_task_and_execute(n, user1, 10, long_ago)
        self._create_task_and_execute(n, user2, 60)

        request = DummyRequest(user=user1)
        result = notebook(n, request)

        urgent = result['urgent_tasks']
        self.assertEqual(len(urgent), 1)
        self.assertEqual(urgent[0].suggested, True)

    def test_suggest_when_execution_in_other_notebook(self):
        from augias.views import notebook
        p1 = Notebook(name='some notebook')
        p2 = Notebook(name='other notebook')
        user = User(email='tagada@example.com')
        long_ago = datetime.datetime.utcfromtimestamp(0)
        self._create_task_and_execute(p1, user, 10, long_ago)
        self._create_task_and_execute(p2, user, 60)

        request = DummyRequest(user=user)
        result = notebook(p1, request)

        urgent = result['urgent_tasks']
        self.assertEqual(len(urgent), 1)
        self.assertEqual(urgent[0].suggested, True)


class InviteTest(TestCase):
    def test_add_invite(self):
        from augias.views import notebook_invite_post
        n = Notebook(name='some notebook')

        request = DummyRequest({'email': 'tagada@example.com'})
        notebook_invite_post(n, request)

        self.assertEqual(n.invites, ['tagada@example.com'])

    def test_add_invite_is_idempotent(self):
        from augias.views import notebook_invite_post
        n = Notebook(name='some notebook')

        request = DummyRequest({'email': 'tagada@example.com'})
        notebook_invite_post(n, request)
        notebook_invite_post(n, request)

        self.assertEqual(n.invites, ['tagada@example.com'])

    def test_accept_invite(self):
        from augias.views import notebook_join
        n = Notebook(name='some notebook', invites=['tagada@example.com'])
        user = User(email='tagada@example.com')

        request = DummyRequest(user=user)
        notebook_join(n, request)
        self.assertEqual(n.users, [user])
        self.assertEqual(n.invites, [])

    def test_cant_accept_not_invite(self):
        from augias.views import notebook_join
        n = Notebook(name='some notebook')
        user = User(email='tagada@example.com')

        request = DummyRequest(user=user)
        notebook_join(n, request)

        self.assertEqual(n.users, [])

class NewNotebookTest(TestCase):
    def test_new_notebook(self):
        from augias.views import new_notebook
        user = User(email='tagada@example.com')
        request = DummyRequest({'name': 'First notebook'},
                                       user=user)

        result = new_notebook(None, request)

        self.assertEqual(Notebook.query().count(), 1)
        n = Notebook.query().one()
        self.assertEqual(n.name, 'First notebook')
        self.assertEqual(n.users, [user])


class DeleteNotebookTest(TestCase):
    def test_last_user_deletes_notebook(self):
        from augias.views import notebook_delete_post
        user = User(email='tagada@example.com')
        notebook = Notebook(name='wizzz', users=[user])
        DBSession.add_all([user, notebook])
        self.assertEqual(Notebook.query().count(), 1)
        request = DummyRequest(user=user)

        result = notebook_delete_post(notebook, request)

        self.assertEqual(Notebook.query().count(), 0)

    def test_non_last_user_leaves_notebook(self):
        from augias.views import notebook_delete_post
        user1 = User(email='tagada@example.com')
        user2 = User(email='tsoin@example.com')
        notebook = Notebook(name='wizzz', users=[user1, user2])
        DBSession.add_all([user1, user2, notebook])

        request = DummyRequest(user=user1)

        result = notebook_delete_post(notebook, request)

        self.assertEqual(Notebook.query().count(), 1)
        self.assertEqual(notebook.users, [user2])

class TaskTest(TestCase):
    def _get_task(self):
        notebook = Notebook(name='some notebook')
        task = Task(name='some task', notebook=notebook, periodicity=42)
        DBSession.add_all([notebook, task])
        return task

    def test_task(self):
        from augias.views import task
        t = self._get_task()

        result = task(t, DummyRequest())

        self.assertEqual(result['task'], t)

    def test_execute(self):
        from augias.views import execute
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
        from augias.views import execute
        task = self._get_task()
        request = DummyRequest({'length': '15', 'executor': ''})

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.executor, None)
        self.assertEqual(execution.length, 15)
        request.flash_success.assert_called_once_with('Task executed')

    def test_execute_without_duration(self):
        from augias.views import execute
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
        from augias.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = DummyRequest({'length': 'this is no integer', 'executor': user.email})

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        request.flash_error.assert_called_once_with('Invalid length "this is no integer"')

    def test_execute_with_colon_duration(self):
        from augias.views import execute
        task = self._get_task()
        user = User(email='tagada@example.com')
        DBSession.add(user)
        request = DummyRequest({'length': '1:30:41', 'executor': user.email})
        request.flash_success = create_autospec(lambda x: None)

        result = execute(task, request)

        self.assertEqual(result.code, 302)
        execution = DBSession.query(Execution).one()
        self.assertEqual(execution.length, 91)


class NewTaskTest(TestCase):
    def test_new_task(self):
        from augias.views import new_task
        user = User(email='tagada@example.com')
        notebook = Notebook(users=[user], name='some notebook')
        DBSession.add_all([user, notebook])
        request = DummyRequest(dict(name='Task name',
                                    periodicity=12))

        result = new_task(notebook, request)

        self.assertEqual(result.code, 302)
        task = DBSession.query(Task).one()
        self.assertEqual(task.name, 'Task name')
        self.assertEqual(task.periodicity, 12)
        self.assertEqual(task.notebook, notebook)
        self.assertEqual(len(task.executions), 0)
        self.assertEqual(task.last_execution, None)
