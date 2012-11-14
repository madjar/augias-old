from demain.models import Task, DBSession

class TaskContainer:
    __root__ = __name__ = None
    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        task = DBSession.query(Task).get(item)
        if not task:
            raise KeyError()
        task.__name__ = item
        task.__parent__ = self
        return task

    def __iter__(self):
        for task in DBSession.query(Task):
            task.__name__ = task.id
            task.__parent__ = self
            yield task