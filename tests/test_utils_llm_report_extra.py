import pytest
from marker.utils.llm_report import validate_sql


def test_validate_sql_invalid():
    # Should raise on non-SELECT
    with pytest.raises(ValueError):
        validate_sql("DROP TABLE foo")
    with pytest.raises(ValueError):
        validate_sql("")
    with pytest.raises(ValueError):
        validate_sql(";")


def test_validate_sql_invalid_gemini_retries(monkeypatch):
    # Coverage for ValueError with invalid GEMINI_RETRIES
    from marker.utils.llm_report import generate_report_sql

    # Patch ChatGoogleGenerativeAI to avoid real API call
    from marker.utils import langchain_ai

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            class Response:
                content = "SELECT 1"

            return Response()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
    monkeypatch.setenv("GEMINI_RETRIES", "notanint")
    # Should not raise, but will set retries_value to None
    result = generate_report_sql("SELECT 1")
    assert isinstance(result, str)


def test_get_configured_model_exceptions(monkeypatch):
    from marker.utils.llm_report import get_configured_model
    import os

    # 1. Force pyramid.threadlocal.get_current_request Exception
    def raising_get_current_request():
        raise RuntimeError("simulated error")
    monkeypatch.setattr("pyramid.threadlocal.get_current_request", raising_get_current_request)

    # 2. Force pyramid.paster.get_appsettings Exception
    def raising_get_appsettings(path):
        raise RuntimeError("simulated error")
    monkeypatch.setattr("pyramid.paster.get_appsettings", raising_get_appsettings)

    # Mock os.path.exists to return True once, to enter the try/except block where get_appsettings is called
    def mock_exists(p):
        if p == "development.ini":
            return True
        return False
    monkeypatch.setattr(os.path, "exists", mock_exists)

    # Run get_configured_model() -> should raise ValueError after catching exceptions in both blocks
    with pytest.raises(ValueError, match="Gemini model is not configured"):
        get_configured_model()

