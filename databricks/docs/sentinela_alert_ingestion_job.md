# Sentinela Alert Ingestion Job

## Purpose

Append normalized Sentinela alert events into the governed landing table `ops_sentinela_alerts`.

## Implementation Asset

- executable job: `sentinela_alert_ingestion_job.py`

## Inputs

- `payload_json`: inline JSON object or array of alert rows
- `payload_path`: path to a JSON file containing alert rows
- `target_table`: target Delta table, defaulting to `ops_sentinela_alerts`

## Behavior

- parses one row or many rows
- validates required alert fields
- rejects unsupported alert kinds
- appends normalized rows to the target Delta table

## Runtime Shape

- designed for Databricks Jobs / serverless execution
- uses batch append only
- no cluster management code

## Next Step

- connect the job to Sentinela alert handoff files or a staging queue
- add the alert landing table to the ops readiness dashboard
