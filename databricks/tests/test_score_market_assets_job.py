from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/score_market_assets_job.py"
SPEC = importlib.util.spec_from_file_location("score_market_assets_job", MODULE_PATH)
score_market_assets_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = score_market_assets_job
SPEC.loader.exec_module(score_market_assets_job)


class BuildScoreRowTests(unittest.TestCase):
    def test_returns_expected_dict_with_all_keys(self) -> None:
        row = score_market_assets_job.build_score_row(
            asset_id="bitcoin",
            symbol="BTC",
            regime="bull",
            anomaly_score=1,
            momentum=4.8,
            regime_confidence=0.92,
            model_version="champion/champion",
            scored_at="2026-05-01T00:00:00+00:00",
        )
        expected_keys = {
            "asset_id", "symbol", "scored_at",
            "predicted_regime", "anomaly_score",
            "momentum_score", "regime_confidence", "model_version",
        }
        self.assertEqual(set(row.keys()), expected_keys)

    def test_field_values_match_inputs(self) -> None:
        row = score_market_assets_job.build_score_row(
            asset_id="ethereum",
            symbol="ETH",
            regime="bear",
            anomaly_score=-1,
            momentum=-2.3,
            regime_confidence=0.78,
            model_version="v1/v1",
            scored_at="2026-05-01T06:00:00+00:00",
        )
        self.assertEqual(row["asset_id"], "ethereum")
        self.assertEqual(row["symbol"], "ETH")
        self.assertEqual(row["predicted_regime"], "bear")
        self.assertEqual(row["anomaly_score"], -1)
        self.assertAlmostEqual(row["momentum_score"], -2.3)
        self.assertAlmostEqual(row["regime_confidence"], 0.78)
        self.assertEqual(row["model_version"], "v1/v1")
        self.assertEqual(row["scored_at"], "2026-05-01T06:00:00+00:00")

    def test_scored_at_defaults_when_not_provided(self) -> None:
        row = score_market_assets_job.build_score_row(
            asset_id="solana",
            symbol="SOL",
            regime="bull",
            anomaly_score=1,
            momentum=3.0,
        )
        self.assertIsNotNone(row["scored_at"])
        self.assertIsInstance(row["scored_at"], str)

    def test_momentum_none_is_preserved(self) -> None:
        row = score_market_assets_job.build_score_row(
            asset_id="ripple",
            symbol="XRP",
            regime="bear",
            anomaly_score=1,
            momentum=None,
        )
        self.assertIsNone(row["momentum_score"])


class ScoringResultTests(unittest.TestCase):
    def test_dataclass_fields_accessible(self) -> None:
        result = score_market_assets_job.ScoringResult(
            rows_scored=42,
            regime_used="market_regime_classifier",
            anomaly_used="market_anomaly_detector",
        )
        self.assertEqual(result.rows_scored, 42)
        self.assertEqual(result.regime_used, "market_regime_classifier")
        self.assertEqual(result.anomaly_used, "market_anomaly_detector")

    def test_dataclass_is_frozen(self) -> None:
        result = score_market_assets_job.ScoringResult(
            rows_scored=10,
            regime_used="model_a",
            anomaly_used="model_b",
        )
        with self.assertRaises(Exception):
            result.rows_scored = 99  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
