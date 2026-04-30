# Dev Live Validation Checklist

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- target_environment: `dev`
- purpose: `move the first governed data family from repo-local validation to workspace execution evidence`

## Scope

This checklist is only for the first governed family:

- `market overview intelligence`

It validates:

1. source-ingestion execution
2. Bronze landing
3. Silver row presence
4. Gold row presence
5. Genie metric-view resolution
6. operational jobs only after the data chain is live

## Prerequisites

- Databricks CLI installed
- `DATABRICKS_HOST` configured
- `DATABRICKS_TOKEN` configured
- `DATABRICKS_SQL_WAREHOUSE_ID` configured for automated live SQL validation
- Unity Catalog enabled workspace
- `dev` target configured for the bundle
- expected catalog: `cgadev`

## Execution Order

1. Run local preflight and bundle validation.
2. Run Databricks CLI bundle validation.
3. Deploy bundle to `dev`.
4. Run `market_source_ingestion_job`.
5. Verify `cgadev.market_bronze.bronze_market_snapshots`.
6. Verify dependent Silver views.
7. Verify dependent Gold views.
8. Verify dependent Genie metric views.
9. Run operational ingestion jobs.
10. Run readiness refresh.
11. Save row counts, timestamps, and any failures to a dated live-validation report.

## Required Commands

```bash
export DATABRICKS_HOST="https://<workspace-host>"
export DATABRICKS_TOKEN="<token>"
export DATABRICKS_SQL_WAREHOUSE_ID="<sql-warehouse-id>"

cd /home/user/Projetos/CoinGeckoanalytical/databricks
python3 validate_bundle.py
python3 preflight_databricks_deploy.py
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run market_source_ingestion_job -t dev
databricks bundle run ops_usage_ingestion_job -t dev
databricks bundle run ops_bundle_run_ingestion_job -t dev
databricks bundle run ops_sentinela_alert_ingestion_job -t dev
databricks bundle run ops_readiness_refresh_job -t dev
```

## Required SQL Checks

```sql
SELECT COUNT(*) AS bronze_rows FROM cgadev.market_bronze.bronze_market_snapshots;
SELECT COUNT(*) AS silver_snapshot_rows FROM cgadev.market_silver.silver_market_snapshots;
SELECT COUNT(*) AS silver_changes_rows FROM cgadev.market_silver.silver_market_changes;
SELECT COUNT(*) AS silver_dominance_rows FROM cgadev.market_silver.silver_market_dominance;
SELECT COUNT(*) AS silver_comparison_rows FROM cgadev.market_silver.silver_cross_asset_comparison;
SELECT COUNT(*) AS gold_rankings_rows FROM cgadev.market_gold.gold_market_rankings;
SELECT COUNT(*) AS gold_movers_rows FROM cgadev.market_gold.gold_top_movers;
SELECT COUNT(*) AS gold_dominance_rows FROM cgadev.market_gold.gold_market_dominance;
SELECT COUNT(*) AS gold_comparison_rows FROM cgadev.market_gold.gold_cross_asset_comparison;
SELECT COUNT(*) AS mv_rankings_rows FROM cgadev.ai_serving.mv_market_rankings;
SELECT COUNT(*) AS mv_movers_rows FROM cgadev.ai_serving.mv_top_movers;
SELECT COUNT(*) AS mv_dominance_rows FROM cgadev.ai_serving.mv_market_dominance;
SELECT COUNT(*) AS mv_compare_rows FROM cgadev.ai_serving.mv_cross_asset_compare;
```

## Expected Outcome

- the first governed data family is no longer only repo-local
- the project gains real evidence that `dashboard`, `Genie`, and `copilot` can consume governed assets later
- a live-validation report becomes the gating artifact before any dashboard delivery claim
- when executed through GitHub Actions with the warehouse secret present, the workflow uploads `databricks-live-sql-validation`
