from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_CATALOG = os.environ.get("COINGECKO_CATALOG", "cgadev")
DEFAULT_SILVER_SCHEMA = "market_silver"
DEFAULT_GOLD_SCHEMA = "market_gold"
FEATURES_TABLE = "silver_market_features"
SCORES_TABLE = "gold_ml_scores"
REGIME_MODEL_NAME = "market_regime_classifier"
ANOMALY_MODEL_NAME = "market_anomaly_detector"
CHAMPION_ALIAS = "champion"


@dataclass(frozen=True)
class ScoringResult:
    rows_scored: int
    regime_used: str
    anomaly_used: str


def build_score_row(
    asset_id: str,
    symbol: str,
    regime: str,
    anomaly_score: int,
    momentum: float | None,
    regime_confidence: float | None = None,
    model_version: str | None = None,
    scored_at: str | None = None,
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "symbol": symbol,
        "scored_at": scored_at or datetime.now(timezone.utc).isoformat(),
        "predicted_regime": regime,
        "anomaly_score": anomaly_score,
        "momentum_score": momentum,
        "regime_confidence": regime_confidence,
        "model_version": model_version,
    }


def main(spark: Any, catalog: str = DEFAULT_CATALOG) -> ScoringResult:
    import mlflow
    import mlflow.sklearn
    import pandas as pd

    features_table = f"{catalog}.{DEFAULT_SILVER_SCHEMA}.{FEATURES_TABLE}"
    scores_table = f"{catalog}.{DEFAULT_GOLD_SCHEMA}.{SCORES_TABLE}"

    max_date = spark.sql(f"SELECT MAX(feature_date) FROM {features_table}").collect()[0][0]
    features_df: pd.DataFrame = (
        spark.table(features_table)
        .filter(f"feature_date = '{max_date}'")
        .toPandas()
    )

    mlflow.set_registry_uri("databricks-uc")

    try:
        regime_model = mlflow.sklearn.load_model(f"models:/{REGIME_MODEL_NAME}@{CHAMPION_ALIAS}")
        anomaly_model = mlflow.sklearn.load_model(f"models:/{ANOMALY_MODEL_NAME}@{CHAMPION_ALIAS}")
    except Exception as exc:
        print(f"WARN: no trained model found in registry ({exc}); scoring skipped until train job runs.")
        return ScoringResult(rows_scored=0, regime_used="none", anomaly_used="none")

    regime_version = CHAMPION_ALIAS
    anomaly_version = CHAMPION_ALIAS

    regime_feature_cols = [
        "price_change_pct_24h",
        "price_change_pct_7d",
        "dominance_pct_btc",
        "vol_to_cap_ratio",
    ]
    anomaly_feature_cols = ["vol_to_cap_ratio", "price_change_pct_24h", "market_cap_usd"]

    score_input = features_df.dropna(subset=regime_feature_cols + anomaly_feature_cols)

    X_regime = score_input[regime_feature_cols]
    X_anomaly = score_input[anomaly_feature_cols]

    regime_preds = regime_model.predict(X_regime)
    regime_proba = regime_model.predict_proba(X_regime).max(axis=1)
    anomaly_preds = anomaly_model.predict(X_anomaly)

    now_str = datetime.now(timezone.utc).isoformat()
    model_version_str = f"{regime_version}/{anomaly_version}"

    score_rows = [
        build_score_row(
            asset_id=str(row["asset_id"]),
            symbol=str(row["symbol"]),
            regime=str(regime_preds[i]),
            anomaly_score=int(anomaly_preds[i]),
            momentum=row.get("momentum_score"),
            regime_confidence=float(regime_proba[i]),
            model_version=model_version_str,
            scored_at=now_str,
        )
        for i, row in enumerate(score_input.to_dict(orient="records"))
    ]

    scores_spark_df = spark.createDataFrame(score_rows)
    scores_spark_df.write.mode("overwrite").format("delta").saveAsTable(scores_table)

    return ScoringResult(
        rows_scored=len(score_rows),
        regime_used=REGIME_MODEL_NAME,
        anomaly_used=ANOMALY_MODEL_NAME,
    )


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    _catalog = os.environ.get("COINGECKO_CATALOG", DEFAULT_CATALOG)
    try:
        _catalog = dbutils.widgets.get("catalog") or _catalog  # type: ignore[name-defined]
    except Exception:
        pass

    _result = main(spark_session, catalog=_catalog)

    import json
    print(
        json.dumps(
            {
                "rows_scored": _result.rows_scored,
                "regime_used": _result.regime_used,
                "anomaly_used": _result.anomaly_used,
            }
        )
    )
