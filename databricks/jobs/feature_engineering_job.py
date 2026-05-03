from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any

DEFAULT_CATALOG = os.environ.get("COINGECKO_CATALOG", "cgadev")
DEFAULT_SILVER_SCHEMA = "market_silver"
DEFAULT_LOOKBACK_DAYS = 30

FEATURES_TABLE = "silver_market_features"
SILVER_CHANGES_TABLE = "silver_market_changes"
SILVER_DOMINANCE_TABLE = "silver_market_dominance"


@dataclass(frozen=True)
class FeatureEngineeringResult:
    rows_written: int
    target_table: str
    lookback_days: int


def compute_vol_to_cap_ratio(vol: float | None, cap: float | None) -> float | None:
    if vol is None or cap is None or cap == 0:
        return None
    return vol / cap


def compute_momentum_score(p24h: float | None, p7d: float | None) -> float | None:
    if p24h is None or p7d is None:
        return None
    return 0.4 * p24h + 0.6 * p7d


def build_feature_row(row_dict: dict[str, Any]) -> dict[str, Any]:
    asset_id = row_dict.get("asset_id")
    symbol = row_dict.get("symbol")
    observed_at = row_dict.get("observed_at")
    price_change_pct_24h = row_dict.get("price_change_pct_24h")
    price_change_pct_7d = row_dict.get("price_change_pct_7d")
    volume_24h_usd = row_dict.get("volume_24h_usd")
    market_cap_usd = row_dict.get("market_cap_usd")
    dominance_pct_btc = row_dict.get("dominance_pct_btc")

    vol_to_cap_ratio = compute_vol_to_cap_ratio(volume_24h_usd, market_cap_usd)
    momentum_score = compute_momentum_score(price_change_pct_24h, price_change_pct_7d)

    feature_date: str | None
    if observed_at is not None:
        feature_date = str(observed_at)[:10]
    else:
        feature_date = None

    return {
        "asset_id": asset_id,
        "symbol": symbol,
        "observed_at": observed_at,
        "price_change_pct_24h": price_change_pct_24h,
        "price_change_pct_7d": price_change_pct_7d,
        "volume_24h_usd": volume_24h_usd,
        "market_cap_usd": market_cap_usd,
        "vol_to_cap_ratio": vol_to_cap_ratio,
        "dominance_pct_btc": dominance_pct_btc,
        "momentum_score": momentum_score,
        "feature_date": feature_date,
    }


def build_features_dataframe(spark: Any, catalog: str, lookback_days: int) -> Any:
    changes_table = f"{catalog}.{DEFAULT_SILVER_SCHEMA}.{SILVER_CHANGES_TABLE}"
    dominance_table = f"{catalog}.{DEFAULT_SILVER_SCHEMA}.{SILVER_DOMINANCE_TABLE}"

    return spark.sql(
        f"""
        WITH changes AS (
            SELECT
                asset_id,
                symbol,
                observed_at,
                price_change_pct_24h,
                price_change_pct_7d,
                volume_24h_usd,
                market_cap_usd
            FROM {changes_table}
            WHERE observed_at >= CURRENT_TIMESTAMP() - INTERVAL {lookback_days} DAYS
              AND asset_id IS NOT NULL
        ),
        btc_dominance AS (
            SELECT
                observed_at,
                dominance_pct AS dominance_pct_btc
            FROM {dominance_table}
            WHERE dominance_group = 'btc'
        ),
        joined AS (
            SELECT
                c.asset_id,
                c.symbol,
                c.observed_at,
                c.price_change_pct_24h,
                c.price_change_pct_7d,
                c.volume_24h_usd,
                c.market_cap_usd,
                CASE
                    WHEN c.market_cap_usd IS NULL OR c.market_cap_usd = 0 THEN NULL
                    ELSE c.volume_24h_usd / c.market_cap_usd
                END AS vol_to_cap_ratio,
                d.dominance_pct_btc,
                CAST(0.4 * c.price_change_pct_24h + 0.6 * c.price_change_pct_7d AS DOUBLE) AS momentum_score,
                DATE(c.observed_at) AS feature_date
            FROM changes c
            LEFT JOIN btc_dominance d
                ON DATE_TRUNC('hour', c.observed_at) = DATE_TRUNC('hour', d.observed_at)
        )
        SELECT * FROM joined
        """
    )


def main(spark: Any, catalog: str = DEFAULT_CATALOG, lookback_days: int = DEFAULT_LOOKBACK_DAYS) -> FeatureEngineeringResult:
    target_table = f"{catalog}.{DEFAULT_SILVER_SCHEMA}.{FEATURES_TABLE}"
    df = build_features_dataframe(spark, catalog, lookback_days)
    (
        df.write
        .mode("overwrite")
        .partitionBy("feature_date")
        .format("delta")
        .saveAsTable(target_table)
    )
    rows = df.count()
    return FeatureEngineeringResult(
        rows_written=rows,
        target_table=target_table,
        lookback_days=lookback_days,
    )


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    _lookback_days = DEFAULT_LOOKBACK_DAYS
    try:
        _lookback_days = int(dbutils.widgets.get("lookback_days"))  # type: ignore[name-defined]
    except Exception:
        pass

    _catalog = os.environ.get("COINGECKO_CATALOG", DEFAULT_CATALOG)
    try:
        _catalog = dbutils.widgets.get("catalog") or _catalog  # type: ignore[name-defined]
    except Exception:
        pass

    _result = main(spark_session, catalog=_catalog, lookback_days=_lookback_days)

    import json
    print(
        json.dumps(
            {
                "rows_written": _result.rows_written,
                "target_table": _result.target_table,
                "lookback_days": _result.lookback_days,
            }
        )
    )
