from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "apps"
    / "cga-analytics"
    / "services"
    / "sql_service.py"
)


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sql_service = _load("cga_analytics_sql_service", MODULE_PATH)


class SqlServiceTests(unittest.TestCase):
    def test_fetch_market_rankings_avoids_unresolved_change_column(self) -> None:
        captured: list[str] = []

        def fake_run_query(sql: str) -> list[dict[str, Any]]:
            captured.append(sql)
            return []

        original = sql_service.run_query
        sql_service.run_query = fake_run_query
        try:
            sql_service.fetch_market_rankings(12)
        finally:
            sql_service.run_query = original

        self.assertIn("CAST(NULL AS DOUBLE) AS price_change_pct_24h", captured[0])
        self.assertIn("FROM `cgadev`.`ai_serving`.`mv_market_rankings`", captured[0])

    def test_fetch_top_movers_falls_back_to_cross_asset_compare(self) -> None:
        captured: list[str] = []

        def fake_run_query(sql: str) -> list[dict[str, Any]]:
            captured.append(sql)
            return [] if len(captured) == 1 else [{"asset_id": "bitcoin"}]

        original = sql_service.run_query
        sql_service.run_query = fake_run_query
        try:
            rows = sql_service.fetch_top_movers(10)
        finally:
            sql_service.run_query = original

        self.assertEqual(rows, [{"asset_id": "bitcoin"}])
        self.assertIn("FROM `cgadev`.`ai_serving`.`mv_top_movers`", captured[0])
        self.assertIn("FROM `cgadev`.`ai_serving`.`mv_cross_asset_compare`", captured[1])

    def test_fetch_defi_protocols_uses_live_ai_serving_view(self) -> None:
        captured: list[str] = []

        def fake_run_query(sql: str) -> list[dict[str, Any]]:
            captured.append(sql)
            return []

        original = sql_service.run_query
        sql_service.run_query = fake_run_query
        try:
            sql_service.fetch_defi_protocols(10)
        finally:
            sql_service.run_query = original

        self.assertIn("name AS protocol_name", captured[0])
        self.assertIn("FROM `cgadev`.`ai_serving`.`mv_defi_protocols`", captured[0])

    def test_fetch_macro_regime_uses_live_ai_serving_view(self) -> None:
        captured: list[str] = []

        def fake_run_query(sql: str) -> list[dict[str, Any]]:
            captured.append(sql)
            return []

        original = sql_service.run_query
        sql_service.run_query = fake_run_query
        try:
            sql_service.fetch_macro_regime(8)
        finally:
            sql_service.run_query = original

        self.assertIn("latest_date AS observation_date", captured[0])
        self.assertIn("current_value AS value", captured[0])
        self.assertIn("FROM `cgadev`.`ai_serving`.`mv_macro_regime`", captured[0])


if __name__ == "__main__":
    unittest.main()
