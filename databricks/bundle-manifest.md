# Databricks Bundle Manifest

## Purpose

Package the Databricks-side jobs as a deployable bundle with scheduled ingestion and refresh.

## Bundle Root

- `databricks/databricks.yml`

## Resources

### `ops_usage_ingestion_job`

- schedule: every 5 minutes
- task: `ops_usage_ingestion_job.py`
- purpose: ingest the backend telemetry handoff file into `ops_usage_events`

### `ops_readiness_refresh_job`

- schedule: every 15 minutes
- task: `ops_readiness_refresh_job.py`
- purpose: refresh telemetry observability and readiness views

## Deployment Notes

- bundle is serverless-friendly and avoids cluster lifecycle management
- deployment should run against a dev target first
- ingestion should remain ahead of refresh in the operational cadence

## Next Step

- validate the bundle with the Databricks CLI
- deploy to a dev workspace target
- connect alerts to failed schedule runs and stale readiness views
