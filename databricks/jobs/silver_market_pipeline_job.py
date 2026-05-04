from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any


DEFAULT_CATALOG = "cgadev"
DEFAULT_SILVER_SCHEMA = "market_silver"
DEFAULT_BRONZE_SCHEMA = "market_bronze"
DEFAULT_BRONZE_TABLE = "bronze_market_snapshots"

SILVER_CHANGES_TABLE = "silver_market_changes"
SILVER_DOMINANCE_TABLE = "silver_market_dominance"
SILVER_COMPARISON_TABLE = "silver_cross_asset_comparison"

SILVER_CHANGES_FIELDS = (
    "asset_id",
    "symbol",
    "name",
    "observed_at",
    "window_id",
    "price_change_pct_1h",
    "price_change_pct_24h",
    "price_change_pct_7d",
    "volume_24h_usd",
    "market_cap_usd",
)

SILVER_DOMINANCE_FIELDS = (
    "observed_at",
    "dominance_group",
    "market_cap_usd",
    "dominance_pct",
)

SILVER_COMPARISON_FIELDS = (
    "asset_id",
    "symbol",
    "observed_at",
    "price_usd",
    "market_cap_usd",
    "volume_24h_usd",
    "price_change_pct_24h",
    "price_change_pct_7d",
    "correlation_bucket",
)

SILVER_CHANGES_SELECT = (
    "CAST(asset_id AS STRING) AS asset_id",
    "UPPER(CAST(symbol AS STRING)) AS symbol",
    "CAST(name AS STRING) AS name",
    "CAST(observed_at AS TIMESTAMP) AS observed_at",
    "CAST(DATE(observed_at) AS STRING) AS window_id",
    "CAST(price_change_pct_1h AS DECIMAL(38, 8)) AS price_change_pct_1h",
    "CAST(price_change_pct_24h AS DECIMAL(38, 8)) AS price_change_pct_24h",
    "CAST(price_change_pct_7d AS DECIMAL(38, 8)) AS price_change_pct_7d",
    "CAST(volume_24h_usd AS DECIMAL(38, 8)) AS volume_24h_usd",
    "CAST(market_cap_usd AS DECIMAL(38, 8)) AS market_cap_usd",
)

SILVER_DOMINANCE_SELECT = (
    "CAST(observed_at AS TIMESTAMP) AS observed_at",
    "CAST(dominance_group AS STRING) AS dominance_group",
    "CAST(market_cap_usd AS DECIMAL(38, 8)) AS market_cap_usd",
    "CAST(dominance_pct AS DECIMAL(38, 8)) AS dominance_pct",
)

SILVER_COMPARISON_SELECT = (
    "CAST(asset_id AS STRING) AS asset_id",
    "UPPER(CAST(symbol AS STRING)) AS symbol",
    "CAST(observed_at AS TIMESTAMP) AS observed_at",
    "CAST(price_usd AS DECIMAL(38, 8)) AS price_usd",
    "CAST(market_cap_usd AS DECIMAL(38, 8)) AS market_cap_usd",
    "CAST(volume_24h_usd AS DECIMAL(38, 8)) AS volume_24h_usd",
    "CAST(price_change_pct_24h AS DECIMAL(38, 8)) AS price_change_pct_24h",
    "CAST(price_change_pct_7d AS DECIMAL(38, 8)) AS price_change_pct_7d",
    "CAST(correlation_bucket AS STRING) AS correlation_bucket",
)


@dataclass(frozen=True)
class SilverPipelineConfig:
    target_catalog: str
    target_env: str
    silver_schema: str
    bronze_schema: str
    bronze_table: str

    @property
    def bronze_full_table(self) -> str:
        return f"{self.target_catalog}.{self.bronze_schema}.{self.bronze_table}"

    @property
    def changes_full_table(self) -> str:
        return f"{self.target_catalog}.{self.silver_schema}.{SILVER_CHANGES_TABLE}"

    @property
    def dominance_full_table(self) -> str:
        return f"{self.target_catalog}.{self.silver_schema}.{SILVER_DOMINANCE_TABLE}"

    @property
    def comparison_full_table(self) -> str:
        return f"{self.target_catalog}.{self.silver_schema}.{SILVER_COMPARISON_TABLE}"


@dataclass(frozen=True)
class SilverPipelineResult:
    changes_rows_written: int
    dominance_rows_written: int
    comparison_rows_written: int
    changes_target_table: str
    dominance_target_table: str
    comparison_target_table: str


def load_pipeline_config_from_env(env: dict[str, str] | None = None) -> SilverPipelineConfig:
    active_env = env if env is not None else os.environ
    target_catalog = active_env.get("SILVER_TARGET_CATALOG", DEFAULT_CATALOG)
    target_env = active_env.get("SILVER_TARGET_ENV", DEFAULT_CATALOG)
    return SilverPipelineConfig(
        target_catalog=target_catalog,
        target_env=target_env,
        silver_schema=active_env.get("SILVER_SCHEMA", DEFAULT_SILVER_SCHEMA),
        bronze_schema=active_env.get("BRONZE_SCHEMA", DEFAULT_BRONZE_SCHEMA),
        bronze_table=active_env.get("BRONZE_TABLE", DEFAULT_BRONZE_TABLE),
    )


def normalize_silver_changes_row(row: dict[str, Any]) -> dict[str, Any]:
    asset_id = row.get("asset_id")
    symbol = row.get("symbol")
    observed_at = row.get("observed_at")

    if not asset_id:
        raise ValueError("silver_market_changes row is missing asset_id.")
    if not symbol:
        raise ValueError("silver_market_changes row is missing symbol.")
    if not observed_at:
        raise ValueError("silver_market_changes row is missing observed_at.")

    import datetime as _dt

    if isinstance(observed_at, str):
        obs_date = observed_at[:10]
    elif isinstance(observed_at, (_dt.datetime, _dt.date)):
        obs_date = str(observed_at)[:10]
    else:
        obs_date = str(observed_at)[:10]

    return {
        "asset_id": str(asset_id),
        "symbol": str(symbol).upper(),
        "name": str(row.get("name") or "unmapped"),
        "observed_at": str(observed_at),
        "window_id": obs_date,
        "price_change_pct_1h": _coerce_optional_float(row.get("price_change_pct_1h")),
        "price_change_pct_24h": _coerce_optional_float(row.get("price_change_pct_24h")),
        "price_change_pct_7d": _coerce_optional_float(row.get("price_change_pct_7d")),
        "volume_24h_usd": _coerce_required_decimal(
            row.get("volume_24h_usd"), "volume_24h_usd"
        ),
        "market_cap_usd": _coerce_required_decimal(
            row.get("market_cap_usd"), "market_cap_usd"
        ),
    }


def normalize_silver_dominance_row(row: dict[str, Any]) -> dict[str, Any]:
    observed_at = row.get("observed_at")
    dominance_group = row.get("dominance_group")
    market_cap_usd = row.get("market_cap_usd")

    if not observed_at:
        raise ValueError("silver_market_dominance row is missing observed_at.")
    if not dominance_group:
        raise ValueError("silver_market_dominance row is missing dominance_group.")
    if market_cap_usd is None:
        raise ValueError("silver_market_dominance row is missing market_cap_usd.")

    return {
        "observed_at": str(observed_at),
        "dominance_group": str(dominance_group),
        "market_cap_usd": _coerce_required_decimal(market_cap_usd, "market_cap_usd"),
        "dominance_pct": _coerce_optional_float(row.get("dominance_pct")),
    }


def normalize_silver_comparison_row(row: dict[str, Any]) -> dict[str, Any]:
    asset_id = row.get("asset_id")
    symbol = row.get("symbol")
    observed_at = row.get("observed_at")
    price_usd = row.get("price_usd")

    if not asset_id:
        raise ValueError("silver_cross_asset_comparison row is missing asset_id.")
    if not symbol:
        raise ValueError("silver_cross_asset_comparison row is missing symbol.")
    if not observed_at:
        raise ValueError("silver_cross_asset_comparison row is missing observed_at.")
    if price_usd is None:
        raise ValueError("silver_cross_asset_comparison row is missing price_usd.")

    market_cap_usd = _coerce_required_decimal(
        row.get("market_cap_usd"), "market_cap_usd"
    )
    market_cap_rank = row.get("market_cap_rank")

    if market_cap_rank is not None:
        rank_int = int(market_cap_rank)
        if rank_int <= 10:
            correlation_bucket = "large_cap"
        elif rank_int <= 50:
            correlation_bucket = "mid_cap"
        else:
            correlation_bucket = "broad_market"
    else:
        correlation_bucket = "broad_market"

    return {
        "asset_id": str(asset_id),
        "symbol": str(symbol).upper(),
        "observed_at": str(observed_at),
        "price_usd": _coerce_required_decimal(price_usd, "price_usd"),
        "market_cap_usd": market_cap_usd,
        "volume_24h_usd": _coerce_required_decimal(
            row.get("volume_24h_usd"), "volume_24h_usd"
        ),
        "price_change_pct_24h": _coerce_optional_float(row.get("price_change_pct_24h")),
        "price_change_pct_7d": _coerce_optional_float(row.get("price_change_pct_7d")),
        "correlation_bucket": correlation_bucket,
    }


def build_silver_changes_dataframe(spark: Any, config: SilverPipelineConfig) -> Any:
    bronze_table = config.bronze_full_table

    lagged = spark.sql(
        f"""
        WITH deduped AS (
            SELECT
                asset_id,
                symbol,
                name,
                observed_at,
                market_cap_usd,
                price_usd,
                volume_24h_usd,
                ROW_NUMBER() OVER (
                    PARTITION BY asset_id, observed_at
                    ORDER BY ingested_at DESC, source_record_id DESC
                ) AS rn
            FROM {bronze_table}
            WHERE asset_id IS NOT NULL
              AND observed_at IS NOT NULL
        ),
        base AS (
            SELECT
                asset_id,
                symbol,
                name,
                observed_at,
                market_cap_usd,
                price_usd,
                volume_24h_usd
            FROM deduped
            WHERE rn = 1
        ),
        lagged AS (
            SELECT
                b.asset_id,
                b.symbol,
                b.name,
                b.observed_at,
                b.price_usd,
                b.volume_24h_usd,
                b.market_cap_usd,
                -- 1h: closest snapshot in [55min, 65min] ago window
                FIRST_VALUE(p1h.price_usd) OVER (
                    PARTITION BY b.asset_id, b.observed_at
                    ORDER BY ABS(
                        UNIX_TIMESTAMP(b.observed_at) - UNIX_TIMESTAMP(p1h.observed_at) - 3600
                    )
                ) AS price_1h_ago,
                -- 24h: closest snapshot in [23h, 25h] ago window (1380–1500 min)
                FIRST_VALUE(p24h.price_usd) OVER (
                    PARTITION BY b.asset_id, b.observed_at
                    ORDER BY ABS(
                        UNIX_TIMESTAMP(b.observed_at) - UNIX_TIMESTAMP(p24h.observed_at) - 86400
                    )
                ) AS price_24h_ago,
                -- 7d: closest snapshot in [7d ± 2h] window
                FIRST_VALUE(p7d.price_usd) OVER (
                    PARTITION BY b.asset_id, b.observed_at
                    ORDER BY ABS(
                        UNIX_TIMESTAMP(b.observed_at) - UNIX_TIMESTAMP(p7d.observed_at) - 604800
                    )
                ) AS price_7d_ago
            FROM base b
            LEFT JOIN base p1h
                ON p1h.asset_id = b.asset_id
               AND p1h.observed_at BETWEEN b.observed_at - INTERVAL 65 MINUTES
                                        AND b.observed_at - INTERVAL 55 MINUTES
            LEFT JOIN base p24h
                ON p24h.asset_id = b.asset_id
               AND p24h.observed_at BETWEEN b.observed_at - INTERVAL 1500 MINUTES
                                         AND b.observed_at - INTERVAL 1380 MINUTES
            LEFT JOIN base p7d
                ON p7d.asset_id = b.asset_id
               AND p7d.observed_at BETWEEN b.observed_at - INTERVAL 7 DAYS - INTERVAL 2 HOURS
                                        AND b.observed_at - INTERVAL 7 DAYS + INTERVAL 2 HOURS
        )
        SELECT
            asset_id,
            symbol,
            name,
            observed_at,
            DATE(observed_at) AS window_id,
            CASE
                WHEN price_1h_ago IS NULL OR price_1h_ago = 0 THEN NULL
                ELSE ((price_usd - price_1h_ago) / price_1h_ago) * 100
            END AS price_change_pct_1h,
            CASE
                WHEN price_24h_ago IS NULL OR price_24h_ago = 0 THEN NULL
                ELSE ((price_usd - price_24h_ago) / price_24h_ago) * 100
            END AS price_change_pct_24h,
            CASE
                WHEN price_7d_ago IS NULL OR price_7d_ago = 0 THEN NULL
                ELSE ((price_usd - price_7d_ago) / price_7d_ago) * 100
            END AS price_change_pct_7d,
            volume_24h_usd,
            market_cap_usd
        FROM lagged
        """
    )

    return (
        lagged.selectExpr(*SILVER_CHANGES_SELECT)
        .dropDuplicates(["asset_id", "window_id", "observed_at"])
    )


def build_silver_dominance_dataframe(spark: Any, config: SilverPipelineConfig) -> Any:
    bronze_table = config.bronze_full_table

    dominance = spark.sql(
        f"""
        WITH deduped AS (
            SELECT
                asset_id,
                UPPER(symbol) AS symbol,
                observed_at,
                market_cap_usd,
                ROW_NUMBER() OVER (
                    PARTITION BY asset_id, observed_at
                    ORDER BY ingested_at DESC, source_record_id DESC
                ) AS rn
            FROM {bronze_table}
            WHERE asset_id IS NOT NULL
              AND observed_at IS NOT NULL
              AND market_cap_usd IS NOT NULL
              AND market_cap_usd >= 0
        ),
        base AS (
            SELECT
                asset_id,
                symbol,
                observed_at,
                market_cap_usd,
                SUM(market_cap_usd) OVER (PARTITION BY observed_at) AS total_market_cap_usd
            FROM deduped
            WHERE rn = 1
        )
        SELECT
            observed_at,
            CASE
                WHEN symbol = 'BTC' THEN 'btc'
                WHEN symbol = 'ETH' THEN 'eth'
                WHEN symbol IN ('USDT', 'USDC', 'DAI', 'FDUSD', 'TUSD') THEN 'stablecoins'
                ELSE 'long_tail'
            END AS dominance_group,
            SUM(market_cap_usd) AS market_cap_usd,
            CASE
                WHEN MAX(total_market_cap_usd) = 0 THEN NULL
                ELSE (SUM(market_cap_usd) / MAX(total_market_cap_usd)) * 100
            END AS dominance_pct
        FROM base
        GROUP BY
            observed_at,
            CASE
                WHEN symbol = 'BTC' THEN 'btc'
                WHEN symbol = 'ETH' THEN 'eth'
                WHEN symbol IN ('USDT', 'USDC', 'DAI', 'FDUSD', 'TUSD') THEN 'stablecoins'
                ELSE 'long_tail'
            END
        """
    )

    return (
        dominance.selectExpr(*SILVER_DOMINANCE_SELECT)
        .dropDuplicates(["dominance_group", "observed_at"])
    )


def build_silver_comparison_dataframe(spark: Any, config: SilverPipelineConfig) -> Any:
    bronze_table = config.bronze_full_table

    comparison = spark.sql(
        f"""
        WITH deduped AS (
            SELECT
                asset_id,
                UPPER(symbol) AS symbol,
                observed_at,
                price_usd,
                market_cap_usd,
                volume_24h_usd,
                market_cap_rank,
                ROW_NUMBER() OVER (
                    PARTITION BY asset_id, observed_at
                    ORDER BY ingested_at DESC, source_record_id DESC
                ) AS rn
            FROM {bronze_table}
            WHERE asset_id IS NOT NULL
              AND observed_at IS NOT NULL
        ),
        base AS (
            SELECT
                asset_id,
                symbol,
                observed_at,
                price_usd,
                market_cap_usd,
                volume_24h_usd,
                market_cap_rank
            FROM deduped
            WHERE rn = 1
        ),
        prices AS (
            SELECT
                b.asset_id,
                b.symbol,
                b.observed_at,
                b.price_usd,
                b.market_cap_usd,
                b.volume_24h_usd,
                b.market_cap_rank,
                -- 24h: closest snapshot 23.5–24.5 hours ago
                (SELECT p24h.price_usd FROM base p24h
                 WHERE p24h.asset_id = b.asset_id
                   AND p24h.observed_at BETWEEN b.observed_at - INTERVAL 1470 MINUTES
                                            AND b.observed_at - INTERVAL 1410 MINUTES
                 ORDER BY ABS(UNIX_TIMESTAMP(b.observed_at) - UNIX_TIMESTAMP(p24h.observed_at) - 86400) ASC
                 LIMIT 1) AS price_24h_ago,
                -- 7d: closest snapshot 6.9–7.1 days ago
                (SELECT p7d.price_usd FROM base p7d
                 WHERE p7d.asset_id = b.asset_id
                   AND p7d.observed_at BETWEEN b.observed_at - INTERVAL 7 DAYS - INTERVAL 2 HOURS
                                           AND b.observed_at - INTERVAL 7 DAYS + INTERVAL 2 HOURS
                 ORDER BY ABS(UNIX_TIMESTAMP(b.observed_at) - UNIX_TIMESTAMP(p7d.observed_at) - 604800) ASC
                 LIMIT 1) AS price_7d_ago
            FROM base b
        )
        SELECT
            asset_id,
            symbol,
            observed_at,
            price_usd,
            market_cap_usd,
            volume_24h_usd,
            CASE
                WHEN market_cap_rank <= 10 THEN 'large_cap'
                WHEN market_cap_rank <= 50 THEN 'mid_cap'
                ELSE 'broad_market'
            END AS correlation_bucket,
            CASE WHEN price_24h_ago IS NULL OR price_24h_ago = 0 THEN NULL
                 ELSE ROUND(((price_usd - price_24h_ago) / price_24h_ago) * 100, 4) END AS price_change_pct_24h,
            CASE WHEN price_7d_ago IS NULL OR price_7d_ago = 0 THEN NULL
                 ELSE ROUND(((price_usd - price_7d_ago) / price_7d_ago) * 100, 4) END AS price_change_pct_7d
        FROM prices
        """
    )

    return (
        comparison.selectExpr(*SILVER_COMPARISON_SELECT)
        .dropDuplicates(["asset_id", "observed_at", "correlation_bucket"])
    )


def write_silver_changes(
    spark: Any,
    config: SilverPipelineConfig,
) -> int:
    dataframe = build_silver_changes_dataframe(spark, config)
    dataframe.write.mode("append").format("delta").saveAsTable(config.changes_full_table)
    return spark.table(config.changes_full_table).count()


def write_silver_dominance(
    spark: Any,
    config: SilverPipelineConfig,
) -> int:
    dataframe = build_silver_dominance_dataframe(spark, config)
    dataframe.write.mode("append").format("delta").saveAsTable(config.dominance_full_table)
    return spark.table(config.dominance_full_table).count()


def write_silver_comparison(
    spark: Any,
    config: SilverPipelineConfig,
) -> int:
    dataframe = build_silver_comparison_dataframe(spark, config)
    dataframe.write.mode("append").format("delta").saveAsTable(config.comparison_full_table)
    return spark.table(config.comparison_full_table).count()


def parse_payload(payload_json: str | None, payload_path: str | None = None) -> list[dict[str, Any]]:
    if payload_json:
        data = json.loads(payload_json)
    elif payload_path:
        with open(payload_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = []

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("Silver payload must be a JSON object or an array of JSON objects.")
    return [dict(item) for item in data]


def main(
    spark: Any,
    payload_json: str | None = None,
    payload_path: str | None = None,
    config: SilverPipelineConfig | None = None,
) -> SilverPipelineResult:
    active_config = config or load_pipeline_config_from_env()

    if payload_json or payload_path:
        rows = parse_payload(payload_json, payload_path=payload_path)
        spark.createDataFrame(rows).createOrReplaceTempView("_silver_pipeline_payload")

    changes_count = write_silver_changes(spark, active_config)
    dominance_count = write_silver_dominance(spark, active_config)
    comparison_count = write_silver_comparison(spark, active_config)

    return SilverPipelineResult(
        changes_rows_written=changes_count,
        dominance_rows_written=dominance_count,
        comparison_rows_written=comparison_count,
        changes_target_table=active_config.changes_full_table,
        dominance_target_table=active_config.dominance_full_table,
        comparison_target_table=active_config.comparison_full_table,
    )


def parse_runtime_args(argv: list[str]) -> dict[str, str | None]:
    parsed: dict[str, str | None] = {
        "payload_json": None,
        "payload_path": None,
        "target_catalog": None,
        "target_env": None,
    }
    index = 0
    while index < len(argv):
        current = argv[index]
        if current == "--payload-json" and index + 1 < len(argv):
            parsed["payload_json"] = argv[index + 1]
            index += 2
            continue
        if current == "--payload-path" and index + 1 < len(argv):
            parsed["payload_path"] = argv[index + 1]
            index += 2
            continue
        if current == "--target-catalog" and index + 1 < len(argv):
            parsed["target_catalog"] = argv[index + 1]
            index += 2
            continue
        if current == "--target-env" and index + 1 < len(argv):
            parsed["target_env"] = argv[index + 1]
            index += 2
            continue
        index += 1
    return parsed


def _coerce_required_decimal(value: Any, field_name: str) -> float:
    if value is None:
        raise ValueError(f"Required decimal field '{field_name}' is missing.")
    return float(value)


def _coerce_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover - Databricks runtime entrypoint only
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    widgets: dict[str, str | None] = {}
    for widget_name in ("payload_json", "payload_path", "target_catalog", "target_env"):
        try:
            widgets[widget_name] = dbutils.widgets.get(widget_name)  # type: ignore[name-defined]
        except Exception:  # pragma: no cover - Databricks widget fallback
            widgets[widget_name] = None

    runtime_args = parse_runtime_args(sys.argv[1:])

    resolved_catalog = (
        widgets.get("target_catalog")
        or runtime_args.get("target_catalog")
        or os.environ.get("SILVER_TARGET_CATALOG", DEFAULT_CATALOG)
    )
    resolved_env = (
        widgets.get("target_env")
        or runtime_args.get("target_env")
        or os.environ.get("SILVER_TARGET_ENV", DEFAULT_CATALOG)
    )

    run_config = SilverPipelineConfig(
        target_catalog=resolved_catalog,
        target_env=resolved_env,
        silver_schema=os.environ.get("SILVER_SCHEMA", DEFAULT_SILVER_SCHEMA),
        bronze_schema=os.environ.get("BRONZE_SCHEMA", DEFAULT_BRONZE_SCHEMA),
        bronze_table=os.environ.get("BRONZE_TABLE", DEFAULT_BRONZE_TABLE),
    )

    result = main(
        spark_session,
        payload_json=widgets.get("payload_json") or runtime_args.get("payload_json"),
        payload_path=widgets.get("payload_path") or runtime_args.get("payload_path"),
        config=run_config,
    )

    print(
        json.dumps(
            {
                "changes_rows_written": result.changes_rows_written,
                "dominance_rows_written": result.dominance_rows_written,
                "comparison_rows_written": result.comparison_rows_written,
                "changes_target_table": result.changes_target_table,
                "dominance_target_table": result.dominance_target_table,
                "comparison_target_table": result.comparison_target_table,
            }
        )
    )
