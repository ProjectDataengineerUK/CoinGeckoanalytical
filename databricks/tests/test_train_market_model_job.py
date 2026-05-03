from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

import pandas as pd

MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/train_market_model_job.py"
SPEC = importlib.util.spec_from_file_location("train_market_model_job", MODULE_PATH)
train_market_model_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = train_market_model_job
SPEC.loader.exec_module(train_market_model_job)


class BuildRegimeLabelsTests(unittest.TestCase):
    def _make_df(self, values: list[float]) -> pd.DataFrame:
        return pd.DataFrame({"avg_price_change_pct_7d": values})

    def test_bull_label_when_above_five(self) -> None:
        df = self._make_df([6.0, 10.0, 5.1])
        labels = train_market_model_job.build_regime_labels(df)
        self.assertTrue((labels == "bull").all())

    def test_risk_off_label_when_below_minus_five(self) -> None:
        df = self._make_df([-6.0, -10.0, -5.1])
        labels = train_market_model_job.build_regime_labels(df)
        self.assertTrue((labels == "risk_off").all())

    def test_bear_label_for_values_in_middle_range(self) -> None:
        df = self._make_df([0.0, -4.9, 4.9, -5.0, 5.0])
        labels = train_market_model_job.build_regime_labels(df)
        self.assertTrue((labels == "bear").all())

    def test_mixed_labels_assigned_correctly(self) -> None:
        df = self._make_df([8.0, -8.0, 1.0])
        labels = train_market_model_job.build_regime_labels(df)
        self.assertEqual(labels.iloc[0], "bull")
        self.assertEqual(labels.iloc[1], "risk_off")
        self.assertEqual(labels.iloc[2], "bear")


class TrainRegimeModelTests(unittest.TestCase):
    def _make_training_data(self) -> tuple[pd.DataFrame, pd.Series]:
        X = pd.DataFrame(
            {
                "avg_price_change_pct_24h": [2.0, -3.0, 0.5, 7.0, -6.0],
                "avg_price_change_pct_7d": [6.0, -6.0, 1.0, 8.0, -7.0],
                "avg_dominance_pct_btc": [52.0, 55.0, 53.0, 50.0, 57.0],
                "avg_vol_to_cap_ratio": [0.04, 0.06, 0.05, 0.03, 0.07],
            }
        )
        y = pd.Series(["bull", "risk_off", "bear", "bull", "risk_off"])
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
        valid = {"bull", "bear", "risk_off"}
        self.assertTrue(preds.issubset(valid))


class TrainAnomalyModelTests(unittest.TestCase):
    def _make_anomaly_data(self) -> pd.DataFrame:
        import numpy as np

        rng = np.random.default_rng(0)
        return pd.DataFrame(
            {
                "vol_to_cap_ratio": rng.uniform(0.01, 0.1, 40).tolist(),
                "price_change_pct_24h": rng.uniform(-5, 5, 40).tolist(),
                "market_cap_usd": rng.uniform(1e9, 1e12, 40).tolist(),
            }
        )

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
            regime_accuracy=0.9,
            anomaly_contamination=0.05,
            regime_run_id="run-abc",
            anomaly_run_id="run-xyz",
        )
        self.assertAlmostEqual(result.regime_accuracy, 0.9)
        self.assertAlmostEqual(result.anomaly_contamination, 0.05)
        self.assertEqual(result.regime_run_id, "run-abc")
        self.assertEqual(result.anomaly_run_id, "run-xyz")

    def test_dataclass_is_frozen(self) -> None:
        result = train_market_model_job.TrainingResult(
            regime_accuracy=0.85,
            anomaly_contamination=0.05,
            regime_run_id="r1",
            anomaly_run_id="r2",
        )
        with self.assertRaises(Exception):
            result.regime_accuracy = 0.99  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
