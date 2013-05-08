import datetime
import markupsafe
from pyramid.decorator import reify
from pyramid.security import authenticated_userid, Allow, Authenticated, Deny, Everyone
import re
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey, DateTime, String, Table)
import sqlalchemy
from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.ext.declarative import declarative_base, declared_attr

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship, backref)
from sqlalchemy.orm.exc import NoResultFound

from augias.utils import cache

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class Base(object):
    @declared_attr
    def __tablename__(cls):
        name = cls.__name__
        return (
            name[0].lower() +
            re.sub(r'([A-Z])', lambda m:"_" + m.group(0).lower(), name[1:]) +
            's'
            )

    @classmethod
    def query(cls):
        return DBSession.query(cls)

Base = declarative_base(cls=Base)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(40), unique=True, index=True)
    name = Column(String(40))
    inscription_date = Column(DateTime, default=datetime.datetime.now)

    def __html__(self):
        return markupsafe.escape(self.name or self.email)

    def __repr__(self):
        # TODO : factor this
        return '<User "%s">'%self.email


class UserNotFound(Exception):
    """TODO : delete me when the site is opened"""

def get_user(request):
    user_email = authenticated_userid(request)
    if not user_email:
        return None
    try:
        user = DBSession.query(User).filter_by(email=user_email).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise UserNotFound(user_email)
#        user = User(email=user_email)
#        DBSession.add(user)
    return user


class Task(Base):
    EMERGENCY_THRESHOLD = 0.8

    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    notebook_id = Column(Integer, ForeignKey('notebooks.id'), nullable=False)
    notebook = relationship('Notebook', backref=backref('tasks', cascade='all, delete-orphan'))

    periodicity = Column(Integer, nullable=False) # days
    last_execution = Column(DateTime)

    suggested = False

    def __repr__(self):
        return '<Task "%s">'%self.name

    def __html__(self):
        return markupsafe.escape(self.name)

    @property
    def __parent__(self):
        return self.notebook

    @property
    def __name__(self):
        return self.id

    def execute(self, user, length, time=None):
        if not time:
            time = datetime.datetime.now()
        execution = Execution(task=self, executor=user, time=time, length=length)
        DBSession.add(execution)
        self.last_execution = time
        task_mean_execution.invalidate(self.id)

    @reify
    def emergency(self):
        if not self.last_execution:
            return Task.EMERGENCY_THRESHOLD
        days_since = (datetime.datetime.now() - self.last_execution).days
        return days_since / self.periodicity

    def emergency_class(self):
        if not self.last_execution:
            return 'never-done'

        ratio = self.emergency
        if ratio >= 1:
            return 'overdue'
        elif ratio >= 0.8:
            return 'urgent'
        elif ratio <= 0.1:
            return 'just-done'
        else:
            return ''

    @property
    def mean_execution(self):
        """This is the mean execution time over the 10 last executions"""
        return task_mean_execution(self.id)


@cache.cache_on_arguments()
def task_mean_execution(task_id):
    executions = (Execution.query()
                  .filter_by(task_id=task_id).filter(Execution.length != None)
                  .order_by(Execution.time.desc())[:10])
    if not executions:
        return 0
    return sum(e.length for e in executions) / len(executions)



class Execution(Base):
    __tablename__ = 'executions'
    id = Column(Integer, primary_key=True)
    executor_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    executor = relationship('User', backref='executions')  # empty means collective work
    task = relationship('Task', backref=backref('executions', cascade='all, delete-orphan'))
    # TODO : http://docs.sqlalchemy.org/en/rel_0_8/orm/collections.html#passive-deletes
    # Once in postgres, this optimization should be enabled
    time = Column(DateTime, nullable=False)
    length = Column(Integer)  # empty means no data


notebooks_authorizations = Table('notebooks_authorizations', Base.metadata,
    Column('notebook_id', Integer, ForeignKey('notebooks.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
)

class Notebook(Base):
    """A notebook is a set of tasks that can be handled by one or many users"""
    __tablename__ = 'notebooks'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    users = relationship(User, secondary=notebooks_authorizations, backref='notebooks')
    inv = relationship('Invite', backref='notebook', cascade='all, delete-orphan')
    invites = association_proxy('inv', 'email')

    def __repr__(self):
        return '<Notebook "%s">'%self.name

    def __html__(self):
        return markupsafe.escape(self.name)

    @property
    def __parent__(self):
        return Root(None)

    @property
    def __name__(self):
        return self.id

    def __getitem__(self, item):
        try:
            id = int(item)
            task = DBSession.query(Task).filter_by(notebook=self, id=id).one()
        except (NoResultFound, ValueError): # pragma: nocover
            raise KeyError(item)
        return task

    def __iter__(self):
        for task in self.tasks:
            yield task

    @property
    def __acl__(self):
        return [(Allow, user.email, 'access') for user in self.users] + [(Deny, Everyone, 'access')]


class Invite(Base):
    __tablename__ = 'invites'
    notebook_id = Column(Integer, ForeignKey('notebooks.id'), primary_key=True)
    email = Column(String(40), primary_key=True)
    date = Column(DateTime, default=datetime.datetime.now)
    by_id = Column(Integer, ForeignKey('users.id'))
    by = relationship(User)

    def __init__(self, email, by=None):
        self.email = email
        self.by = by

    def __repr__(self):
        return '<Invite "%s" to notebook %s >'%(self.email, self.notebook.name)


class Root:
    __root__ = __name__ = None
    # TODO : review this when adding a welcome notebook
    __acl__ = [
        (Allow, Authenticated, 'access'),
        (Allow, Authenticated, 'auth'),
        ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        try:
            id = int(item)
        except ValueError: #pragma: nocover
            raise KeyError(item)
        notebook = Notebook.query().get(id)
        if not notebook: #pragma: nocover
            raise KeyError(item)
        return notebook

    def notebooks(self):
        return self.request.user.notebooks
