from __future__ import annotations

import importlib.util
import json
import sys
import time
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

_GENIE_PATH = Path(__file__).resolve().parent.parent / "genie_client.py"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gc = _load("genie_client", _GENIE_PATH)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_ENV: dict[str, str] = {
    "DATABRICKS_HOST": "https://adb-123.azuredatabricks.net",
    "DATABRICKS_GENIE_SPACE_ID": "space-abc",
    "DATABRICKS_SP_CLIENT_ID": "sp-id",
    "DATABRICKS_SP_CLIENT_SECRET": "sp-secret",
    "AZURE_TENANT_ID": "tenant-xyz",
}


def _make_config(
    host: str = "https://adb-123.azuredatabricks.net",
    space_id: str = "space-abc",
    client_id: str = "sp-id",
    client_secret: str = "sp-secret",
    tenant_id: str = "tenant-xyz",
    poll_max_attempts: int = 3,
    poll_interval_seconds: float = 0.0,
) -> Any:
    return gc.GenieConfig(
        host=host,
        space_id=space_id,
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        poll_max_attempts=poll_max_attempts,
        poll_interval_seconds=poll_interval_seconds,
    )


def _fake_urlopen_factory(responses: list[bytes]) -> Any:
    """Return a fake urlopen that cycles through the given byte payloads."""
    call_index: list[int] = [0]

    def fake_urlopen(req: Any, timeout: Any = None) -> Any:
        payload = responses[call_index[0]]
        call_index[0] += 1
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = payload
        return mock_resp

    return fake_urlopen


def _token_response(token: str = "tok-1", expires_in: int = 3600) -> bytes:
    return json.dumps({"access_token": token, "expires_in": expires_in}).encode()


def _genie_start_response(
    status: str,
    conversation_id: str = "conv-1",
    message_id: str = "msg-1",
    attachments: list[dict[str, Any]] | None = None,
) -> bytes:
    payload: dict[str, Any] = {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "status": status,
    }
    if attachments is not None:
        payload["attachments"] = attachments
    return json.dumps(payload).encode()


def _genie_poll_response(
    status: str,
    attachments: list[dict[str, Any]] | None = None,
) -> bytes:
    payload: dict[str, Any] = {"status": status}
    if attachments is not None:
        payload["attachments"] = attachments
    return json.dumps(payload).encode()


def _text_attachment(content: str) -> dict[str, Any]:
    return {"text": {"content": content}}


def _query_attachment(sql: str) -> dict[str, Any]:
    return {"query": {"query": sql}}


# ---------------------------------------------------------------------------
# TestLoadConfigFromEnv
# ---------------------------------------------------------------------------


class TestLoadConfigFromEnv(unittest.TestCase):
    def test_returns_config_when_all_required_present(self) -> None:
        config = gc.load_config_from_env(_BASE_ENV)
        self.assertIsNotNone(config)
        self.assertEqual(config.host, "https://adb-123.azuredatabricks.net")
        self.assertEqual(config.space_id, "space-abc")
        self.assertEqual(config.client_id, "sp-id")
        self.assertEqual(config.client_secret, "sp-secret")
        self.assertEqual(config.tenant_id, "tenant-xyz")

    def test_returns_none_when_host_missing(self) -> None:
        env = {k: v for k, v in _BASE_ENV.items() if k != "DATABRICKS_HOST"}
        self.assertIsNone(gc.load_config_from_env(env))

    def test_returns_none_when_space_id_missing(self) -> None:
        env = {k: v for k, v in _BASE_ENV.items() if k != "DATABRICKS_GENIE_SPACE_ID"}
        self.assertIsNone(gc.load_config_from_env(env))

    def test_returns_none_when_both_host_and_space_id_missing(self) -> None:
        self.assertIsNone(gc.load_config_from_env({}))

    def test_strips_trailing_slash_from_host(self) -> None:
        env = dict(_BASE_ENV)
        env["DATABRICKS_HOST"] = "https://adb-123.azuredatabricks.net/"
        config = gc.load_config_from_env(env)
        self.assertIsNotNone(config)
        self.assertFalse(config.host.endswith("/"))

    def test_default_poll_max_attempts_is_30(self) -> None:
        config = gc.load_config_from_env(_BASE_ENV)
        self.assertIsNotNone(config)
        self.assertEqual(config.poll_max_attempts, 30)

    def test_default_poll_interval_is_2_seconds(self) -> None:
        config = gc.load_config_from_env(_BASE_ENV)
        self.assertIsNotNone(config)
        self.assertEqual(config.poll_interval_seconds, 2.0)


# ---------------------------------------------------------------------------
# TestGetOAuthToken
# ---------------------------------------------------------------------------


class TestGetOAuthToken(unittest.TestCase):
    def setUp(self) -> None:
        gc._TOKEN_CACHE.clear()

    def tearDown(self) -> None:
        gc._TOKEN_CACHE.clear()

    def test_cache_miss_makes_http_request(self) -> None:
        config = _make_config()
        fake_urlopen = _fake_urlopen_factory([_token_response("tok-miss")])

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            token = gc._get_oauth_token(config)

        self.assertEqual(token, "tok-miss")

    def test_cache_hit_does_not_make_new_request(self) -> None:
        config = _make_config()
        cache_key = f"{config.tenant_id}:{config.client_id}"
        gc._TOKEN_CACHE[cache_key] = ("cached-tok", time.monotonic() + 9999)

        with patch("urllib.request.urlopen") as mock_urlopen:
            token = gc._get_oauth_token(config)
            mock_urlopen.assert_not_called()

        self.assertEqual(token, "cached-tok")

    def test_expired_cache_entry_triggers_refresh(self) -> None:
        config = _make_config()
        cache_key = f"{config.tenant_id}:{config.client_id}"
        gc._TOKEN_CACHE[cache_key] = ("old-tok", 0.0)  # already expired

        fake_urlopen = _fake_urlopen_factory([_token_response("refreshed-tok")])

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            token = gc._get_oauth_token(config)

        self.assertEqual(token, "refreshed-tok")

    def test_second_call_returns_same_token_without_extra_request(self) -> None:
        config = _make_config()
        call_count: list[int] = [0]

        def fake_urlopen(req: Any, timeout: Any = None) -> Any:
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_resp.read.return_value = _token_response("tok-single")
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            t1 = gc._get_oauth_token(config)
            t2 = gc._get_oauth_token(config)

        self.assertEqual(t1, "tok-single")
        self.assertEqual(t2, "tok-single")
        self.assertEqual(call_count[0], 1)

    def test_ttl_capped_at_3300_when_server_returns_large_expires_in(self) -> None:
        config = _make_config()
        fake_urlopen = _fake_urlopen_factory([_token_response("tok-ttl", expires_in=9999)])

        before = time.monotonic()
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            gc._get_oauth_token(config)

        cache_key = f"{config.tenant_id}:{config.client_id}"
        _, expires_at = gc._TOKEN_CACHE[cache_key]
        # TTL must be min(9999, 3300) = 3300 seconds from now
        self.assertAlmostEqual(expires_at - before, 3300, delta=2)

    def test_ttl_uses_expires_in_when_less_than_3300(self) -> None:
        config = _make_config()
        fake_urlopen = _fake_urlopen_factory([_token_response("tok-short", expires_in=600)])

        before = time.monotonic()
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            gc._get_oauth_token(config)

        cache_key = f"{config.tenant_id}:{config.client_id}"
        _, expires_at = gc._TOKEN_CACHE[cache_key]
        self.assertAlmostEqual(expires_at - before, 600, delta=2)


# ---------------------------------------------------------------------------
# TestExtractAnswerText
# ---------------------------------------------------------------------------


class TestExtractAnswerText(unittest.TestCase):
    def test_extracts_content_from_text_attachment(self) -> None:
        attachments = [_text_attachment("Bitcoin is up 5% today.")]
        self.assertEqual(gc._extract_answer_text(attachments), "Bitcoin is up 5% today.")

    def test_returns_first_non_empty_content(self) -> None:
        attachments = [
            {"text": {"content": ""}},
            _text_attachment("Second content"),
        ]
        self.assertEqual(gc._extract_answer_text(attachments), "Second content")

    def test_returns_none_when_all_content_empty(self) -> None:
        attachments = [{"text": {"content": ""}}, {"text": {"content": ""}}]
        self.assertIsNone(gc._extract_answer_text(attachments))

    def test_returns_none_for_empty_list(self) -> None:
        self.assertIsNone(gc._extract_answer_text([]))

    def test_returns_none_when_text_key_absent(self) -> None:
        attachments = [{"query": {"query": "SELECT 1"}}]
        self.assertIsNone(gc._extract_answer_text(attachments))


# ---------------------------------------------------------------------------
# TestExtractGeneratedQuery
# ---------------------------------------------------------------------------


class TestExtractGeneratedQuery(unittest.TestCase):
    def test_extracts_sql_from_query_attachment(self) -> None:
        attachments = [_query_attachment("SELECT * FROM gold_market_rankings")]
        self.assertEqual(
            gc._extract_generated_query(attachments),
            "SELECT * FROM gold_market_rankings",
        )

    def test_returns_first_non_empty_query(self) -> None:
        attachments = [
            {"query": {"query": ""}},
            _query_attachment("SELECT 1"),
        ]
        self.assertEqual(gc._extract_generated_query(attachments), "SELECT 1")

    def test_returns_none_when_all_queries_empty(self) -> None:
        attachments = [{"query": {"query": ""}}, {"query": {"query": ""}}]
        self.assertIsNone(gc._extract_generated_query(attachments))

    def test_returns_none_for_empty_list(self) -> None:
        self.assertIsNone(gc._extract_generated_query([]))

    def test_returns_none_when_query_key_absent(self) -> None:
        attachments = [_text_attachment("some text")]
        self.assertIsNone(gc._extract_generated_query(attachments))


# ---------------------------------------------------------------------------
# TestAskGenie
# ---------------------------------------------------------------------------


class TestAskGenie(unittest.TestCase):
    def setUp(self) -> None:
        gc._TOKEN_CACHE.clear()

    def tearDown(self) -> None:
        gc._TOKEN_CACHE.clear()

    def _run_ask_genie(
        self,
        urlopen_responses: list[bytes],
        question: str = "What is the price of BTC?",
        config: Any = None,
    ) -> Any:
        """Patch urlopen and time.sleep, then call ask_genie."""
        if config is None:
            config = _make_config()

        fake_urlopen = _fake_urlopen_factory(urlopen_responses)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), patch(
            "time.sleep"
        ):
            return gc.ask_genie(config, question)

    # --- immediate terminal status ---

    def test_completed_status_on_first_call_returns_completed(self) -> None:
        attachments = [_text_attachment("BTC is at 95k USD."), _query_attachment("SELECT price FROM btc")]
        responses = [
            _token_response(),
            _genie_start_response("COMPLETED", attachments=attachments),
        ]
        answer = self._run_ask_genie(responses)

        self.assertEqual(answer.execution_status, "completed")
        self.assertEqual(answer.answer_text, "BTC is at 95k USD.")
        self.assertEqual(answer.generated_query, "SELECT price FROM btc")

    def test_failed_status_on_first_call_returns_failed(self) -> None:
        responses = [
            _token_response(),
            _genie_start_response("FAILED"),
        ]
        answer = self._run_ask_genie(responses)

        self.assertEqual(answer.execution_status, "failed")
        self.assertEqual(answer.answer_text, "")
        self.assertIsNone(answer.generated_query)

    def test_cancelled_status_returns_failed(self) -> None:
        responses = [
            _token_response(),
            _genie_start_response("CANCELLED"),
        ]
        answer = self._run_ask_genie(responses)
        self.assertEqual(answer.execution_status, "failed")

    def test_query_result_expired_returns_failed(self) -> None:
        responses = [
            _token_response(),
            _genie_start_response("QUERY_RESULT_EXPIRED"),
        ]
        answer = self._run_ask_genie(responses)
        self.assertEqual(answer.execution_status, "failed")
        self.assertEqual(answer.answer_text, "")
        self.assertIsNone(answer.generated_query)

    # --- polling path ---

    def test_pending_then_completed_polls_until_terminal(self) -> None:
        attachments = [_text_attachment("Ethereum dominance is 18%.")]
        responses = [
            _token_response(),
            _genie_start_response("PENDING"),   # start-conversation
            _genie_poll_response("PENDING"),    # poll attempt 1
            _genie_poll_response("COMPLETED", attachments=attachments),  # poll attempt 2
        ]
        answer = self._run_ask_genie(responses)

        self.assertEqual(answer.execution_status, "completed")
        self.assertEqual(answer.answer_text, "Ethereum dominance is 18%.")

    def test_polling_sleeps_between_attempts(self) -> None:
        config = _make_config(poll_interval_seconds=2.0)
        attachments = [_text_attachment("result")]
        responses = [
            _token_response(),
            _genie_start_response("PENDING"),
            _genie_poll_response("COMPLETED", attachments=attachments),
        ]
        fake_urlopen = _fake_urlopen_factory(responses)
        sleep_calls: list[float] = []

        def fake_sleep(seconds: float) -> None:
            sleep_calls.append(seconds)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), patch(
            "time.sleep", side_effect=fake_sleep
        ):
            gc.ask_genie(config, "How much?")

        self.assertTrue(all(s == 2.0 for s in sleep_calls))
        self.assertGreaterEqual(len(sleep_calls), 1)

    def test_failed_status_during_polling_returns_failed(self) -> None:
        responses = [
            _token_response(),
            _genie_start_response("PENDING"),
            _genie_poll_response("FAILED"),
        ]
        answer = self._run_ask_genie(responses)
        self.assertEqual(answer.execution_status, "failed")

    def test_query_result_expired_during_polling_returns_failed(self) -> None:
        responses = [
            _token_response(),
            _genie_start_response("PENDING"),
            _genie_poll_response("QUERY_RESULT_EXPIRED"),
        ]
        answer = self._run_ask_genie(responses)
        self.assertEqual(answer.execution_status, "failed")

    # --- no_answer path ---

    def test_completed_without_attachments_returns_no_answer(self) -> None:
        responses = [
            _token_response(),
            _genie_start_response("COMPLETED", attachments=[]),
        ]
        answer = self._run_ask_genie(responses)
        self.assertEqual(answer.execution_status, "no_answer")
        self.assertEqual(answer.answer_text, "")

    def test_completed_with_empty_text_content_returns_no_answer(self) -> None:
        responses = [
            _token_response(),
            _genie_start_response("COMPLETED", attachments=[{"text": {"content": ""}}]),
        ]
        answer = self._run_ask_genie(responses)
        self.assertEqual(answer.execution_status, "no_answer")

    def test_no_answer_still_exposes_generated_query_when_present(self) -> None:
        attachments = [_query_attachment("SELECT 1"), {"text": {"content": ""}}]
        responses = [
            _token_response(),
            _genie_start_response("COMPLETED", attachments=attachments),
        ]
        answer = self._run_ask_genie(responses)
        self.assertEqual(answer.execution_status, "no_answer")
        self.assertEqual(answer.generated_query, "SELECT 1")

    # --- latency field ---

    def test_answer_latency_ms_is_non_negative_integer(self) -> None:
        attachments = [_text_attachment("answer")]
        responses = [
            _token_response(),
            _genie_start_response("COMPLETED", attachments=attachments),
        ]
        answer = self._run_ask_genie(responses)
        self.assertIsInstance(answer.latency_ms, int)
        self.assertGreaterEqual(answer.latency_ms, 0)

    # --- GenieAnswer is a frozen dataclass ---

    def test_genie_answer_fields_are_immutable(self) -> None:
        answer = gc.GenieAnswer(
            answer_text="test",
            generated_query=None,
            execution_status="completed",
            latency_ms=42,
        )
        with self.assertRaises((AttributeError, TypeError)):
            answer.answer_text = "modified"  # type: ignore[misc]

    # --- token reuse across ask_genie call ---

    def test_cached_token_is_reused_within_ask_genie(self) -> None:
        config = _make_config()
        cache_key = f"{config.tenant_id}:{config.client_id}"
        gc._TOKEN_CACHE[cache_key] = ("pre-cached-tok", time.monotonic() + 9999)

        attachments = [_text_attachment("result")]
        # Only two urlopen calls expected: POST start-conversation, no token fetch
        responses = [
            _genie_start_response("COMPLETED", attachments=attachments),
        ]
        fake_urlopen = _fake_urlopen_factory(responses)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), patch("time.sleep"):
            answer = gc.ask_genie(config, "question")

        self.assertEqual(answer.execution_status, "completed")


if __name__ == "__main__":
    unittest.main()
