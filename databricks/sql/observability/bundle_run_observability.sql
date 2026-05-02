-- Databricks Bundle Run Observability Baseline
-- Purpose: land Databricks bundle/job run results and expose readiness views
-- that Sentinela and ops dashboards can consume.

CREATE TABLE IF NOT EXISTS cgadev.ops_observability.ops_bundle_runs (
  job_name STRING,
  run_id STRING,
  status STRING,
  result_state STRING,
  update_time TIMESTAMP,
  duration_ms INT
)
USING DELTA
PARTITIONED BY (job_name)
TBLPROPERTIES (
  delta.autoOptimize.optimizeWrite = true,
  delta.autoOptimize.autoCompact = true
);

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_bundle_runs_normalized AS
SELECT
  job_name,
  run_id,
  UPPER(status) AS status,
  UPPER(result_state) AS result_state,
  CAST(update_time AS TIMESTAMP) AS update_time,
  duration_ms,
  CASE
    WHEN UPPER(status) IN ('SUCCESS', 'SUCCEEDED', 'COMPLETED') THEN 'success'
    WHEN UPPER(status) IN ('RUNNING', 'QUEUED', 'PENDING') THEN 'running'
    WHEN UPPER(status) IN ('CANCELLED', 'CANCELED') THEN 'cancelled'
    ELSE 'failed'
  END AS run_state,
  CASE
    WHEN duration_ms IS NULL THEN 'unknown'
    WHEN duration_ms < 1000 THEN 'fast'
    WHEN duration_ms < 10000 THEN 'normal'
    ELSE 'slow'
  END AS duration_band
FROM cgadev.ops_observability.ops_bundle_runs;

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_bundle_run_health AS
SELECT
  job_name,
  COUNT(*) AS run_count,
  SUM(CASE WHEN run_state = 'success' THEN 1 ELSE 0 END) AS success_count,
  SUM(CASE WHEN run_state = 'failed' THEN 1 ELSE 0 END) AS failed_count,
  SUM(CASE WHEN run_state = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
  SUM(CASE WHEN run_state = 'running' THEN 1 ELSE 0 END) AS running_count,
  MAX(update_time) AS latest_update_time,
  MAX(duration_ms) AS max_duration_ms,
  AVG(duration_ms) AS avg_duration_ms,
  CASE
    WHEN SUM(CASE WHEN run_state IN ('failed', 'cancelled') THEN 1 ELSE 0 END) = 0
    THEN 'ready'
    ELSE 'hold'
  END AS bundle_readiness_status
FROM cgadev.ops_observability.ops_bundle_runs_normalized
GROUP BY job_name;

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_bundle_run_latest AS
WITH latest_per_job AS (
  SELECT
    job_name,
    run_id,
    status,
    result_state,
    update_time,
    duration_ms,
    run_state,
    duration_band,
    ROW_NUMBER() OVER (
      PARTITION BY job_name
      ORDER BY update_time DESC
    ) AS row_number
  FROM cgadev.ops_observability.ops_bundle_runs_normalized
)
SELECT
  job_name,
  run_id,
  status,
  result_state,
  update_time,
  duration_ms,
  run_state,
  duration_band
FROM latest_per_job
WHERE row_number = 1;

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_bundle_run_readiness AS
SELECT
  h.job_name,
  h.run_count,
  h.success_count,
  h.failed_count,
  h.cancelled_count,
  h.running_count,
  h.latest_update_time,
  h.max_duration_ms,
  h.avg_duration_ms,
  h.bundle_readiness_status,
  l.run_id AS latest_run_id,
  l.status AS latest_status,
  l.result_state AS latest_result_state,
  l.run_state AS latest_run_state,
  CASE
    WHEN h.bundle_readiness_status = 'ready' THEN 'serve'
    ELSE 'hold'
  END AS serving_status
FROM cgadev.ops_observability.ops_bundle_run_health h
LEFT JOIN cgadev.ops_observability.ops_bundle_run_latest l
  ON h.job_name = l.job_name;
