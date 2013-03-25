import unittest
from pyramid import testing
from testconfig import config
from augias.models import DBSession, Base


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from sqlalchemy import create_engine

        try:
            cls.db_url = config['db']['url']
        except KeyError:
            cls.db_url = 'sqlite://'
        cls.engine = create_engine(cls.db_url)

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
