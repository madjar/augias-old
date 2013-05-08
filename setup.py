import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'pyramid_persona',
    'dogpile.cache'
    ]

setup(name='augias',
      version='0.0',
      description='augias',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='augias',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = augias:main
      [console_scripts]
      augias_initialize_db = augias.scripts.initializedb:main
      augias_add_user = augias.scripts.add_user:main
      augias_db_upgrade = augias.scripts.alembic_upgrade:main
      """,
      )
