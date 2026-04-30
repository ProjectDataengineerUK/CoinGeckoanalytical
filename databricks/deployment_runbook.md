# Databricks Deployment Runbook

## Purpose

Deploy the Databricks bundle safely from the repository into a dev workspace target, then promote to the next environment only after validation.

## Prerequisites

- Databricks CLI installed and authenticated
- workspace with Unity Catalog enabled
- dev target configured in `databricks/databricks.yml`

## Local Preflight

Run from the bundle root:

```bash
cd /home/user/Projetos/CoinGeckoanalytical/databricks
python3 validate_bundle.py
```

If the Databricks CLI is available, run:

```bash
databricks bundle validate
```

## Deploy Order

1. Validate the bundle locally.
2. Validate the bundle with the Databricks CLI.
3. Deploy to `dev`.
4. Run `ops_usage_ingestion_job` once with a test payload.
5. Run `ops_bundle_run_ingestion_job` once with a test payload.
6. Run `ops_sentinela_alert_ingestion_job` once with a test payload.
7. Run `ops_readiness_refresh_job`.
8. Inspect `ops_ready_overview`, `ops_bundle_run_status`, and `ops_sentinela_alert_status`.

## Commands

```bash
databricks bundle deploy -t dev
databricks bundle run ops_usage_ingestion_job -t dev
databricks bundle run ops_bundle_run_ingestion_job -t dev
databricks bundle run ops_sentinela_alert_ingestion_job -t dev
databricks bundle run ops_readiness_refresh_job -t dev
```

## Post-Deploy Checks

- `ops_usage_events` receives rows
- `ops_bundle_runs` receives rows for bundle/job execution
- `ops_sentinela_alerts` receives rows for alert events
- `ops_bundle_run_readiness` returns `serve` for successful runs
- `ops_sentinela_alert_readiness` returns `ready` only when backlog is clear

## Rollback Notes

- pause the ingestion and refresh jobs before changing SQL views
- revert the bundle definition before changing schedules
- keep backend handoff formats compatible with the active contracts

## Next Step

- wire the deployment runbook into CI or a release checklist when the workspace and CLI are available
