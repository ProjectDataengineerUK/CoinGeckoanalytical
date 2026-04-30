# Ops Usage Ingestion Job

## Purpose

Append normalized usage telemetry into the governed Databricks landing table `ops_usage_events`.

## Implementation Asset

- executable job: `ops_usage_ingestion_job.py`

## Inputs

- `payload_json`: inline JSON object or array of telemetry rows
- `payload_path`: path to a JSON file containing telemetry rows
- `target_table`: target Delta table, defaulting to `ops_usage_events`

## Behavior

- parses one row or many rows
- validates the required usage telemetry fields
- rejects unsupported route or response values
- coerces numeric fields into stable types
- appends the normalized rows to the target Delta table

## Runtime Shape

- designed for Databricks Jobs / serverless execution
- uses batch append only
- does not manage clusters or streaming state

## Next Step

- connect the job to the real backend emission path or a staging file handoff
- add refresh scheduling and basic failure alerts in Databricks Jobs
