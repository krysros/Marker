import pytest
from unittest.mock import MagicMock, patch
from marker.utils import langchain_ai


class DummyLLM:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.invoked = []

    def invoke(self, prompt):
        self.invoked.append(prompt)
        if prompt == "fail":
            raise RuntimeError("fail")
        return MagicMock(
            content=f"Echo: {prompt}",
            response_metadata={"usage_metadata": {"tokens": 42}},
        )


@patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", DummyLLM)
def test_invoke_text_success():
    result = langchain_ai.invoke_text("hello", model="test-model")
    assert result == "Echo: hello"


@patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", DummyLLM)
def test_invoke_text_fallback():
    # fallback_model is used if model fails
    # The fallback_model should only be called if the first model fails
    class FailFirstLLM(DummyLLM):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.calls = 0

        def invoke(self, prompt):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("fail")
            return MagicMock(content="ok", response_metadata={})

    with patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", FailFirstLLM):
        result = langchain_ai.invoke_text("hello", model="fail", fallback_model="ok")
        assert result == "ok"


@patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", DummyLLM)
def test_invoke_text_retries():
    # Should retry on failure
    class RetryLLM(DummyLLM):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.calls = 0

        def invoke(self, prompt):
            self.calls += 1
            if self.calls < 2:
                raise RuntimeError("fail")
            return MagicMock(content="ok", response_metadata={})

    with patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", RetryLLM):
        result = langchain_ai.invoke_text("hello", model="test", retries=1)
        assert result == "ok"


@patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", DummyLLM)
def test_response_to_text_variants():
    # string
    assert langchain_ai._response_to_text("foo") == "foo"
    # list of dicts
    resp = [{"text": "a"}, {"text": "b"}]
    assert langchain_ai._response_to_text(resp) == "a\nb"
    # list of strings
    assert langchain_ai._response_to_text(["x", "y"]) == "x\ny"
    # fallback
    assert langchain_ai._response_to_text(123) == "123"


@patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", DummyLLM)
def test_usage_metadata():
    resp = MagicMock(response_metadata={"usage_metadata": {"foo": 1}})
    assert langchain_ai._usage_metadata(resp) == {"foo": 1}


def test_invoke_text_runtimeerror():
    class DummyLLM:
        def __init__(self, *a, **k):
            pass

        def invoke(self, prompt):
            raise Exception("should not be called")

    with patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", DummyLLM):
        # Should raise the Exception from DummyLLM, since last_error is set
        with pytest.raises(Exception, match="should not be called"):
            langchain_ai.invoke_text(
                "prompt", model=None, fallback_model=None, retries=0
            )


def test_invoke_text_both_models_fail():
    class FailingLLM:
        def __init__(self, *a, **k):
            pass

        def invoke(self, prompt):
            raise RuntimeError("fail-both")

    with patch("marker.utils.langchain_ai.ChatGoogleGenerativeAI", FailingLLM):
        with pytest.raises(RuntimeError, match="fail-both"):
            langchain_ai.invoke_text(
                "prompt", model="fail1", fallback_model="fail2", retries=0
            )
    resp = MagicMock(response_metadata=None)
    assert langchain_ai._usage_metadata(resp) == {}
    resp = MagicMock(response_metadata="notadict")
    assert langchain_ai._usage_metadata(resp) == {}
