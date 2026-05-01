from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

_TOKEN_CACHE: dict[str, tuple[str, float]] = {}


@dataclass(frozen=True)
class MosaicConfig:
    host: str
    endpoint_name: str
    client_id: str
    client_secret: str
    tenant_id: str
    timeout_seconds: int = 30


def load_config_from_env(env: dict[str, str] | None = None) -> MosaicConfig | None:
    source = env if env is not None else os.environ
    host = source.get("DATABRICKS_HOST", "").rstrip("/")
    endpoint_name = source.get("DATABRICKS_MOSAIC_ENDPOINT_NAME", "")
    if not host or not endpoint_name:
        return None
    return MosaicConfig(
        host=host,
        endpoint_name=endpoint_name,
        client_id=source.get("DATABRICKS_SP_CLIENT_ID", ""),
        client_secret=source.get("DATABRICKS_SP_CLIENT_SECRET", ""),
        tenant_id=source.get("AZURE_TENANT_ID", ""),
    )


def _get_oauth_token(config: MosaicConfig) -> str:
    cache_key = f"{config.tenant_id}:{config.client_id}"
    now = time.monotonic()
    if cache_key in _TOKEN_CACHE:
        token, expires_at = _TOKEN_CACHE[cache_key]
        if now < expires_at:
            return token

    url = f"https://login.microsoftonline.com/{config.tenant_id}/oauth2/v2.0/token"
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default",
        }
    ).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=config.timeout_seconds) as resp:
        data: dict[str, Any] = json.loads(resp.read())

    token = str(data["access_token"])
    ttl = int(data.get("expires_in", 3600))
    _TOKEN_CACHE[cache_key] = (token, now + min(ttl, 3300))
    return token


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
) -> MosaicAnswer:
    started_at = time.monotonic()
    token = _get_oauth_token(config)

    messages: list[dict[str, str]] = list(conversation_history or [])
    messages.append({"role": "user", "content": question})

    url = f"{config.host}/serving-endpoints/{config.endpoint_name}/invocations"
    payload = json.dumps({"messages": messages}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=config.timeout_seconds) as resp:
            data: dict[str, Any] = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        latency_ms = int((time.monotonic() - started_at) * 1000)
        return MosaicAnswer(
            answer_text="",
            model_id="",
            token_count_hint=0,
            latency_ms=latency_ms,
            execution_status="failed",
        )
    except urllib.error.URLError as exc:
        latency_ms = int((time.monotonic() - started_at) * 1000)
        return MosaicAnswer(
            answer_text="",
            model_id="",
            token_count_hint=0,
            latency_ms=latency_ms,
            execution_status="failed",
        )

    latency_ms = int((time.monotonic() - started_at) * 1000)

    choices: list[dict[str, Any]] = data.get("choices") or []
    answer_text = ""
    if choices:
        message = choices[0].get("message") or {}
        answer_text = message.get("content") or ""

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
