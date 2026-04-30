-- Sentinela Alert Observability Baseline
-- Purpose: land normalized Sentinela alert events and expose a backlog view
-- for operations, dashboards, and notification routing.

CREATE TABLE IF NOT EXISTS ops_sentinela_alerts (
  kind STRING,
  message STRING,
  request_id STRING,
  tenant_id STRING,
  route_selected STRING,
  job_name STRING,
  run_id STRING,
  escalation STRING,
  source STRING,
  created_at TIMESTAMP
)
USING DELTA
PARTITIONED BY (kind)
TBLPROPERTIES (
  delta.autoOptimize.optimizeWrite = true,
  delta.autoOptimize.autoCompact = true
);

CREATE OR REPLACE VIEW ops_sentinela_alerts_normalized AS
SELECT
  kind,
  message,
  request_id,
  tenant_id,
  route_selected,
  job_name,
  run_id,
  escalation,
  source,
  CAST(created_at AS TIMESTAMP) AS created_at,
  CASE
    WHEN kind IN ('bundle_failure', 'bundle_cancelled') THEN 'bundle'
    WHEN kind IN ('latency_breach', 'cost_anomaly', 'freshness_gap', 'token_spike', 'error_spike') THEN 'runtime'
    ELSE 'other'
  END AS alert_family
FROM ops_sentinela_alerts;

CREATE OR REPLACE VIEW ops_sentinela_alert_backlog AS
SELECT
  kind,
  alert_family,
  COUNT(*) AS alert_count,
  MAX(created_at) AS latest_created_at
FROM ops_sentinela_alerts_normalized
GROUP BY kind, alert_family;

CREATE OR REPLACE VIEW ops_sentinela_alert_readiness AS
SELECT
  CASE
    WHEN SUM(CASE WHEN kind IN ('bundle_failure', 'bundle_cancelled') THEN 1 ELSE 0 END) = 0
     AND SUM(CASE WHEN kind IN ('latency_breach', 'cost_anomaly', 'freshness_gap', 'token_spike', 'error_spike') THEN 1 ELSE 0 END) = 0
    THEN 'ready'
    ELSE 'hold'
  END AS sentinela_alert_status,
  COUNT(*) AS total_alerts,
  SUM(CASE WHEN alert_family = 'bundle' THEN 1 ELSE 0 END) AS bundle_alerts,
  SUM(CASE WHEN alert_family = 'runtime' THEN 1 ELSE 0 END) AS runtime_alerts
FROM ops_sentinela_alerts_normalized;
