from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_CLIENT_PATH = Path(__file__).resolve().parent.parent / "databricks_sql_client.py"
_BFF_PATH = Path(__file__).resolve().parent.parent / "routing_bff.py"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


from typing import Any

client = _load("databricks_sql_client", _CLIENT_PATH)


class TestLoadConfigFromEnv(unittest.TestCase):
    def test_returns_config_when_all_required_present(self) -> None:
        env = {
            "DATABRICKS_HOST": "https://adb-123.azuredatabricks.net",
            "DATABRICKS_SQL_WAREHOUSE_ID": "wh-abc",
            "DATABRICKS_CLIENT_ID": "sp-id",
            "DATABRICKS_CLIENT_SECRET": "sp-secret",
        }
        config = client.load_config_from_env(env)
        self.assertIsNotNone(config)
        self.assertEqual(config.host, "https://adb-123.azuredatabricks.net")
        self.assertEqual(config.warehouse_id, "wh-abc")
        self.assertEqual(config.catalog, "cgadev")

    def test_returns_none_when_host_missing(self) -> None:
        env = {"DATABRICKS_SQL_WAREHOUSE_ID": "wh-abc"}
        self.assertIsNone(client.load_config_from_env(env))

    def test_returns_none_when_warehouse_id_missing(self) -> None:
        env = {"DATABRICKS_HOST": "https://adb-123.azuredatabricks.net"}
        self.assertIsNone(client.load_config_from_env(env))

    def test_returns_none_when_both_missing(self) -> None:
        self.assertIsNone(client.load_config_from_env({}))

    def test_strips_trailing_slash_from_host(self) -> None:
        env = {
            "DATABRICKS_HOST": "https://adb-123.azuredatabricks.net/",
            "DATABRICKS_SQL_WAREHOUSE_ID": "wh-abc",
        }
        config = client.load_config_from_env(env)
        self.assertIsNotNone(config)
        self.assertFalse(config.host.endswith("/"))

    def test_uses_custom_catalog_from_env(self) -> None:
        env = {
            "DATABRICKS_HOST": "https://adb-123.azuredatabricks.net",
            "DATABRICKS_SQL_WAREHOUSE_ID": "wh-abc",
            "COINGECKO_CATALOG": "cgaprod",
        }
        config = client.load_config_from_env(env)
        self.assertEqual(config.catalog, "cgaprod")

    def test_default_catalog_is_cgadev(self) -> None:
        env = {
            "DATABRICKS_HOST": "https://adb-123.azuredatabricks.net",
            "DATABRICKS_SQL_WAREHOUSE_ID": "wh-abc",
        }
        config = client.load_config_from_env(env)
        self.assertEqual(config.catalog, "cgadev")


class TestConvertResultRows(unittest.TestCase):
    def _make_response(
        self,
        columns: list[dict[str, str]],
        data_array: list[list[Any]],
    ) -> dict[str, Any]:
        return {
            "manifest": {"schema": {"columns": columns}},
            "result": {"data_array": data_array},
        }

    def test_converts_string_columns(self) -> None:
        resp = self._make_response(
            [{"name": "asset_id", "type_name": "STRING"}],
            [["bitcoin"], ["ethereum"]],
        )
        rows = client._rows_from_response(resp)
        self.assertEqual(rows, [{"asset_id": "bitcoin"}, {"asset_id": "ethereum"}])

    def test_converts_decimal_to_float(self) -> None:
        resp = self._make_response(
            [{"name": "price_usd", "type_name": "DECIMAL"}],
            [["95000.5"]],
        )
        rows = client._rows_from_response(resp)
        self.assertIsInstance(rows[0]["price_usd"], float)
        self.assertAlmostEqual(rows[0]["price_usd"], 95000.5)

    def test_converts_double_to_float(self) -> None:
        resp = self._make_response(
            [{"name": "dominance_pct", "type_name": "DOUBLE"}],
            [["52.8"]],
        )
        rows = client._rows_from_response(resp)
        self.assertIsInstance(rows[0]["dominance_pct"], float)

    def test_converts_bigint_to_int(self) -> None:
        resp = self._make_response(
            [{"name": "market_cap_rank", "type_name": "BIGINT"}],
            [["1"]],
        )
        rows = client._rows_from_response(resp)
        self.assertIsInstance(rows[0]["market_cap_rank"], int)
        self.assertEqual(rows[0]["market_cap_rank"], 1)

    def test_converts_int_to_int(self) -> None:
        resp = self._make_response(
            [{"name": "rank", "type_name": "INT"}],
            [["42"]],
        )
        rows = client._rows_from_response(resp)
        self.assertIsInstance(rows[0]["rank"], int)

    def test_returns_empty_list_for_empty_data_array(self) -> None:
        resp = self._make_response(
            [{"name": "asset_id", "type_name": "STRING"}],
            [],
        )
        self.assertEqual(client._rows_from_response(resp), [])

    def test_returns_empty_list_when_no_columns(self) -> None:
        resp: dict[str, Any] = {"manifest": {"schema": {"columns": []}}, "result": {"data_array": [["x"]]}}
        self.assertEqual(client._rows_from_response(resp), [])

    def test_handles_none_value(self) -> None:
        resp = self._make_response(
            [{"name": "price_usd", "type_name": "DOUBLE"}],
            [[None]],
        )
        rows = client._rows_from_response(resp)
        self.assertIsNone(rows[0]["price_usd"])

    def test_converts_multiple_columns(self) -> None:
        cols = [
            {"name": "asset_id", "type_name": "STRING"},
            {"name": "price_usd", "type_name": "FLOAT"},
            {"name": "market_cap_rank", "type_name": "INT"},
        ]
        resp = self._make_response(cols, [["bitcoin", "95000.0", "1"]])
        rows = client._rows_from_response(resp)
        self.assertEqual(rows[0]["asset_id"], "bitcoin")
        self.assertIsInstance(rows[0]["price_usd"], float)
        self.assertIsInstance(rows[0]["market_cap_rank"], int)


class TestBuildSQL(unittest.TestCase):
    def _make_config(self, catalog: str = "cgadev") -> Any:
        return client.DatabricksSQLConfig(
            host="https://host",
            warehouse_id="wh",
            client_id="cid",
            client_secret="sec",
            catalog=catalog,
            token=None,
        )

    def _captured_sql(self, fn: Any, *args: Any, **kwargs: Any) -> str:
        captured: list[str] = []

        def fake_execute(config: Any, sql: str) -> list[dict[str, Any]]:
            captured.append(sql)
            return []

        original = client.execute_statement
        client.execute_statement = fake_execute
        try:
            fn(*args, **kwargs)
        finally:
            client.execute_statement = original
        return captured[0]

    def test_fetch_market_rankings_has_quality_filter(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_market_rankings, config)
        self.assertIn("quality_status = 'pass'", sql)

    def test_fetch_market_rankings_has_limit(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_market_rankings, config, 50)
        self.assertIn("LIMIT 50", sql)

    def test_fetch_market_rankings_has_order_by(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_market_rankings, config)
        self.assertIn("ORDER BY market_cap_rank ASC", sql)

    def test_fetch_market_rankings_uses_catalog(self) -> None:
        config = self._make_config(catalog="cgaprod")
        sql = self._captured_sql(client.fetch_market_rankings, config)
        self.assertIn("cgaprod.market_gold.gold_market_rankings", sql)

    def test_fetch_top_movers_has_abs_order(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_top_movers, config)
        self.assertIn("ABS(price_change_pct_24h)", sql)

    def test_fetch_cross_asset_comparison_no_filter_when_no_ids(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_cross_asset_comparison, config, None)
        self.assertNotIn("IN (", sql)

    def test_fetch_cross_asset_comparison_generates_in_clause(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(
            client.fetch_cross_asset_comparison, config, ["bitcoin", "ethereum"]
        )
        self.assertIn("IN (", sql)
        self.assertIn("'bitcoin'", sql)
        self.assertIn("'ethereum'", sql)

    def test_fetch_cross_asset_comparison_empty_list_no_in_clause(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_cross_asset_comparison, config, [])
        self.assertNotIn("IN (", sql)

    def test_fetch_market_dominance_has_max_subquery(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_market_dominance, config)
        self.assertIn("SELECT MAX(observed_at)", sql)

    def test_fetch_market_dominance_orders_by_dominance_pct(self) -> None:
        config = self._make_config()
        sql = self._captured_sql(client.fetch_market_dominance, config)
        self.assertIn("ORDER BY dominance_pct DESC", sql)


class TestTokenCache(unittest.TestCase):
    def setUp(self) -> None:
        client._TOKEN_CACHE.clear()

    def tearDown(self) -> None:
        client._TOKEN_CACHE.clear()

    def _make_config(self) -> Any:
        return client.DatabricksSQLConfig(
            host="https://host",
            warehouse_id="wh",
            client_id="client-id",
            client_secret="secret",
            token=None,
        )

    def test_token_is_cached_on_second_call(self) -> None:
        config = self._make_config()
        call_count = 0

        def fake_urlopen(req: Any, timeout: Any = None) -> Any:
            nonlocal call_count
            call_count += 1
            mock_resp = MagicMock()
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_resp.read.return_value = b'{"access_token": "tok-1", "expires_in": 3600}'
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            t1 = client._get_bearer_token(config)
            t2 = client._get_bearer_token(config)

        self.assertEqual(t1, "tok-1")
        self.assertEqual(t2, "tok-1")
        self.assertEqual(call_count, 1)

    def test_expired_token_triggers_refresh(self) -> None:
        config = self._make_config()
        cache_key = f"{config.host}:{config.client_id}"
        client._TOKEN_CACHE[cache_key] = ("old-token", 0.0)

        call_count = 0

        def fake_urlopen(req: Any, timeout: Any = None) -> Any:
            nonlocal call_count
            call_count += 1
            mock_resp = MagicMock()
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_resp.read.return_value = b'{"access_token": "new-token", "expires_in": 3600}'
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            token = client._get_bearer_token(config)

        self.assertEqual(token, "new-token")
        self.assertEqual(call_count, 1)

    def test_valid_cached_token_not_refreshed(self) -> None:
        import time

        config = self._make_config()
        cache_key = f"{config.host}:{config.client_id}"
        client._TOKEN_CACHE[cache_key] = ("cached-token", time.monotonic() + 1000)

        with patch("urllib.request.urlopen") as mock_urlopen:
            token = client._get_bearer_token(config)
            mock_urlopen.assert_not_called()

        self.assertEqual(token, "cached-token")


class TestDemoFallback(unittest.TestCase):
    def test_build_dashboard_response_warns_when_config_none(self) -> None:
        bff = _load("routing_bff_fallback_test", _BFF_PATH)

        original_load = bff._load_dbsql_config
        bff._load_dbsql_config = lambda: None
        try:
            response = bff._build_dashboard_response(
                bff.FrontendRoutingRequest(
                    tenant_id="t1",
                    session_id="s1",
                    request_id="r1",
                    locale="pt-BR",
                    channel="web_dashboard",
                    request_type_hint="dashboard_query",
                    message_text="market overview",
                )
            )
        finally:
            bff._load_dbsql_config = original_load

        self.assertIn(bff._DEMO_MODE_WARNING, response.get("warnings", []))
        self.assertEqual(response["surface_type"], "dashboard_payload")

    def test_build_dashboard_response_warns_on_live_fetch_exception(self) -> None:
        bff = _load("routing_bff_exception_test", _BFF_PATH)

        def _raise_config() -> Any:
            raise RuntimeError("connection refused")

        original_load = bff._load_dbsql_config
        bff._load_dbsql_config = _raise_config
        try:
            response = bff._build_dashboard_response(
                bff.FrontendRoutingRequest(
                    tenant_id="t1",
                    session_id="s1",
                    request_id="r1",
                    locale="pt-BR",
                    channel="web_dashboard",
                    request_type_hint="dashboard_query",
                    message_text="market overview",
                )
            )
        finally:
            bff._load_dbsql_config = original_load

        self.assertIn(bff._DEMO_MODE_WARNING, response.get("warnings", []))

    def test_build_dashboard_response_no_warning_when_live_data_succeeds(self) -> None:
        bff = _load("routing_bff_live_test", _BFF_PATH)

        fake_datasets = {
            "rankings": [],
            "movers": [],
            "dominance": [],
            "comparisons": [],
        }

        fake_config = object()
        bff._load_dbsql_config = lambda: fake_config
        bff._fetch_live_datasets = lambda config, req: fake_datasets
        try:
            response = bff._build_dashboard_response(
                bff.FrontendRoutingRequest(
                    tenant_id="t1",
                    session_id="s1",
                    request_id="r1",
                    locale="pt-BR",
                    channel="web_dashboard",
                    request_type_hint="dashboard_query",
                    message_text="market overview",
                )
            )
        finally:
            pass

        self.assertNotIn(bff._DEMO_MODE_WARNING, response.get("warnings", []))


if __name__ == "__main__":
    unittest.main()
