from unittest.mock import MagicMock, patch

import pytest

from marker.scripts.initialize_db import main, parse_args, setup_models


def test_parse_args():
    args = parse_args(["prog", "development.ini"])
    assert args.config_uri == "development.ini"


def test_parse_args_missing():
    with pytest.raises(SystemExit):
        parse_args(["prog"])


def test_setup_models():
    dbsession = MagicMock()
    setup_models(dbsession)
    dbsession.add.assert_called_once()
    model = dbsession.add.call_args[0][0]
    assert model.name == "admin"
    assert model.role == "admin"
    assert model.email == "admin@example.com"


@patch("marker.scripts.initialize_db.bootstrap")
@patch("marker.scripts.initialize_db.setup_logging")
def test_main_success(mock_logging, mock_bootstrap):
    mock_tm = MagicMock()
    mock_dbsession = MagicMock()
    mock_request = MagicMock()
    mock_request.tm = mock_tm
    mock_request.dbsession = mock_dbsession
    mock_tm.__enter__ = MagicMock(return_value=mock_tm)
    mock_tm.__exit__ = MagicMock(return_value=False)
    mock_bootstrap.return_value = {"request": mock_request}

    main(["prog", "testing.ini"])

    mock_logging.assert_called_once_with("testing.ini")
    mock_bootstrap.assert_called_once_with("testing.ini")


@patch("marker.scripts.initialize_db.bootstrap")
@patch("marker.scripts.initialize_db.setup_logging")
def test_main_operational_error(mock_logging, mock_bootstrap, capsys):
    from sqlalchemy.exc import OperationalError

    mock_request = MagicMock()
    mock_request.tm.__enter__ = MagicMock(
        side_effect=OperationalError("stmt", {}, Exception("db error"))
    )
    mock_request.tm.__exit__ = MagicMock(return_value=False)
    mock_bootstrap.return_value = {"request": mock_request}

    main(["prog", "testing.ini"])

    captured = capsys.readouterr()
    assert "SQL database" in captured.out
