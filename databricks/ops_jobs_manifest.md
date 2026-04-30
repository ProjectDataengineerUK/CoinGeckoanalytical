# Ops Jobs Manifest

## Purpose

Document the scheduled Databricks jobs that keep telemetry and readiness current.

## Jobs

### `ops_usage_ingestion_job`

- frequency: every 5 minutes
- task: `ops_usage_ingestion_job.py`
- input: backend telemetry handoff file
- output: append to `ops_usage_events`

### `ops_readiness_refresh_job`

- frequency: every 15 minutes
- task: `ops_readiness_refresh_job.py`
- input: `telemetry-observability.sql` and `ops_readiness_dashboard.sql`
- output: refreshed views for dashboard consumption

## Ordering

- ingestion must complete before refresh
- dashboard queries read only from the refreshed views

## Failure Policy

- ingestion failures should block refresh
- refresh failures should page Sentinela with a hold status
- bundle or scheduled job failures should be surfaced to Sentinela as release blockers

## Next Step

- translate this manifest into the Databricks job scheduler or Asset Bundle when deployment wiring is introduced
