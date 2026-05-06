from __future__ import annotations

import ast
import json
import logging
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)

_TOKEN_CACHE: dict[str, tuple[str, float]] = {}
_TOKEN_CACHE_LOCK = threading.Lock()

_TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"}


@dataclass(frozen=True)
class GenieConfig:
    host: str
    space_id: str
    token: str | None = None
    client_id: str = ""
    client_secret: str = ""
    poll_max_attempts: int = 30
    poll_interval_seconds: float = 2.0


def load_config_from_env(env: dict[str, str] | None = None) -> GenieConfig | None:
    source = env if env is not None else os.environ
    host = source.get("DATABRICKS_HOST", "").rstrip("/")
    if host and not host.startswith("https://"):
        host = f"https://{host}"
    space_id = source.get("DATABRICKS_GENIE_SPACE_ID", "")
    if not host or not space_id:
        return None
    return GenieConfig(
        host=host,
        space_id=space_id,
        token=source.get("DATABRICKS_TOKEN") or None,
        client_id=source.get("DATABRICKS_CLIENT_ID", ""),
        client_secret=source.get("DATABRICKS_CLIENT_SECRET", ""),
    )


def _get_bearer_token(config: GenieConfig) -> str:
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
        with urllib.request.urlopen(req, timeout=30) as resp:
            data: dict[str, Any] = json.loads(resp.read())

        bearer = str(data["access_token"])
        ttl = int(data.get("expires_in", 3600))
        _TOKEN_CACHE[cache_key] = (bearer, now + min(ttl, 3300))
        return bearer


def _raise_for_http(exc: urllib.error.HTTPError, url: str) -> None:
    try:
        body = exc.read().decode("utf-8", errors="replace")
    except Exception:
        body = "<unreadable>"
    _log.error("Genie HTTP %s %s — %s", exc.code, url, body)
    raise urllib.error.HTTPError(exc.url, exc.code, f"HTTP {exc.code}: {body}", exc.headers, None) from exc


def _post_json(url: str, body: dict[str, Any], token: str, timeout: int = 30) -> dict[str, Any]:
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        _raise_for_http(exc, url)
        raise  # unreachable but satisfies type checker


def _get_json(url: str, token: str, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        _raise_for_http(exc, url)
        raise  # unreachable


def _extract_answer_text(attachments: list[dict[str, Any]]) -> str | None:
    for attachment in attachments:
        for path in (
            ("text", "content"),
            ("text", "value"),
            ("message", "content"),
            ("response", "text"),
        ):
            content: Any = attachment
            for key in path:
                if not isinstance(content, dict):
                    content = None
                    break
                content = content.get(key)
            extracted = _normalize_text_content(content)
            if extracted:
                return extracted
    return None


def _extract_generated_query(attachments: list[dict[str, Any]]) -> str | None:
    for attachment in attachments:
        for path in (
            ("query", "query"),
            ("query", "content"),
            ("statement", "query"),
            ("sql",),
        ):
            sql: Any = attachment
            for key in path:
                if not isinstance(sql, dict):
                    sql = None
                    break
                sql = sql.get(key)
            normalized = _normalize_text_content(sql)
            if normalized:
                return normalized
    return None


def _normalize_text_content(content: Any) -> str | None:
    if isinstance(content, str):
        stripped = content.strip()
        if not stripped:
            return None
        if stripped.startswith("[") or stripped.startswith("{"):
            for parser in (json.loads, ast.literal_eval):
                try:
                    parsed = parser(stripped)
                    extracted = _normalize_text_content(parsed)
                    if extracted:
                        return extracted
                except Exception:
                    continue
        return stripped
    if isinstance(content, dict):
        for key in ("text", "content", "value"):
            extracted = _normalize_text_content(content.get(key))
            if extracted:
                return extracted
        return None
    if isinstance(content, list):
        parts = [part for item in content if (part := _normalize_text_content(item))]
        return "\n\n".join(parts).strip() or None
    return None


@dataclass(frozen=True)
class GenieAnswer:
    answer_text: str
    generated_query: str | None
    execution_status: str
    latency_ms: int


def ask_genie(config: GenieConfig, question: str) -> GenieAnswer:
    started_at = time.monotonic()
    token = _get_bearer_token(config)

    start_url = f"{config.host}/api/2.0/genie/spaces/{config.space_id}/start-conversation"
    result = _post_json(start_url, {"content": question}, token)

    conversation_id = result.get("conversation_id", "")
    message_id = result.get("message_id", "")
    status = result.get("status", "")
    attachments: list[dict[str, Any]] = result.get("attachments") or []

    if status not in _TERMINAL_STATUSES:
        poll_url = (
            f"{config.host}/api/2.0/genie/spaces/{config.space_id}"
            f"/conversations/{conversation_id}/messages/{message_id}"
        )
        for _ in range(config.poll_max_attempts):
            time.sleep(config.poll_interval_seconds)
            poll_result = _get_json(poll_url, token)
            status = poll_result.get("status", "")
            attachments = poll_result.get("attachments") or []
            if status in _TERMINAL_STATUSES:
                break

    latency_ms = int((time.monotonic() - started_at) * 1000)

    if status in {"FAILED", "CANCELLED"}:
        return GenieAnswer(
            answer_text="",
            generated_query=None,
            execution_status="failed",
            latency_ms=latency_ms,
        )

    if status == "QUERY_RESULT_EXPIRED":
        return GenieAnswer(
            answer_text="",
            generated_query=None,
            execution_status="query_result_expired",
            latency_ms=latency_ms,
        )

    answer_text = _extract_answer_text(attachments)
    generated_query = _extract_generated_query(attachments)

    if not answer_text:
        return GenieAnswer(
            answer_text="",
            generated_query=generated_query,
            execution_status="no_answer",
            latency_ms=latency_ms,
        )

    return GenieAnswer(
        answer_text=answer_text,
        generated_query=generated_query,
        execution_status="completed",
        latency_ms=latency_ms,
    )
