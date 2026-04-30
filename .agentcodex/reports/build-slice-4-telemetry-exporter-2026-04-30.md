# Build Slice 4 Telemetry Exporter Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `copilot telemetry exporter`

## Delivered

- added `build_databricks_usage_row` in `backend/copilot_mvp.py`
- aligned the export shape with `contracts/usage_event.schema.json`
- updated `backend/copilot_mvp.md` to document the Databricks landing row path
- added a unit test for the landing-table export shape

## Verification

- the backend can produce a Databricks-ready telemetry row from the copilot response flow
- the exported row only contains the observability fields expected by the landing table
- the route remains explicit and still routes structured questions to Genie

## Remaining Work

- wire the exporter to a real Databricks client or ingestion job
- add a dashboard or notebook to inspect the landing table and readiness views
- propagate the same row builder to dashboard and internal-app events when those flows exist
