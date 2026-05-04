from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/model_drift_monitoring_job.py"
SPEC = importlib.util.spec_from_file_location("model_drift_monitoring_job", MODULE_PATH)
model_drift_monitoring_job = importlib.util.module_from_spec(SPEC)  # type: ignore[arg-type]
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = model_drift_monitoring_job
SPEC.loader.exec_module(model_drift_monitoring_job)  # type: ignore[union-attr]


class ComputePsiTests(unittest.TestCase):
    def test_compute_psi_identical_distributions(self) -> None:
        baseline = {"bull": 1.0}
        current = {"bull": 1.0}
        psi = model_drift_monitoring_job.compute_psi(baseline, current)
        self.assertAlmostEqual(psi, 0.0, places=5)

    def test_compute_psi_large_shift(self) -> None:
        baseline = {"bull": 0.9, "bear": 0.1}
        current = {"bull": 0.1, "bear": 0.9}
        psi = model_drift_monitoring_job.compute_psi(baseline, current)
        self.assertGreater(psi, 0.2)


class ComputeRegimeDistributionTests(unittest.TestCase):
    def test_compute_regime_distribution_empty(self) -> None:
        result = model_drift_monitoring_job.compute_regime_distribution([])
        self.assertEqual(result, {})

    def test_compute_regime_distribution_single(self) -> None:
        rows = [{"predicted_regime": "bull"}, {"predicted_regime": "bull"}]
        result = model_drift_monitoring_job.compute_regime_distribution(rows)
        self.assertAlmostEqual(result["bull"], 1.0)

    def test_compute_regime_distribution_sum_to_one(self) -> None:
        rows = [
            {"predicted_regime": "bull"},
            {"predicted_regime": "bear"},
            {"predicted_regime": "neutral"},
            {"predicted_regime": "bull"},
        ]
        result = model_drift_monitoring_job.compute_regime_distribution(rows)
        self.assertAlmostEqual(sum(result.values()), 1.0, places=9)


class DriftResultDataclassTests(unittest.TestCase):
    def test_drift_result_dataclass(self) -> None:
        result = model_drift_monitoring_job.DriftResult(
            psi_score=0.15,
            alert_written=False,
            regime_distribution_24h={"bull": 0.6, "bear": 0.4},
            regime_distribution_7d={"bull": 0.5, "bear": 0.5},
        )
        self.assertAlmostEqual(result.psi_score, 0.15)
        self.assertFalse(result.alert_written)
        self.assertEqual(result.regime_distribution_24h["bull"], 0.6)
        self.assertEqual(result.regime_distribution_7d["bear"], 0.5)
        with self.assertRaises(Exception):
            result.psi_score = 0.99  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
