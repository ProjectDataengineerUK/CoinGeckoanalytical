from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier

DEFAULT_CATALOG = os.environ.get("COINGECKO_CATALOG", "cgadev")
DEFAULT_SILVER_SCHEMA = "market_silver"
DEFAULT_LOOKBACK_DAYS = 30
FEATURES_TABLE = "silver_market_features"

REGIME_MODEL_NAME = "market_regime_classifier"
ANOMALY_MODEL_NAME = "market_anomaly_detector"
CHAMPION_ALIAS = "champion"


@dataclass(frozen=True)
class TrainingResult:
    regime_accuracy: float
    anomaly_contamination: float
    regime_run_id: str
    anomaly_run_id: str


def build_regime_labels(df: pd.DataFrame) -> pd.Series:
    avg_7d = df["avg_price_change_pct_7d"]
    labels = avg_7d.apply(
        lambda v: "bull" if v > 5 else ("risk_off" if v < -5 else "bear")
    )
    return labels


def train_regime_model(X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model


def train_anomaly_model(X: pd.DataFrame) -> IsolationForest:
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    return model


def _aggregate_regime_features(features_df: pd.DataFrame) -> pd.DataFrame:
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


def _latest_asset_features(features_df: pd.DataFrame) -> pd.DataFrame:
    latest_date = features_df["feature_date"].max()
    snapshot = features_df[features_df["feature_date"] == latest_date].copy()
    cols = ["vol_to_cap_ratio", "price_change_pct_24h", "market_cap_usd"]
    return snapshot[cols].dropna()


def main(spark: Any, catalog: str = DEFAULT_CATALOG, lookback_days: int = DEFAULT_LOOKBACK_DAYS) -> TrainingResult:
    features_table = f"{catalog}.{DEFAULT_SILVER_SCHEMA}.{FEATURES_TABLE}"
    features_df: pd.DataFrame = spark.table(features_table).toPandas()

    agg_df = _aggregate_regime_features(features_df)
    regime_feature_cols = [
        "avg_price_change_pct_24h",
        "avg_price_change_pct_7d",
        "avg_dominance_pct_btc",
        "avg_vol_to_cap_ratio",
    ]
    X_regime = agg_df[regime_feature_cols]
    y_regime = build_regime_labels(agg_df)

    with mlflow.start_run(run_name=f"{REGIME_MODEL_NAME}_training") as regime_run:
        regime_model = train_regime_model(X_regime, y_regime)
        train_preds = regime_model.predict(X_regime)
        regime_accuracy = float((train_preds == y_regime.values).mean())

        mlflow.log_param("n_estimators", 50)
        mlflow.log_param("lookback_days", lookback_days)
        mlflow.log_metric("train_accuracy", regime_accuracy)
        mlflow.sklearn.log_model(regime_model, artifact_path="model")

        mv = mlflow.register_model(
            model_uri=f"runs:/{regime_run.info.run_id}/model",
            name=REGIME_MODEL_NAME,
        )
        client = mlflow.tracking.MlflowClient()
        client.set_registered_model_alias(REGIME_MODEL_NAME, CHAMPION_ALIAS, mv.version)
        regime_run_id = regime_run.info.run_id

    asset_df = _latest_asset_features(features_df)
    X_anomaly = asset_df

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
        regime_accuracy=regime_accuracy,
        anomaly_contamination=0.05,
        regime_run_id=regime_run_id,
        anomaly_run_id=anomaly_run_id,
    )


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    _catalog = os.environ.get("COINGECKO_CATALOG", DEFAULT_CATALOG)
    _lookback_days = DEFAULT_LOOKBACK_DAYS
    try:
        _catalog = dbutils.widgets.get("catalog") or _catalog  # type: ignore[name-defined]
    except Exception:
        pass
    try:
        _lookback_days = int(dbutils.widgets.get("lookback_days"))  # type: ignore[name-defined]
    except Exception:
        pass

    _result = main(spark_session, catalog=_catalog, lookback_days=_lookback_days)

    import json
    print(
        json.dumps(
            {
                "regime_accuracy": _result.regime_accuracy,
                "anomaly_contamination": _result.anomaly_contamination,
                "regime_run_id": _result.regime_run_id,
                "anomaly_run_id": _result.anomaly_run_id,
            }
        )
    )
