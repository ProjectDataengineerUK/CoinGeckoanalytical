from __future__ import annotations

import json
from pathlib import Path

EXPECTED_BRONZE_OBJECTS = {
    "bronze_defillama_protocols": "CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_defillama_protocols",
    "bronze_github_activity":     "CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_github_activity",
    "bronze_fred_macro":          "CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_fred_macro",
}

EXPECTED_SILVER_OBJECTS = {
    "silver_asset_enriched": "CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_asset_enriched",
    "silver_macro_context":  "CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_macro_context",
}

EXPECTED_GOLD_OBJECTS = {
    "gold_enriched_rankings": "CREATE OR REPLACE VIEW cgadev.market_gold.gold_enriched_rankings AS",
    "gold_defi_protocols":    "CREATE OR REPLACE VIEW cgadev.market_gold.gold_defi_protocols AS",
    "gold_macro_regime":      "CREATE OR REPLACE VIEW cgadev.market_gold.gold_macro_regime AS",
}

EXPECTED_METRIC_VIEWS = {
    "mv_enriched_rankings": "FROM cgadev.market_gold.gold_enriched_rankings",
    "mv_defi_protocols":    "FROM cgadev.market_gold.gold_defi_protocols",
    "mv_macro_regime":      "FROM cgadev.market_gold.gold_macro_regime",
}


def validate_enrichment_chain(root_dir: str | Path | None = None) -> list[str]:
    base_dir = Path(root_dir) if root_dir is not None else Path(__file__).resolve().parent.parent
    errors: list[str] = []

    bronze_migration_sql = _read(base_dir / "sql/migrations/bronze_enrichment_migration.sql")
    silver_migration_sql  = _read(base_dir / "sql/migrations/silver_enrichment_migration.sql")
    gold_sql              = _read(base_dir / "sql/layers/gold_market_views.sql")
    metric_sql            = _read(base_dir / "sql/layers/genie_metric_views.sql")
    defillama_job         = _read(base_dir / "jobs/defillama_ingestion_job.py")
    repo_map_path         = base_dir / "config/github_asset_repo_map.json"

    for name, signature in EXPECTED_BRONZE_OBJECTS.items():
        if signature not in bronze_migration_sql:
            errors.append(f"missing Bronze object definition: {name}")

    for name, signature in EXPECTED_SILVER_OBJECTS.items():
        if signature not in silver_migration_sql:
            errors.append(f"missing Silver object definition: {name}")

    for name, signature in EXPECTED_GOLD_OBJECTS.items():
        if signature not in gold_sql:
            errors.append(f"missing Gold view definition: {name}")

    for metric_name, source_signature in EXPECTED_METRIC_VIEWS.items():
        if f"cgadev.ai_serving.{metric_name}" not in metric_sql:
            errors.append(f"missing metric view definition: {metric_name}")
        if source_signature not in metric_sql:
            errors.append(f"metric view source mismatch for: {metric_name}")

    if 'DEFAULT_TARGET_TABLE = "cgadev.market_bronze.bronze_defillama_protocols"' not in defillama_job:
        errors.append("defillama ingestion job must target cgadev.market_bronze.bronze_defillama_protocols by default")

    if not repo_map_path.exists():
        errors.append("github_asset_repo_map.json not found")
    else:
        try:
            repo_map = json.loads(repo_map_path.read_text(encoding="utf-8"))
            if not isinstance(repo_map, list) or len(repo_map) < 10:
                errors.append("github_asset_repo_map.json must contain at least 10 entries")
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"github_asset_repo_map.json is invalid: {exc}")

    return errors


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors = validate_enrichment_chain()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Enrichment chain validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
