# Ops Jobs Manifest

## Purpose

Document the scheduled Databricks jobs that keep telemetry and readiness current.

## Jobs

### `market_source_ingestion_job`

- frequency: every 5 minutes
- task: `market_source_ingestion_job.py`
- input: source payload handoff for CoinGecko-style market rows
- output: append to `bronze_market_snapshots`

### `ops_usage_ingestion_job`

- frequency: every 5 minutes
- task: `ops_usage_ingestion_job.py`
- input: backend telemetry handoff file
- output: append to `ops_usage_events`

### `ops_readiness_refresh_job`

- frequency: every 15 minutes
- task: `ops_readiness_refresh_job.py`
- input: runtime-safe Unity Catalog foundation SQL, telemetry observability SQL, market readiness SQL, and dashboard readiness SQL
- output: refreshed views for dashboard consumption
- safety: skips ownership and grant statements if they are accidentally present in the runtime refresh path

### `ops_bundle_run_observability`

- frequency: on every bundle or job run result ingest
- task: `bundle_run_observability.sql`
- input: normalized bundle run result records
- output: `ops_bundle_runs` and readiness views

### `ops_bundle_run_ingestion_job`

- trigger: event-driven or on-demand
- task: `bundle_run_ingestion_job.py`
- input: backend or workspace handoff file containing bundle run records
- output: append to `ops_bundle_runs`

### `ops_sentinela_alert_ingestion_job`

- trigger: event-driven or on-demand
- task: `sentinela_alert_ingestion_job.py`
- input: backend or workspace handoff file containing Sentinela alerts
- output: append to `ops_sentinela_alerts`

## Ordering

- market source ingestion must complete before Gold-serving routes are treated as real
- ingestion must complete before refresh
- dashboard queries read only from the refreshed views
- bundle run observability feeds the Sentinela release-blocker layer
- bundle run ingestion can trigger independently of the scheduled telemetry path
- Sentinela alerts should be ingested independently of bundle run results when they are emitted directly

## Failure Policy

- ingestion failures should block refresh
- refresh failures should page Sentinela with a hold status
- bundle or scheduled job failures should be surfaced to Sentinela as release blockers

## Next Step

- translate this manifest into the Databricks job scheduler or Asset Bundle when deployment wiring is introduced
