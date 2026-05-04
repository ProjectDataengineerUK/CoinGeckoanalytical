from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

try:
    import sklearn  # noqa: F401
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/train_market_model_job.py"
SPEC = importlib.util.spec_from_file_location("train_market_model_job", MODULE_PATH)
train_market_model_job = importlib.util.module_from_spec(SPEC)  # type: ignore[arg-type]
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = train_market_model_job
SPEC.loader.exec_module(train_market_model_job)  # type: ignore[union-attr]


class BuildRegimeLabelsTests(unittest.TestCase):
    def test_bull_label_when_above_five(self) -> None:
        labels = train_market_model_job.build_regime_labels([6.0, 10.0, 5.1])
        self.assertEqual(labels, ["bull", "bull", "bull"])

    def test_risk_off_label_when_below_minus_five(self) -> None:
        labels = train_market_model_job.build_regime_labels([-6.0, -10.0, -5.1])
        self.assertEqual(labels, ["risk_off", "risk_off", "risk_off"])

    def test_bear_label_for_values_in_middle_range(self) -> None:
        # Values in (2, 5] and [-5, -2) should be "bear"
        labels = train_market_model_job.build_regime_labels([2.1, -2.1, 4.9])
        self.assertEqual(labels, ["bear", "bear", "bear"])

    def test_neutral_label_for_sideways_market(self) -> None:
        labels = train_market_model_job.build_regime_labels([0.0, -1.9, 2.0])
        self.assertEqual(labels, ["neutral", "neutral", "neutral"])

    def test_mixed_labels_assigned_correctly(self) -> None:
        labels = train_market_model_job.build_regime_labels([8.0, -8.0, 0.5])
        self.assertEqual(labels, ["bull", "risk_off", "neutral"])

    def test_empty_input_returns_empty(self) -> None:
        self.assertEqual(train_market_model_job.build_regime_labels([]), [])


@unittest.skipUnless(_SKLEARN_AVAILABLE, "sklearn not installed in this environment")
class TrainRegimeModelTests(unittest.TestCase):
    def _make_training_data(self):
        X = [
            [2.0, 6.0, 52.0, 0.04],
            [-3.0, -6.0, 55.0, 0.06],
            [0.5, 1.0, 53.0, 0.05],
            [7.0, 8.0, 50.0, 0.03],
            [-2.0, -7.0, 57.0, 0.07],
        ]
        y = ["bull", "risk_off", "bear", "bull", "risk_off"]
        return X, y

    def test_returns_fitted_model_with_predict_method(self) -> None:
        X, y = self._make_training_data()
        model = train_market_model_job.train_regime_model(X, y)
        self.assertTrue(hasattr(model, "predict"))

    def test_predict_returns_labels_for_each_row(self) -> None:
        X, y = self._make_training_data()
        model = train_market_model_job.train_regime_model(X, y)
        preds = model.predict(X)
        self.assertEqual(len(preds), len(X))

    def test_predict_output_contains_valid_regime_labels(self) -> None:
        X, y = self._make_training_data()
        model = train_market_model_job.train_regime_model(X, y)
        preds = set(model.predict(X))
        self.assertTrue(preds.issubset({"bull", "bear", "risk_off", "neutral"}))


@unittest.skipUnless(_SKLEARN_AVAILABLE, "sklearn not installed in this environment")
class TrainAnomalyModelTests(unittest.TestCase):
    def _make_anomaly_data(self):
        import random
        rng = random.Random(0)
        return [
            [rng.uniform(0.01, 0.1), rng.uniform(-5, 5), rng.uniform(1e9, 1e12)]
            for _ in range(40)
        ]

    def test_returns_fitted_model_with_predict_method(self) -> None:
        X = self._make_anomaly_data()
        model = train_market_model_job.train_anomaly_model(X)
        self.assertTrue(hasattr(model, "predict"))

    def test_predict_returns_plus_one_or_minus_one(self) -> None:
        X = self._make_anomaly_data()
        model = train_market_model_job.train_anomaly_model(X)
        preds = set(model.predict(X))
        self.assertTrue(preds.issubset({1, -1}))


class TrainingResultTests(unittest.TestCase):
    def test_dataclass_fields_accessible(self) -> None:
        result = train_market_model_job.TrainingResult(
            regime_cv_accuracy=0.9,
            anomaly_contamination=0.05,
            regime_run_id="run-abc",
            anomaly_run_id="run-xyz",
        )
        self.assertAlmostEqual(result.regime_cv_accuracy, 0.9)
        self.assertEqual(result.regime_run_id, "run-abc")

    def test_dataclass_is_frozen(self) -> None:
        result = train_market_model_job.TrainingResult(
            regime_cv_accuracy=0.85,
            anomaly_contamination=0.05,
            regime_run_id="r1",
            anomaly_run_id="r2",
        )
        with self.assertRaises(Exception):
            result.regime_cv_accuracy = 0.99  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
