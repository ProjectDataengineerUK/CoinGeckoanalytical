# Ops Readiness Refresh Job

## Purpose

Recreate the telemetry observability and readiness views on a schedule so the dashboard always reads the latest governed definitions.

## Implementation Asset

- executable job: `ops_readiness_refresh_job.py`

## Behavior

- loads the runtime-safe Unity Catalog foundation SQL before view refresh
- loads `telemetry-observability.sql`
- loads `ops_readiness_dashboard.sql`
- executes each SQL statement in order
- skips principal-management statements such as `ALTER ... OWNER`, `GRANT`, and `REVOKE` if they are accidentally present in a runtime refresh file
- keeps the refresh logic separate from ingestion

## Runtime Shape

- designed for Databricks Jobs / serverless execution
- uses Spark SQL only
- no cluster lifecycle code or notebook dependency
- does not require workspace groups such as `data_platform` to exist during the runtime refresh path

## Next Step

- schedule this job after telemetry ingestion
- connect dashboard refresh alerts to the job outcome
