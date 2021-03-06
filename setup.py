import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'plaster_pastedeploy',
    'pyramid',
    'pyramid_mako',
    'pyramid_chameleon',
    # 'pyramid_debugtoolbar',
    'pyramid_retry',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'psycopg2',
    'waitress',
    'passlib',
    'bcrypt',
    'deform @ git+https://github.com/krysros/deform@fix-seq-widgets#egg=deform',
    'python-slugify',
    'xlsxwriter',
    'alembic',
    'babel',
    'docxtpl',
    'slownie',
    'zxcvbn',
    'Unidecode',
    'pyramid_storage',
    ]

tests_require = [
    'WebTest',
    'pytest',
    'pytest-cov',
    'pylint',  # default linter used by Python ext for Visual Studio Code
    ]

setup(name='marker',
      version='1.21',
      description='marker',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Krystian Rosiński',
      author_email='krystian.rosinski@gmail.com',
      url='https://kros.xyz/',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points={
          'paste.app_factory': [
              'main = marker:main',
          ],
          'console_scripts': [
              'initialize_marker_db=marker.scripts.initialize_db:main',
          ],
      },
)