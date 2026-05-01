# Databricks Bundle Manifest

## Purpose

Package the Databricks-side jobs as a deployable bundle with scheduled ingestion and refresh.

## Bundle Root

- `databricks/databricks.yml`

## Resources

The scheduled production jobs use `spark_python_task` for testable CI/CD. Thin notebooks also exist under `databricks/notebooks/` for Databricks workspace execution and review.

### `market_source_ingestion_job`

- schedule: every 5 minutes
- task: `market_source_ingestion_job.py`
- purpose: fetch CoinGecko `/coins/markets`, normalize rows, and append them into `bronze_market_snapshots`
- smoke behavior: CI can still pass an explicit fixture payload to keep deploy validation deterministic

### `ops_usage_ingestion_job`

- schedule: every 5 minutes
- task: `ops_usage_ingestion_job.py`
- purpose: ingest the backend telemetry handoff file into `ops_usage_events`

### `ops_readiness_refresh_job`

- schedule: every 15 minutes
- task: `ops_readiness_refresh_job.py`
- purpose: refresh telemetry observability and readiness views
- runtime safety: skips principal-management statements so deploy refresh is not blocked by missing placeholder groups such as `data_platform`

### `ops_bundle_run_ingestion_job`

- trigger: event-driven or on-demand handoff
- task: `bundle_run_ingestion_job.py`
- purpose: ingest normalized Databricks bundle/job run results into `ops_bundle_runs`
- failure handling: failed and cancelled runs are surfaced to Sentinela as release blockers

### `ops_sentinela_alert_ingestion_job`

- trigger: event-driven or on-demand handoff
- task: `sentinela_alert_ingestion_job.py`
- purpose: ingest normalized Sentinela alert events into `ops_sentinela_alerts`
- failure handling: alert delivery failures should be surfaced to ops readiness

## Deployment Notes

- bundle is serverless-friendly and avoids cluster lifecycle management
- deployment should run against a dev target first
- market source ingestion should remain ahead of Gold-serving validation and refresh
- ingestion should remain ahead of refresh in the operational cadence
- bundle run ingest should feed Sentinela before dashboard refresh and release checks

## Next Step

- validate the bundle with `python3 validate_bundle.py` in this repo, then with the Databricks CLI when available
- deploy to a dev workspace target
- connect alerts to failed schedule runs and stale readiness views

## Deployment Runbook

- use `deployment_runbook.md` for the ordered dev deployment flow
- it documents the preflight, deploy, verification, and rollback sequence

## Failure Signals

- ingestion or refresh failures are treated as release blockers
- bundle run events should be normalized using `contracts/bundle_run_event.schema.json`
- Sentinela should interpret failed bundle runs as `bundle_failure` or `bundle_cancelled` alerts

## Local Validation

When the Databricks CLI is not available, use:

```bash
cd /home/user/Projetos/CoinGeckoanalytical/databricks
python3 validate_bundle.py
```

Before attempting a live deploy, use:

```bash
cd /home/user/Projetos/CoinGeckoanalytical/databricks
python3 preflight_databricks_deploy.py
```

That preflight checks:

- `databricks` CLI availability
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`

When the Databricks CLI is available, use:

```bash
cd /home/user/Projetos/CoinGeckoanalytical/databricks
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run market_source_ingestion_job -t dev
databricks bundle run ops_usage_ingestion_job -t dev
databricks bundle run ops_readiness_refresh_job -t dev
```
