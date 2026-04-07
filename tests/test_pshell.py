from types import SimpleNamespace

from marker.pshell import setup


def test_setup_populates_env():
    tm = SimpleNamespace()
    tm.begin = lambda: None
    dbsession = object()
    request = SimpleNamespace(tm=tm, dbsession=dbsession)
    env = {"request": request}

    setup(env)

    assert env["tm"] is tm
    assert env["dbsession"] is dbsession
    from marker import models

    assert env["models"] is models
