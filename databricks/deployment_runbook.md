# Databricks Deployment Runbook

## Purpose

Deploy the Databricks bundle safely from the repository into a dev workspace target, then promote to the next environment only after validation.

## Prerequisites

- Databricks CLI installed and authenticated
- workspace with Unity Catalog enabled
- dev target configured in `databricks/databricks.yml`
- `DATABRICKS_HOST` and `DATABRICKS_TOKEN` available for deploy execution
- `DATABRICKS_SQL_WAREHOUSE_ID` available when running live SQL validation through the Statement Execution API

## Local Preflight

Run from the bundle root:

```bash
cd /home/user/Projetos/CoinGeckoanalytical/databricks
python3 validate_bundle.py
python3 preflight_databricks_deploy.py
```

If the Databricks CLI is available, run:

```bash
databricks bundle validate
```

## Deploy Order

1. Validate the bundle locally.
2. Validate the bundle with the Databricks CLI.
3. Deploy to `dev`.
4. If the Bronze table already exists with legacy numeric types, run `bronze_market_table_migration_job` once in `dev`.
5. Run `market_source_ingestion_job` once with the market fixture payload.
6. Run `ops_usage_ingestion_job` once with a test payload.
7. Run `ops_bundle_run_ingestion_job` once with a test payload.
8. Run `ops_sentinela_alert_ingestion_job` once with a test payload.
9. Run `ops_readiness_refresh_job`.
10. Inspect `ops_ready_overview`, `ops_bundle_run_status`, and `ops_sentinela_alert_status`.

## Commands

```bash
export DATABRICKS_HOST="https://<workspace-host>"
export DATABRICKS_TOKEN="<token>"
export DATABRICKS_SQL_WAREHOUSE_ID="<sql-warehouse-id>"

cd /home/user/Projetos/CoinGeckoanalytical/databricks
python3 validate_bundle.py
python3 preflight_databricks_deploy.py
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run bronze_market_table_migration_job -t dev
databricks bundle run market_source_ingestion_job -t dev
databricks bundle run ops_usage_ingestion_job -t dev
databricks bundle run ops_bundle_run_ingestion_job -t dev
databricks bundle run ops_sentinela_alert_ingestion_job -t dev
databricks bundle run ops_readiness_refresh_job -t dev
```

## Fixture Inputs

Use these repo-local payloads for the first live smoke:

- market source fixture: `databricks/fixtures/market_source_sample.json`
- usage telemetry handoff: generate with `backend/telemetry_handoff.py` when needed
- bundle run handoff: generate with `backend/bundle_run_handoff.py` when needed
- sentinela alert handoff: generate with `backend/sentinela_alert_handoff.py` when needed

## Live Validation Checklist

1. Confirm `DATABRICKS_HOST` and `DATABRICKS_TOKEN` are set.
2. Confirm `DATABRICKS_SQL_WAREHOUSE_ID` is set when the SQL checks will run through automation.
3. Confirm the CLI can authenticate to the target workspace.
4. Validate and deploy the bundle to `dev`.
5. Run `bronze_market_table_migration_job` if the Bronze table uses a legacy schema.
6. Run `market_source_ingestion_job` with the market fixture payload.
7. Verify rows landed in `cgadev.market_bronze.bronze_market_snapshots`.
8. Verify dependent Silver views resolve and return rows.
9. Verify dependent Gold views resolve and return rows.
10. Verify Genie metric views resolve in `cgadev.ai_serving`.
11. Only after that run the operational ingestion and refresh jobs.
12. Record the exact row counts and timestamps in a live validation report.

## SQL Checks

Run these in Databricks SQL or a workspace notebook against `cgadev`:

```sql
SELECT COUNT(*) AS bronze_rows
FROM cgadev.market_bronze.bronze_market_snapshots;

SELECT MAX(observed_at) AS bronze_latest_observed_at
FROM cgadev.market_bronze.bronze_market_snapshots;

SELECT COUNT(*) AS silver_snapshot_rows
FROM cgadev.market_silver.silver_market_snapshots;

SELECT COUNT(*) AS silver_changes_rows
FROM cgadev.market_silver.silver_market_changes;

SELECT COUNT(*) AS silver_dominance_rows
FROM cgadev.market_silver.silver_market_dominance;

SELECT COUNT(*) AS silver_comparison_rows
FROM cgadev.market_silver.silver_cross_asset_comparison;

SELECT COUNT(*) AS gold_rankings_rows
FROM cgadev.market_gold.gold_market_rankings;

SELECT COUNT(*) AS gold_movers_rows
FROM cgadev.market_gold.gold_top_movers;

SELECT COUNT(*) AS gold_dominance_rows
FROM cgadev.market_gold.gold_market_dominance;

SELECT COUNT(*) AS gold_comparison_rows
FROM cgadev.market_gold.gold_cross_asset_comparison;

SELECT COUNT(*) AS mv_rankings_rows
FROM cgadev.ai_serving.mv_market_rankings;

SELECT COUNT(*) AS mv_movers_rows
FROM cgadev.ai_serving.mv_top_movers;

SELECT COUNT(*) AS mv_dominance_rows
FROM cgadev.ai_serving.mv_market_dominance;

SELECT COUNT(*) AS mv_compare_rows
FROM cgadev.ai_serving.mv_cross_asset_compare;
```

## Acceptance Rule For Data Plane

Treat the `market overview intelligence` data plane as live-validated only when:

- Bronze contains fixture-derived rows
- all first-order Silver views resolve and return rows
- all first-order Gold views resolve and return rows
- Genie metric views resolve from the Gold assets
- the observed timestamps are coherent across Bronze and Gold
- the evidence is written into a dated report under `.agentcodex/reports/`

## Post-Deploy Checks

- `bronze_market_snapshots` receives rows from the market source fixture or handoff
- `ops_usage_events` receives rows
- `ops_bundle_runs` receives rows for bundle/job execution
- `ops_sentinela_alerts` receives rows for alert events
- `ops_bundle_run_readiness` returns `serve` for successful runs
- `ops_sentinela_alert_readiness` returns `ready` only when backlog is clear

## Rollback Notes

- pause the ingestion and refresh jobs before changing SQL views
- use the Bronze recreation script to reset the landing table if a legacy schema keeps blocking append operations
- revert the bundle definition before changing schedules
- keep backend handoff formats compatible with the active contracts

## Next Step

- wire the deployment runbook into CI or a release checklist when the workspace and CLI are available
- in GitHub Actions, add `DATABRICKS_SQL_WAREHOUSE_ID` as a secret to publish the `databricks-live-sql-validation` artifact after deploy
