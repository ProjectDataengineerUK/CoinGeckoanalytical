from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

DEFAULT_CATALOG = os.environ.get("COINGECKO_CATALOG", "cgadev")
DEFAULT_SILVER_SCHEMA = "market_silver"
DEFAULT_LOOKBACK_DAYS = 30
FEATURES_TABLE = "silver_market_features"

REGIME_MODEL_NAME = "market_regime_classifier"
ANOMALY_MODEL_NAME = "market_anomaly_detector"
CHAMPION_ALIAS = "champion"


@dataclass(frozen=True)
class TrainingResult:
    regime_cv_accuracy: float
    anomaly_contamination: float
    regime_run_id: str
    anomaly_run_id: str


def build_regime_labels(avg_pct_7d: list[float]) -> list[str]:
    labels = []
    for v in avg_pct_7d:
        if v > 5.0:
            labels.append("bull")
        elif v < -5.0:
            labels.append("risk_off")
        elif -2.0 <= v <= 2.0:
            labels.append("neutral")
        else:
            labels.append("bear")
    return labels


def train_regime_model(X: Any, y: Any) -> Any:
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model


def train_anomaly_model(X: Any) -> Any:
    from sklearn.ensemble import IsolationForest
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    return model


def _aggregate_regime_features(features_df: Any) -> Any:
    agg = (
        features_df.groupby("feature_date")
        .agg(
            avg_price_change_pct_24h=("price_change_pct_24h", "mean"),
            avg_price_change_pct_7d=("price_change_pct_7d", "mean"),
            avg_dominance_pct_btc=("dominance_pct_btc", "mean"),
            avg_vol_to_cap_ratio=("vol_to_cap_ratio", "mean"),
        )
        .reset_index()
        .dropna()
    )
    return agg


def _latest_asset_features(features_df: Any) -> Any:
    latest_date = features_df["feature_date"].max()
    snapshot = features_df[features_df["feature_date"] == latest_date].copy()
    cols = ["vol_to_cap_ratio", "price_change_pct_24h", "market_cap_usd"]
    return snapshot[cols].dropna()


def main(spark: Any, catalog: str = DEFAULT_CATALOG, lookback_days: int = DEFAULT_LOOKBACK_DAYS) -> TrainingResult:
    import mlflow
    import mlflow.sklearn

    features_table = f"{catalog}.{DEFAULT_SILVER_SCHEMA}.{FEATURES_TABLE}"
    features_df = spark.table(features_table).toPandas()

    agg_df = _aggregate_regime_features(features_df)
    regime_feature_cols = [
        "avg_price_change_pct_24h",
        "avg_price_change_pct_7d",
        "avg_dominance_pct_btc",
        "avg_vol_to_cap_ratio",
    ]
    X_regime = agg_df[regime_feature_cols].values
    y_regime = build_regime_labels(agg_df["avg_price_change_pct_7d"].tolist())

    with mlflow.start_run(run_name=f"{REGIME_MODEL_NAME}_training") as regime_run:
        regime_model = train_regime_model(X_regime, y_regime)

        from sklearn.model_selection import cross_val_score
        n_splits = min(5, len(X_regime))
        if n_splits >= 2:
            cv_scores = cross_val_score(regime_model, X_regime, y_regime, cv=n_splits)
            regime_cv_accuracy = float(cv_scores.mean())
            mlflow.log_metric("cv_accuracy_mean", regime_cv_accuracy)
            mlflow.log_metric("cv_accuracy_std", float(cv_scores.std()))
        else:
            regime_cv_accuracy = 0.0
            mlflow.log_metric("cv_accuracy_mean", 0.0)

        mlflow.log_param("n_estimators", 50)
        mlflow.log_param("lookback_days", lookback_days)
        mlflow.sklearn.log_model(regime_model, artifact_path="model")

        MIN_REGIME_CV_ACCURACY = 0.60
        if regime_cv_accuracy < MIN_REGIME_CV_ACCURACY and n_splits >= 2:
            raise ValueError(
                f"Regime CV accuracy {regime_cv_accuracy:.2f} below threshold "
                f"{MIN_REGIME_CV_ACCURACY}. Model not promoted."
            )

        mv = mlflow.register_model(
            model_uri=f"runs:/{regime_run.info.run_id}/model",
            name=REGIME_MODEL_NAME,
        )
        client = mlflow.tracking.MlflowClient()
        client.set_registered_model_alias(REGIME_MODEL_NAME, CHAMPION_ALIAS, mv.version)
        regime_run_id = regime_run.info.run_id

    X_anomaly = _latest_asset_features(features_df).values

    with mlflow.start_run(run_name=f"{ANOMALY_MODEL_NAME}_training") as anomaly_run:
        anomaly_model = train_anomaly_model(X_anomaly)

        mlflow.log_param("contamination", 0.05)
        mlflow.log_param("lookback_days", lookback_days)
        mlflow.sklearn.log_model(anomaly_model, artifact_path="model")

        mv_a = mlflow.register_model(
            model_uri=f"runs:/{anomaly_run.info.run_id}/model",
            name=ANOMALY_MODEL_NAME,
        )
        client.set_registered_model_alias(ANOMALY_MODEL_NAME, CHAMPION_ALIAS, mv_a.version)
        anomaly_run_id = anomaly_run.info.run_id

    return TrainingResult(
        regime_cv_accuracy=regime_cv_accuracy,
        anomaly_contamination=0.05,
        regime_run_id=regime_run_id,
        anomaly_run_id=anomaly_run_id,
    )


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    _catalog = os.environ.get("COINGECKO_CATALOG", DEFAULT_CATALOG)
    _lookback_days = DEFAULT_LOOKBACK_DAYS
    try:
        _catalog = dbutils.widgets.get("catalog") or _catalog  # type: ignore[name-defined]
    except Exception:  # pragma: no cover
        pass
    try:
        _lookback_days = int(dbutils.widgets.get("lookback_days"))  # type: ignore[name-defined]
    except Exception:  # pragma: no cover
        pass

    _result = main(spark_session, catalog=_catalog, lookback_days=_lookback_days)
    print(json.dumps({
        "regime_cv_accuracy": _result.regime_cv_accuracy,
        "anomaly_contamination": _result.anomaly_contamination,
        "regime_run_id": _result.regime_run_id,
        "anomaly_run_id": _result.anomaly_run_id,
    }))
