from __future__ import annotations

from pathlib import Path


EXPECTED_BRONZE_OBJECTS = {
    "bronze_market_snapshots": "CREATE OR REPLACE TABLE cgadev.market_bronze.bronze_market_snapshots",
}

EXPECTED_SILVER_SNAPSHOT_OBJECTS = {
    "silver_market_snapshots": "CREATE OR REPLACE VIEW cgadev.market_silver.silver_market_snapshots AS",
}

EXPECTED_SILVER_TABLE_OBJECTS = {
    "silver_market_changes": "CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_market_changes",
    "silver_market_dominance": "CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_market_dominance",
    "silver_cross_asset_comparison": "CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_cross_asset_comparison",
}

EXPECTED_GOLD_OBJECTS = {
    "gold_market_rankings": "CREATE OR REPLACE VIEW cgadev.market_gold.gold_market_rankings AS",
    "gold_top_movers": "CREATE OR REPLACE VIEW cgadev.market_gold.gold_top_movers AS",
    "gold_market_dominance": "CREATE OR REPLACE VIEW cgadev.market_gold.gold_market_dominance AS",
    "gold_cross_asset_comparison": "CREATE OR REPLACE VIEW cgadev.market_gold.gold_cross_asset_comparison AS",
}

EXPECTED_METRIC_VIEWS = {
    "mv_market_rankings": "source: cgadev.market_gold.gold_market_rankings",
    "mv_top_movers": "source: cgadev.market_gold.gold_top_movers",
    "mv_market_dominance": "source: cgadev.market_gold.gold_market_dominance",
    "mv_cross_asset_compare": "source: cgadev.market_gold.gold_cross_asset_comparison",
}


def validate_market_overview_chain(root_dir: str | Path | None = None) -> list[str]:
    base_dir = Path(root_dir) if root_dir is not None else Path(__file__).resolve().parent
    errors: list[str] = []

    bronze_migration_sql = _read(base_dir / "bronze_market_table_migration.sql")
    bronze_silver_sql = _read(base_dir / "bronze_silver_market_foundation.sql")
    silver_migration_sql = _read(base_dir / "silver_market_migration.sql")
    gold_sql = _read(base_dir / "gold_market_views.sql")
    metric_sql = _read(base_dir / "genie_metric_views.sql")
    lineage_map = _read(base_dir / "unity-catalog-lineage-map.md")
    market_job = _read(base_dir / "market_source_ingestion_job.py")
    silver_pipeline_job = _read(base_dir / "silver_market_pipeline_job.py")

    for object_name, signature in EXPECTED_BRONZE_OBJECTS.items():
        if signature not in bronze_migration_sql:
            errors.append(f"missing Bronze object definition: {object_name}")

    for object_name, signature in EXPECTED_SILVER_SNAPSHOT_OBJECTS.items():
        if signature not in bronze_silver_sql:
            errors.append(f"missing Silver object definition: {object_name}")

    for object_name, signature in EXPECTED_SILVER_TABLE_OBJECTS.items():
        if signature not in silver_migration_sql:
            errors.append(f"missing Silver object definition: {object_name}")

    for object_name, signature in EXPECTED_GOLD_OBJECTS.items():
        if signature not in gold_sql:
            errors.append(f"missing Gold object definition: {object_name}")

    for metric_name, signature in EXPECTED_METRIC_VIEWS.items():
        if f"CREATE OR REPLACE VIEW {metric_name}" not in metric_sql:
            errors.append(f"missing metric view definition: {metric_name}")
        if signature not in metric_sql:
            errors.append(f"metric view source mismatch for: {metric_name}")

    dependency_checks = (
        ("silver_market_snapshots", "FROM cgadev.market_bronze.bronze_market_snapshots", bronze_silver_sql),
        ("gold_market_rankings", "FROM cgadev.market_bronze.bronze_market_snapshots", gold_sql),
        ("gold_top_movers", "FROM cgadev.market_silver.silver_market_changes", gold_sql),
        ("gold_market_dominance", "FROM cgadev.market_silver.silver_market_dominance", gold_sql),
        ("gold_cross_asset_comparison", "FROM cgadev.market_silver.silver_cross_asset_comparison", gold_sql),
    )
    for object_name, dependency, source_text in dependency_checks:
        if dependency not in source_text:
            errors.append(f"missing dependency {dependency} for {object_name}")

    lineage_expectations = (
        "`CoinGecko API`",
        "`market_bronze.bronze_market_snapshots`",
        "`market_silver.silver_market_snapshots`",
        "`market_gold.gold_market_rankings`",
        "`ai_serving.mv_market_rankings`",
    )
    for marker in lineage_expectations:
        if marker not in lineage_map:
            errors.append(f"lineage map missing marker: {marker}")

    if 'target_table: str = "bronze_market_snapshots"' not in market_job:
        errors.append("market source ingestion job must target bronze_market_snapshots by default")

    if 'DEFAULT_BRONZE_TABLE = "bronze_market_snapshots"' not in silver_pipeline_job:
        errors.append("silver pipeline job must read from bronze_market_snapshots by default")

    return errors


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors = validate_market_overview_chain()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Market overview chain validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
