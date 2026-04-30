from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "dashboard_market_overview.py"
SPEC = importlib.util.spec_from_file_location("dashboard_market_overview", MODULE_PATH)
dashboard_market_overview = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = dashboard_market_overview
SPEC.loader.exec_module(dashboard_market_overview)


class DashboardMarketOverviewTests(unittest.TestCase):
    def test_builds_dashboard_payload_for_market_overview(self) -> None:
        request = dashboard_market_overview.DashboardRequest(
            request_id="req-10",
            tenant_id="tenant-1",
            user_id="user-1",
            session_id="sess-1",
            locale="pt-BR",
        )
        observed_at = dt.datetime(2026, 4, 30, 12, 0, tzinfo=dt.UTC)
        response = dashboard_market_overview.build_market_overview_payload(
            request=request,
            rankings=[
                {
                    "asset_id": "bitcoin",
                    "symbol": "btc",
                    "name": "Bitcoin",
                    "market_cap_rank": 1,
                    "market_cap_usd": 1000,
                    "price_usd": 10,
                    "observed_at": observed_at,
                }
            ],
            movers=[
                {
                    "asset_id": "solana",
                    "symbol": "sol",
                    "move_direction_24h": "positive",
                    "price_change_pct_24h": 12.5,
                    "move_band_24h": "high",
                    "observed_at": observed_at,
                }
            ],
            dominance=[
                {
                    "dominance_group": "btc",
                    "dominance_pct": 52.3,
                    "market_cap_usd": 500,
                    "observed_at": observed_at,
                }
            ],
            comparisons=[
                {
                    "asset_id": "ethereum",
                    "symbol": "eth",
                    "correlation_bucket": "large_cap",
                    "price_change_pct_24h": 4.2,
                    "price_change_pct_7d": 9.8,
                    "observed_at": observed_at,
                }
            ],
        )

        self.assertEqual(response["surface_type"], "dashboard_payload")
        self.assertEqual(response["routing"]["route_id"], "dashboard.market-overview")
        self.assertEqual(response["payload"]["route_id"], "dashboard.market-overview")
        self.assertEqual(response["payload"]["hero_metrics"]["tracked_assets"], 1)
        self.assertEqual(response["payload"]["sections"]["market_rankings"][0]["asset"], "BTC")
        self.assertEqual(response["freshness"]["status"], "ready")
        self.assertEqual(response["schema_version"], "coingecko.response.v1")

    def test_emits_warning_when_dashboard_data_is_missing(self) -> None:
        request = dashboard_market_overview.DashboardRequest(
            request_id="req-11",
            tenant_id="tenant-1",
            user_id=None,
            session_id="sess-2",
            locale="pt-BR",
        )
        response = dashboard_market_overview.build_market_overview_payload(
            request=request,
            rankings=[],
            movers=[],
            dominance=[],
            comparisons=[],
        )

        self.assertIn("market_rankings_unavailable", response["warnings"])
        self.assertIn("freshness_watermark_missing", response["warnings"])
        self.assertEqual(response["freshness"]["status"], "unknown")

    def test_builds_usage_row_for_dashboard_route(self) -> None:
        request = dashboard_market_overview.DashboardRequest(
            request_id="req-12",
            tenant_id="tenant-1",
            user_id="user-2",
            session_id="sess-3",
            locale="pt-BR",
        )
        response = {
            "freshness": {"watermark": "2026-04-30T12:00:00+00:00"},
        }

        row = dashboard_market_overview.build_usage_row(
            request=request,
            response=response,
            latency_ms=95,
            cost_estimate=0.001,
        )

        self.assertEqual(row["route_selected"], "dashboard.market-overview")
        self.assertEqual(row["model_or_engine"], "dashboard-api")
        self.assertEqual(row["latency_ms"], 95)
        self.assertEqual(row["cost_estimate"], 0.001)
        self.assertEqual(row["freshness_watermark"], "2026-04-30T12:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
