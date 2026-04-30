# Build Slice 5 Telemetry Ingestion Job Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `telemetry ingestion job`

## Delivered

- created `databricks/ops_usage_ingestion_job.py`
- created `databricks/ops_usage_ingestion_job.md`
- added `databricks/test_ops_usage_ingestion_job.py`
- updated `databricks/README.md` to index the ingestion job

## Verification

- the job parses single-row and multi-row JSON payloads
- required telemetry fields are validated before write
- route and response values are constrained to the governed telemetry schema
- local unit tests pass for parsing, coercion, and invalid-route rejection

## Remaining Work

- connect the job to a real Databricks job schedule or landing handoff
- add a retry / dead-letter policy for malformed telemetry payloads
- wire the backend to emit the payload into the job input path
