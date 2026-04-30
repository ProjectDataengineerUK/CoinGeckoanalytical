# Bundle Run Ingestion Job

## Purpose

Append normalized Databricks bundle/job run results into the governed landing table `ops_bundle_runs`.

## Implementation Asset

- executable job: `bundle_run_ingestion_job.py`

## Inputs

- `payload_json`: inline JSON object or array of bundle run rows
- `payload_path`: path to a JSON file containing bundle run rows
- `target_table`: target Delta table, defaulting to `ops_bundle_runs`

## Behavior

- parses one row or many rows
- validates the required bundle run fields
- rejects unsupported run status values
- coerces duration into a stable numeric type
- appends normalized rows to the target Delta table

## Runtime Shape

- designed for Databricks Jobs / serverless execution
- uses batch append only
- no cluster management code

## Next Step

- connect the job to real Databricks job run results or a staging file handoff
- add this job to the bundle manifest and schedule/trigger model
