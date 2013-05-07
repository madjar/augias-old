import unittest
from pyramid import testing
from testconfig import config
from dogpile.cache.api import CacheBackend, NO_VALUE
from dogpile.cache.region import register_backend
from augias.models import DBSession, Base
from augias.utils import cache


class NullCache(CacheBackend):
    get = lambda *_: NO_VALUE
    __init__ = set = delete = lambda *_: None

register_backend('null', 'augias.tests', 'NullCache')


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from sqlalchemy import create_engine

        try:
            cls.db_url = config['db']['url']
        except KeyError:
            cls.db_url = 'sqlite://'
        cls.engine = create_engine(cls.db_url)

        if not 'backend' in cache.__dict__:
            cache.configure('null')


    def setUp(self):
        self.config = testing.setUp()
        Base.metadata.create_all(self.engine)
        DBSession.configure(bind=self.engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
