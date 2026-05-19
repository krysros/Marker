import json
import logging
import re
import time
from typing import Any

from .ai_metrics import record_ai_event

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:  # pragma: no cover - exercised by tests through monkeypatching

    class ChatGoogleGenerativeAI:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def invoke(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "langchain_google_genai is required for AI features"
            )


log = logging.getLogger(__name__)

_DEFAULT_RETRIES = 2
_DEFAULT_BACKOFF_SECONDS = 1.0


def _model_candidates(model: str, fallback_model: str | None) -> list[str]:
    candidates = [model]
    if fallback_model and fallback_model != model:
        candidates.append(fallback_model)
    return candidates


def _response_to_text(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part).strip()
    return str(content)


def _usage_metadata(response: Any) -> dict[str, Any]:
    metadata = getattr(response, "response_metadata", None) or {}
    if not isinstance(metadata, dict):
        return {}
    usage = metadata.get("usage_metadata")
    return usage if isinstance(usage, dict) else {}


def invoke_text(
    prompt: str,
    model: str,
    *,
    fallback_model: str | None = None,
    retries: int = _DEFAULT_RETRIES,
    source: str = "unknown",
) -> str:
    retries = max(0, int(retries))
    last_error = None
    for model_name in _model_candidates(model, fallback_model):
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        for attempt in range(retries + 1):
            if attempt == 0:
                record_ai_event(source, "request", model=model_name)
            started = time.monotonic()
            try:
                response = llm.invoke(prompt)
                text = _response_to_text(response).strip()
                elapsed_ms = int((time.monotonic() - started) * 1000)
                usage = _usage_metadata(response)
                record_ai_event(
                    source,
                    "success",
                    model=model_name,
                    elapsed_ms=elapsed_ms,
                    prompt_chars=len(prompt),
                    response_chars=len(text),
                    usage=usage,
                )
                log.info(
                    "AI invoke success model=%s attempt=%s/%s elapsed_ms=%s prompt_chars=%s response_chars=%s usage=%s",
                    model_name,
                    attempt + 1,
                    retries + 1,
                    elapsed_ms,
                    len(prompt),
                    len(text),
                    usage,
                )
                return text
            except Exception as exc:  # pragma: no cover - external API failures
                last_error = exc
                elapsed_ms = int((time.monotonic() - started) * 1000)
                if attempt >= retries:
                    record_ai_event(
                        source,
                        "error",
                        model=model_name,
                        elapsed_ms=elapsed_ms,
                        error=exc,
                    )
                    log.warning(
                        "AI invoke failed model=%s attempt=%s/%s elapsed_ms=%s error=%s",
                        model_name,
                        attempt + 1,
                        retries + 1,
                        elapsed_ms,
                        exc,
                    )
                    break
                delay = _DEFAULT_BACKOFF_SECONDS * (2**attempt)
                record_ai_event(source, "retry", model=model_name)
                log.warning(
                    "AI invoke retry model=%s attempt=%s/%s elapsed_ms=%s backoff_s=%.2f error=%s",
                    model_name,
                    attempt + 1,
                    retries + 1,
                    elapsed_ms,
                    delay,
                    exc,
                )
                time.sleep(delay)

    if last_error is not None:
        log.error(
            "AI invoke exhausted models=%s retries=%s error=%s",
            _model_candidates(model, fallback_model),
            retries,
            last_error,
        )
        raise last_error
    raise RuntimeError("AI invocation failed before request execution")


def invoke_json(
    prompt: str,
    model: str,
    *,
    fallback_model: str | None = None,
    retries: int = _DEFAULT_RETRIES,
    source: str = "unknown",
) -> Any:
    payload = invoke_text(
        prompt,
        model,
        fallback_model=fallback_model,
        retries=retries,
        source=source,
    )
    payload = re.sub(r"^```(?:json)?\s*\n?", "", payload, flags=re.IGNORECASE)
    payload = re.sub(r"\n?```\s*$", "", payload)
    return json.loads(payload)
