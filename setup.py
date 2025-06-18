import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.md")) as f:
    CHANGES = f.read()

requires = [
    "plaster_pastedeploy",
    "pyramid",
    "pyramid_mako",
    "pyramid_debugtoolbar",
    "pyramid_retry",
    "pyramid_tm",
    "SQLAlchemy >= 2.0",
    "transaction",
    "zope.sqlalchemy",
    "waitress",
    "argon2-cffi",
    "WTForms",
    "python-slugify",
    "xlsxwriter",
    "alembic",
    "zxcvbn",
    "Babel",
    "Unidecode",
    "markdown",
    "pycountry",
]

tests_require = [
    "WebTest",
    "pytest",
    "pytest-cov",
    "pylint",  # default linter used by Python ext for Visual Studio Code
    "sqlalchemy-data-model-visualizer",
]

setup(
    name="marker",
    version="2.0b5",
    description="marker",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Krystian Rosiński",
    author_email="krystian.rosinski@gmail.com",
    url="https://github.com/krysros/marker",
    keywords="web wsgi bfg pylons pyramid",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        "testing": tests_require,
    },
    install_requires=requires,
    message_extractors={
        "marker": [
            ("**.py", "python", None),
            ("templates/**.html", "mako", None),
            ("templates/**.mako", "mako", None),
            ("static/**", "ignore", None),
        ]
    },
    entry_points={
        "paste.app_factory": [
            "main = marker:main",
        ],
        "console_scripts": [
            "initialize_marker_db=marker.scripts.initialize_db:main",
        ],
    },
)
