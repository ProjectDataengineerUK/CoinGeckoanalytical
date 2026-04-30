-- Databricks Ops Readiness Dashboard Surface
-- Purpose: notebook/dashboard-friendly queries over telemetry observability
-- and Gold serving readiness.

CREATE OR REPLACE VIEW ops_ready_overview AS
SELECT
  COUNT(*) AS route_rows,
  SUM(CASE WHEN readiness_status = 'ready' THEN 1 ELSE 0 END) AS ready_routes,
  SUM(CASE WHEN readiness_status = 'hold' THEN 1 ELSE 0 END) AS hold_routes,
  SUM(event_count) AS total_events,
  SUM(error_count) AS total_errors,
  SUM(total_cost_estimate) AS total_cost_estimate,
  MAX(max_latency_ms) AS peak_latency_ms,
  SUM(stale_freshness_count) AS stale_freshness_count
FROM ops_release_readiness;

CREATE OR REPLACE VIEW ops_route_readiness_latest AS
WITH latest_per_route AS (
  SELECT
    route_selected,
    readiness_status,
    hour_bucket,
    event_count,
    success_count,
    partial_count,
    refused_count,
    error_count,
    max_latency_ms,
    avg_latency_ms,
    total_tokens,
    total_cost_estimate,
    stale_freshness_count,
    policy_max_latency_ms,
    policy_max_cost_estimate,
    policy_max_total_tokens,
    ROW_NUMBER() OVER (
      PARTITION BY route_selected
      ORDER BY hour_bucket DESC
    ) AS row_number
  FROM ops_release_readiness
)
SELECT
  route_selected,
  readiness_status,
  hour_bucket,
  event_count,
  success_count,
  partial_count,
  refused_count,
  error_count,
  max_latency_ms,
  avg_latency_ms,
  total_tokens,
  total_cost_estimate,
  stale_freshness_count,
  policy_max_latency_ms,
  policy_max_cost_estimate,
  policy_max_total_tokens
FROM latest_per_route
WHERE row_number = 1;

CREATE OR REPLACE VIEW ops_alert_backlog AS
SELECT
  alert_kind,
  route_selected,
  COUNT(*) AS alert_count,
  MAX(event_time) AS latest_event_time
FROM ops_alert_queue
GROUP BY alert_kind, route_selected
ORDER BY alert_count DESC, latest_event_time DESC;

CREATE OR REPLACE VIEW ops_cost_latency_trend AS
SELECT
  route_selected,
  hour_bucket,
  SUM(event_count) AS event_count,
  AVG(avg_latency_ms) AS avg_latency_ms,
  MAX(max_latency_ms) AS max_latency_ms,
  SUM(total_cost_estimate) AS total_cost_estimate,
  SUM(stale_freshness_count) AS stale_freshness_count
FROM ops_release_readiness
GROUP BY route_selected, hour_bucket
ORDER BY hour_bucket DESC, route_selected;

CREATE OR REPLACE VIEW ops_bundle_run_status AS
SELECT
  job_name,
  bundle_readiness_status,
  run_count,
  success_count,
  failed_count,
  cancelled_count,
  running_count,
  latest_update_time,
  max_duration_ms,
  avg_duration_ms,
  latest_run_id,
  latest_status,
  latest_result_state,
  latest_run_state,
  serving_status
FROM ops_bundle_run_readiness;

SELECT * FROM ops_ready_overview;
SELECT * FROM ops_route_readiness_latest;
SELECT * FROM ops_alert_backlog;
SELECT * FROM ops_cost_latency_trend;
SELECT * FROM ops_bundle_run_status;
