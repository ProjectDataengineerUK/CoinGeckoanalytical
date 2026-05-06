from __future__ import annotations

import ast
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

_TOKEN_CACHE: dict[str, tuple[str, float]] = {}
_TOKEN_CACHE_LOCK = threading.Lock()


@dataclass(frozen=True)
class MosaicConfig:
    host: str
    endpoint_name: str
    token: str | None = None
    client_id: str = ""
    client_secret: str = ""
    timeout_seconds: int = 30
    # Per-tier endpoint overrides. Falls back to endpoint_name when empty.
    endpoint_name_light: str = ""
    endpoint_name_complex: str = ""


# Unity AI Gateway FMAPI endpoints available in every Databricks workspace by default.
_DEFAULT_ENDPOINT_STANDARD = "databricks-gpt-oss-120b"
_DEFAULT_ENDPOINT_LIGHT = "databricks-gemma-3-12b"
_DEFAULT_ENDPOINT_COMPLEX = "databricks-qwen3-next-80b-a3b-instruct"


def load_config_from_env(env: dict[str, str] | None = None) -> MosaicConfig | None:
    source = env if env is not None else os.environ
    host = source.get("DATABRICKS_HOST", "").rstrip("/")
    if host and not host.startswith("https://"):
        host = f"https://{host}"
    if not host:
        return None
    endpoint_name = source.get("DATABRICKS_MOSAIC_ENDPOINT_NAME", _DEFAULT_ENDPOINT_STANDARD)
    return MosaicConfig(
        host=host,
        endpoint_name=endpoint_name,
        token=source.get("DATABRICKS_TOKEN") or None,
        client_id=source.get("DATABRICKS_CLIENT_ID", ""),
        client_secret=source.get("DATABRICKS_CLIENT_SECRET", ""),
        endpoint_name_light=source.get("DATABRICKS_MOSAIC_ENDPOINT_LIGHT", _DEFAULT_ENDPOINT_LIGHT),
        endpoint_name_complex=source.get("DATABRICKS_MOSAIC_ENDPOINT_COMPLEX", _DEFAULT_ENDPOINT_COMPLEX),
    )


def _resolve_endpoint(config: MosaicConfig, tier: str) -> str:
    if tier == "light" and config.endpoint_name_light:
        return config.endpoint_name_light
    if tier == "complex" and config.endpoint_name_complex:
        return config.endpoint_name_complex
    return config.endpoint_name


def _extract_text_from_content(content: Any) -> str:
    if isinstance(content, str):
        stripped = content.strip()
        if stripped.startswith("[") or stripped.startswith("{"):
            for parser in (json.loads, ast.literal_eval):
                try:
                    parsed = parser(stripped)
                    extracted = _extract_text_from_content(parsed)
                    if extracted:
                        return extracted
                except Exception:
                    continue
        lower = stripped.lower()
        for marker in ("\nclaro!", "\ncom certeza!", "\nresumo rápido", "\n**resumo"):
            idx = lower.find(marker)
            if idx >= 0:
                return stripped[idx + 1 :].strip()
        if lower.startswith("the user writes") and "claro!" in lower:
            idx = lower.find("claro!")
            return stripped[idx:].strip()
        return stripped

    if isinstance(content, dict):
        if content.get("type") == "reasoning":
            return ""
        if content.get("type") == "text":
            return _extract_text_from_content(content.get("text"))
        for key in ("output_text", "text", "content"):
            extracted = _extract_text_from_content(content.get(key))
            if extracted:
                return extracted
        return ""

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            extracted = _extract_text_from_content(item)
            if extracted:
                parts.append(extracted)
        return "\n\n".join(parts).strip()

    return ""


def _extract_answer_text(data: dict[str, Any]) -> str:
    choices: list[dict[str, Any]] = data.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        extracted = _extract_text_from_content(message.get("content"))
        if extracted:
            return extracted

    extracted = _extract_text_from_content(data.get("output"))
    if extracted:
        return extracted

    extracted = _extract_text_from_content(data.get("content"))
    if extracted:
        return extracted

    return ""


def _get_bearer_token(config: MosaicConfig) -> str:
    if config.token:
        return config.token

    cache_key = f"{config.host}:{config.client_id}"
    now = time.monotonic()

    with _TOKEN_CACHE_LOCK:
        if cache_key in _TOKEN_CACHE:
            cached, expires_at = _TOKEN_CACHE[cache_key]
            if now < expires_at:
                return cached

        url = f"{config.host}/oidc/v1/token"
        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "scope": "all-apis",
            }
        ).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        with urllib.request.urlopen(req, timeout=config.timeout_seconds) as resp:
            data: dict[str, Any] = json.loads(resp.read())

        bearer = str(data["access_token"])
        ttl = int(data.get("expires_in", 3600))
        _TOKEN_CACHE[cache_key] = (bearer, now + min(ttl, 3300))
        return bearer


@dataclass(frozen=True)
class MosaicAnswer:
    answer_text: str
    model_id: str
    token_count_hint: int
    latency_ms: int
    execution_status: str


def ask_mosaic(
    config: MosaicConfig,
    question: str,
    conversation_history: list[dict[str, str]] | None = None,
    tier: str = "standard",
) -> MosaicAnswer:
    started_at = time.monotonic()
    token = _get_bearer_token(config)

    messages: list[dict[str, str]] = list(conversation_history or [])
    messages.append({"role": "user", "content": question})

    endpoint = _resolve_endpoint(config, tier)
    url = f"{config.host}/serving-endpoints/{endpoint}/invocations"
    payload = json.dumps({"messages": messages}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )

    import logging as _logging
    _log = _logging.getLogger(__name__)

    _RETRY_CODES = {429, 503, 502}
    _MAX_RETRIES = 3
    _BACKOFF_BASE = 2.0

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        if attempt > 0:
            time.sleep(_BACKOFF_BASE ** attempt)
        try:
            with urllib.request.urlopen(req, timeout=config.timeout_seconds) as resp:
                raw = resp.read()
            data: dict[str, Any] = json.loads(raw)
            last_exc = None
            break
        except urllib.error.HTTPError as exc:
            last_exc = exc
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            if exc.code in _RETRY_CODES and attempt < _MAX_RETRIES - 1:
                _log.warning("Mosaic HTTP %s for endpoint %s (attempt %d/%d) — retrying",
                             exc.code, endpoint, attempt + 1, _MAX_RETRIES)
                continue
            _log.error("Mosaic HTTP %s for endpoint %s: %s", exc.code, endpoint, body)
            latency_ms = int((time.monotonic() - started_at) * 1000)
            return MosaicAnswer(
                answer_text="", model_id="", token_count_hint=0,
                latency_ms=latency_ms, execution_status=f"http_{exc.code}",
            )
        except urllib.error.URLError as exc:
            last_exc = exc
            _log.error("Mosaic URLError for endpoint %s: %s", endpoint, exc.reason)
            latency_ms = int((time.monotonic() - started_at) * 1000)
            return MosaicAnswer(
                answer_text="", model_id="", token_count_hint=0,
                latency_ms=latency_ms, execution_status="url_error",
            )
        except json.JSONDecodeError as exc:
            last_exc = exc
            _log.error("Mosaic JSON parse error for endpoint %s (body prefix: %r): %s",
                       endpoint, raw[:120] if "raw" in dir() else b"", exc)
            latency_ms = int((time.monotonic() - started_at) * 1000)
            return MosaicAnswer(
                answer_text="", model_id="", token_count_hint=0,
                latency_ms=latency_ms, execution_status="json_parse_error",
            )

    if last_exc is not None:
        latency_ms = int((time.monotonic() - started_at) * 1000)
        return MosaicAnswer(
            answer_text="", model_id="", token_count_hint=0,
            latency_ms=latency_ms, execution_status="failed",
        )

    latency_ms = int((time.monotonic() - started_at) * 1000)

    answer_text = _extract_answer_text(data)

    model_id = str(data.get("model", ""))
    token_count_hint = int((data.get("usage") or {}).get("total_tokens", 0))

    if not answer_text:
        return MosaicAnswer(
            answer_text="",
            model_id=model_id,
            token_count_hint=token_count_hint,
            latency_ms=latency_ms,
            execution_status="no_answer",
        )

    return MosaicAnswer(
        answer_text=answer_text,
        model_id=model_id,
        token_count_hint=token_count_hint,
        latency_ms=latency_ms,
        execution_status="completed",
    )
