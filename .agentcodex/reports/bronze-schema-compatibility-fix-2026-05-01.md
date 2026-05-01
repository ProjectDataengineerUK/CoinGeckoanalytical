# Bronze Schema Compatibility Fix

- date: `2026-05-01`
- project: `CoinGeckoAnalytical`
- issue: `DELTA_MERGE_INCOMPATIBLE_DATATYPE on circulating_supply`

## Root Cause

The Databricks Bronze append path could hit an existing Delta table whose legacy schema used `DoubleType` for one or more numeric fields, while the current contract expects `DecimalType(38,8)`.

## Fix Applied

- updated `databricks/market_source_ingestion_job.py`
- added schema-alignment logic before `saveAsTable`
- added a regression test for legacy Bronze tables
- updated the job documentation to explain the fallback behavior

## Result

- local unit tests pass for both backend and Databricks layers
- the Bronze ingest job now adapts to a pre-existing table schema instead of failing on a type merge during append

## Follow-up

- if the workspace Bronze table was created with a legacy schema, run the approved migration or recreation path when safe so the runtime schema matches the current contract
