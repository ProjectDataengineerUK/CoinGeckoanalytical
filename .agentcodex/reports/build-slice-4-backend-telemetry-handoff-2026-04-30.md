# Build Slice 4 Backend Telemetry Handoff Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `backend telemetry handoff`

## Delivered

- created `backend/telemetry_handoff.py`
- created `backend/tests/test_telemetry_handoff.py`
- updated `backend/README.md` to document the handoff path
- updated `databricks/ops_usage_ingestion_job.md` to consume the handoff file

## Verification

- backend can emit a Databricks-ready JSON array file
- the emitted row reuses the same usage telemetry shape as the Databricks landing table
- the local tests pass for file creation and row shaping

## Remaining Work

- connect the file handoff to an actual scheduled job or service endpoint
- add retry and dead-letter handling for malformed payload files
- render the ops readiness dashboard against real ingested rows
