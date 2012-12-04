import datetime
from pyramid.decorator import reify
from pyramid.security import authenticated_userid, Allow
import re
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey, DateTime, String, Table)
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base, declared_attr

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship)
from sqlalchemy.orm.exc import NoResultFound

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

    id = Column(Integer, primary_key=True)

    @classmethod
    def query(cls):
        return DBSession.query(cls)

Base = declarative_base(cls=Base)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True, index=True)
    name = Column(Text)

    def __html__(self):
        return self.name or self.email


def get_user(request):
    user_email = authenticated_userid(request)
    if not user_email:
        return None
    try:
        user = DBSession.query(User).filter_by(email=user_email).one()
    except sqlalchemy.orm.exc.NoResultFound:
        user = User(email=user_email)
        DBSession.add(user)
    return user


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(Text) # Todo this should be String, I believe
    page_id = Column(Integer, ForeignKey('pages.id'), nullable=False)
    page = relationship('Page', backref='tasks')

    periodicity = Column(Integer) # days
    last_execution = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Task "%s">'%self.name

    @property
    def __parent__(self):
        return self.page

    @property
    def __name__(self):
        return self.id

    def execute(self, user, length):
        now = datetime.datetime.now()
        execution = Execution(task=self, executor=user, time=now, length=length)
        DBSession.add(execution)
        self.last_execution = now

    @reify
    def emergency(self):
        if not self.last_execution:
            return 0
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


class Execution(Base):
    __tablename__ = 'executions'
    id = Column(Integer, primary_key=True)
    executor_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    executor = relationship('User', backref='executions')  # empty means collective work
    task = relationship('Task', backref='executions')
    time = Column(DateTime)
    length = Column(Integer)


page_authorizations = Table('page_authorizations', Base.metadata,
    Column('page_id', Integer, ForeignKey('pages.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
)

class Page(Base):
    """A page is a set of tasks that can be handled by one or many users"""
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    users = relationship(User, secondary=page_authorizations, backref='pages')

    @property
    def __parent__(self):
        return Root(None)

    @property
    def __name__(self):
        return self.id

    def __getitem__(self, item):
        try:
            task = DBSession.query(Task).filter_by(page=self, id=item).one()
        except NoResultFound: # pragma: nocover
            raise KeyError(item)
        return task

    # TODO : mettre des vrais __name__ et __parent__ partout
    def __iter__(self):
        for task in self.tasks:
            yield task

    @reify
    def __acl__(self):
        return [(Allow, user.email, 'access') for user in self.users]


class Root:
    __root__ = __name__ = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        page = Page.query().get(item)
        if not page: #pragma: nocover
            raise KeyError(item)
        return page