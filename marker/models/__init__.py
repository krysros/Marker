# ruff: noqa: E402,F401

import locale
import zope.sqlalchemy
from sqlalchemy import engine_from_config, event
from sqlalchemy.orm import configure_mappers, sessionmaker

# Configure Polish locale for string collation
try:
    locale.setlocale(locale.LC_COLLATE, "pl_PL")
except locale.Error:
    try:
        locale.setlocale(locale.LC_COLLATE, "Polish_Poland.1250")
    except locale.Error:
        pass


def _polish_collate(a: str, b: str) -> int:
    """Case-insensitive Polish alphabetical collation for SQLite using system locale."""
    return locale.strcoll(a.lower(), b.lower())


def _unicode_lower(s: str | None) -> str | None:
    """Unicode-aware lower() for SQLite (built-in lower() handles ASCII only)."""
    return s.lower() if s else s


# Import or define all models here to ensure they are attached to the
# ``Base.metadata`` prior to any initialization routines.
from .association import Activity  # noqa
from .association import companies_stars  # noqa
from .association import companies_tags  # noqa
from .association import projects_stars  # noqa
from .association import projects_tags  # noqa
from .association import selected_companies  # noqa
from .association import selected_contacts  # noqa
from .association import selected_projects  # noqa
from .association import selected_tags  # noqa
from .comment import Comment  # noqa
from .company import Company  # noqa
from .contact import Contact  # noqa
from .project import Project  # noqa
from .tag import Tag  # noqa
from .user import User  # noqa

# Run ``configure_mappers`` after defining all of the models to ensure
# all relationships can be setup.
configure_mappers()


def get_engine(settings, prefix="sqlalchemy."):
    engine = engine_from_config(settings, prefix)

    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            dbapi_connection.create_collation("POLISH_CI", _polish_collate)
            dbapi_connection.create_function("unicode_lower", 1, _unicode_lower)

    return engine


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager, request=None):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example:

      .. code-block:: python

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    This function may be invoked with a ``request`` kwarg, such as when invoked
    by the reified ``.dbsession`` Pyramid request attribute which is configured
    via the ``includeme`` function below. The default value, for backwards
    compatibility, is ``None``.

    The ``request`` kwarg is used to populate the ``sqlalchemy.orm.Session``'s
    "info" dict.  The "info" dict is the official namespace for developers to
    stash session-specific information.  For more information, please see the
    SQLAlchemy docs:
    https://docs.sqlalchemy.org/en/stable/orm/session_api.html#sqlalchemy.orm.session.Session.params.info

    By placing the active ``request`` in the "info" dict, developers will be
    able to access the active Pyramid request from an instance of an SQLAlchemy
    object in one of two ways:

    - Classic SQLAlchemy. This uses the ``Session``'s utility class method:

      .. code-block:: python

          from sqlalchemy.orm.session import Session as sa_Session

          dbsession = sa_Session.object_session(dbObject)
          request = dbsession.info["request"]

    - Modern SQLAlchemy. This uses the "Runtime Inspection API":

      .. code-block:: python

          from sqlalchemy import inspect as sa_inspect

          dbsession = sa_inspect(dbObject).session
          request = dbsession.info["request"]
    """
    dbsession = session_factory(info={"request": request})
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('marker.models')``.

    """
    settings = config.get_settings()
    settings["tm.manager_hook"] = "pyramid_tm.explicit_manager"

    # Use ``pyramid_tm`` to hook the transaction lifecycle to the request.
    # Note: the packages ``pyramid_tm`` and ``transaction`` work together to
    # automatically close the active database session after every request.
    # If your project migrates away from ``pyramid_tm``, you may need to use a
    # Pyramid callback function to close the database session after each
    # request.
    config.include("pyramid_tm")

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include("pyramid_retry")

    # hook to share the dbengine fixture in testing
    dbengine = settings.get("dbengine")
    if not dbengine:
        dbengine = get_engine(settings)

    session_factory = get_session_factory(dbengine)
    config.registry["dbsession_factory"] = session_factory

    # make request.dbsession available for use in Pyramid
    def dbsession(request):
        # hook to share the dbsession fixture in testing
        dbsession = request.environ.get("app.dbsession")
        if dbsession is None:
            # request.tm is the transaction manager used by pyramid_tm
            dbsession = get_tm_session(session_factory, request.tm, request=request)
        return dbsession

    config.add_request_method(dbsession, reify=True)
