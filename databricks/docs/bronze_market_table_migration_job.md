# Bronze Market Table Migration Job

## Purpose

Recreate the Bronze landing table with the canonical decimal schema when a workspace already contains a legacy table with incompatible numeric types.

## Executable

- `bronze_market_table_migration_job.py`

## SQL Asset

- `bronze_market_table_migration.sql`

## Behavior

- executes the migration SQL as a versioned Databricks job
- is intended for explicit operator-run execution in legacy workspaces
- is safe to deploy from Git without running automatically on every deploy

## Inputs

- none required at runtime beyond the Databricks Spark session

## Output

- the Bronze table is recreated with the canonical schema

## Operational Notes

- run only when the workspace Bronze table needs schema remediation
- do not schedule this job as a recurring task
- keep the migration before the first live market ingest in a legacy workspace
