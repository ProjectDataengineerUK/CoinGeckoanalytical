from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/feature_engineering_job.py"
SPEC = importlib.util.spec_from_file_location("feature_engineering_job", MODULE_PATH)
feature_engineering_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = feature_engineering_job
SPEC.loader.exec_module(feature_engineering_job)


class ComputeVolToCapRatioTests(unittest.TestCase):
    def test_computes_ratio_correctly(self) -> None:
        result = feature_engineering_job.compute_vol_to_cap_ratio(500.0, 1000.0)
        self.assertAlmostEqual(result, 0.5)

    def test_returns_none_when_cap_is_zero(self) -> None:
        result = feature_engineering_job.compute_vol_to_cap_ratio(100.0, 0.0)
        self.assertIsNone(result)

    def test_returns_none_when_cap_is_none(self) -> None:
        result = feature_engineering_job.compute_vol_to_cap_ratio(100.0, None)
        self.assertIsNone(result)

    def test_returns_none_when_vol_is_none(self) -> None:
        result = feature_engineering_job.compute_vol_to_cap_ratio(None, 1000.0)
        self.assertIsNone(result)

    def test_returns_none_when_both_none(self) -> None:
        result = feature_engineering_job.compute_vol_to_cap_ratio(None, None)
        self.assertIsNone(result)


class ComputeMomentumScoreTests(unittest.TestCase):
    def test_computes_score_with_known_values(self) -> None:
        result = feature_engineering_job.compute_momentum_score(10.0, 5.0)
        expected = 0.4 * 10.0 + 0.6 * 5.0
        self.assertAlmostEqual(result, expected)

    def test_negative_values_produce_negative_score(self) -> None:
        result = feature_engineering_job.compute_momentum_score(-4.0, -10.0)
        expected = 0.4 * (-4.0) + 0.6 * (-10.0)
        self.assertAlmostEqual(result, expected)

    def test_returns_none_when_p24h_is_none(self) -> None:
        result = feature_engineering_job.compute_momentum_score(None, 5.0)
        self.assertIsNone(result)

    def test_returns_none_when_p7d_is_none(self) -> None:
        result = feature_engineering_job.compute_momentum_score(3.0, None)
        self.assertIsNone(result)


class BuildFeatureRowTests(unittest.TestCase):
    def _valid_input(self) -> dict:
        return {
            "asset_id": "bitcoin",
            "symbol": "BTC",
            "observed_at": "2026-05-01T12:00:00Z",
            "price_change_pct_24h": 2.0,
            "price_change_pct_7d": 8.0,
            "volume_24h_usd": 40000000000.0,
            "market_cap_usd": 1000000000000.0,
            "dominance_pct_btc": 52.5,
        }

    def test_fills_all_expected_keys(self) -> None:
        row = feature_engineering_job.build_feature_row(self._valid_input())
        expected_keys = {
            "asset_id", "symbol", "observed_at",
            "price_change_pct_24h", "price_change_pct_7d",
            "volume_24h_usd", "market_cap_usd",
            "vol_to_cap_ratio", "dominance_pct_btc",
            "momentum_score", "feature_date",
        }
        self.assertEqual(set(row.keys()), expected_keys)

    def test_vol_to_cap_ratio_computed(self) -> None:
        row = feature_engineering_job.build_feature_row(self._valid_input())
        self.assertAlmostEqual(row["vol_to_cap_ratio"], 0.04)

    def test_momentum_score_computed(self) -> None:
        row = feature_engineering_job.build_feature_row(self._valid_input())
        expected = 0.4 * 2.0 + 0.6 * 8.0
        self.assertAlmostEqual(row["momentum_score"], expected)

    def test_feature_date_derived_from_observed_at(self) -> None:
        row = feature_engineering_job.build_feature_row(self._valid_input())
        self.assertEqual(row["feature_date"], "2026-05-01")

    def test_vol_to_cap_ratio_none_when_cap_zero(self) -> None:
        inp = self._valid_input()
        inp["market_cap_usd"] = 0.0
        row = feature_engineering_job.build_feature_row(inp)
        self.assertIsNone(row["vol_to_cap_ratio"])


if __name__ == "__main__":
    unittest.main()
