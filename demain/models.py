import datetime
from pyramid.security import authenticated_userid
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey, DateTime)
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

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
    name = Column(Text)
    length = Column(Integer) # minutes TODO useless column, remove at some point
    periodicity = Column(Integer) # days
    last_execution = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Task "%s">'%self.name

    def execute(self, user, length):
        now = datetime.datetime.now()
        execution = Execution(task=self, executor=user, time=now, length=length)
        DBSession.add(execution)
        self.last_execution = now

    def emergency(self):
        days_since = (datetime.datetime.now() - self.last_execution).days
        ratio = days_since / self.periodicity
        if ratio >= 1:
            return 'error'
        elif ratio >= 0.8:
            return 'warning'
        elif ratio <= 0.1:
            return 'success'
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