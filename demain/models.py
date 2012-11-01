import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey, DateTime)

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


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    length = Column(Integer) # minutes
    periodicity = Column(Integer) # days
    last_execution = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Task "%s">'%self.name


class Execution(Base):
    __tablename__ = 'executions'
    executor_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True)
    executor = relationship('User', backref='executions')
    task = relationship('Task', backref='executions')