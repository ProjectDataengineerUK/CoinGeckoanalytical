-- Databricks Telemetry Observability Baseline
-- Purpose: normalize usage telemetry from Genie, copilot, dashboard API,
-- and internal ops surfaces into a governed Databricks view layer for
-- Sentinela, dashboards, and release-readiness analysis.

CREATE TABLE IF NOT EXISTS cgadev.ops_observability.ops_usage_events (
  event_time TIMESTAMP,
  request_id STRING,
  tenant_id STRING,
  user_id STRING,
  route_selected STRING,
  model_or_engine STRING,
  prompt_tokens INT,
  completion_tokens INT,
  total_tokens INT,
  latency_ms INT,
  cost_estimate DOUBLE,
  freshness_watermark STRING,
  response_status STRING
)
USING DELTA
PARTITIONED BY (tenant_id, route_selected)
TBLPROPERTIES (
  delta.autoOptimize.optimizeWrite = true,
  delta.autoOptimize.autoCompact = true
);

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_usage_events_normalized AS
SELECT
  CAST(event_time AS TIMESTAMP) AS event_time,
  request_id,
  tenant_id,
  user_id,
  route_selected,
  model_or_engine,
  prompt_tokens,
  completion_tokens,
  total_tokens,
  latency_ms,
  cost_estimate,
  freshness_watermark,
  response_status,
  date_trunc('HOUR', CAST(event_time AS TIMESTAMP)) AS hour_bucket,
  date_trunc('DAY', CAST(event_time AS TIMESTAMP)) AS day_bucket,
  CASE
    WHEN latency_ms >= 1000 THEN 'slow'
    WHEN latency_ms >= 500 THEN 'warm'
    ELSE 'fast'
  END AS latency_band,
  CASE
    WHEN COALESCE(cost_estimate, 0.0) >= 0.05 THEN 'high'
    WHEN COALESCE(cost_estimate, 0.0) >= 0.01 THEN 'medium'
    ELSE 'low'
  END AS cost_band,
  CASE
    WHEN freshness_watermark IS NULL OR freshness_watermark IN ('', 'unknown', 'pending') THEN 'stale'
    ELSE 'fresh'
  END AS freshness_state
FROM cgadev.ops_observability.ops_usage_events;

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_route_health AS
SELECT
  route_selected,
  hour_bucket,
  COUNT(*) AS event_count,
  SUM(CASE WHEN response_status = 'success' THEN 1 ELSE 0 END) AS success_count,
  SUM(CASE WHEN response_status = 'partial' THEN 1 ELSE 0 END) AS partial_count,
  SUM(CASE WHEN response_status = 'refused' THEN 1 ELSE 0 END) AS refused_count,
  SUM(CASE WHEN response_status = 'error' THEN 1 ELSE 0 END) AS error_count,
  MAX(latency_ms) AS max_latency_ms,
  AVG(latency_ms) AS avg_latency_ms,
  SUM(COALESCE(total_tokens, 0)) AS total_tokens,
  SUM(COALESCE(cost_estimate, 0.0)) AS total_cost_estimate,
  SUM(CASE WHEN freshness_state = 'stale' THEN 1 ELSE 0 END) AS stale_freshness_count
FROM cgadev.ops_observability.ops_usage_events_normalized
GROUP BY route_selected, hour_bucket;

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_release_readiness AS
WITH route_policy AS (
  SELECT * FROM VALUES
    ('genie', 500, 0.02, 1200),
    ('copilot', 1200, 0.05, 4000),
    ('dashboard_api', 250, 0.005, 800),
    ('internal_app', 800, 0.03, 2500)
  AS route_policy(route_selected, max_latency_ms, max_cost_estimate, max_total_tokens)
),
gold_readiness AS (
  SELECT
    COUNT(*) AS gold_assets_total,
    SUM(CASE WHEN serving_status = 'serve' THEN 1 ELSE 0 END) AS gold_assets_ready
  FROM cgadev.market_gold.gold_serving_readiness
)
SELECT
  h.route_selected,
  h.hour_bucket,
  h.event_count,
  h.success_count,
  h.partial_count,
  h.refused_count,
  h.error_count,
  h.max_latency_ms,
  h.avg_latency_ms,
  h.total_tokens,
  h.total_cost_estimate,
  h.stale_freshness_count,
  p.max_latency_ms AS policy_max_latency_ms,
  p.max_cost_estimate AS policy_max_cost_estimate,
  p.max_total_tokens AS policy_max_total_tokens,
  g.gold_assets_total,
  g.gold_assets_ready,
  CASE
    WHEN h.error_count = 0
      AND h.max_latency_ms < p.max_latency_ms
      AND h.total_cost_estimate < p.max_cost_estimate
      AND h.total_tokens < p.max_total_tokens
      AND h.stale_freshness_count = 0
      AND g.gold_assets_ready = g.gold_assets_total
    THEN 'ready'
    ELSE 'hold'
  END AS readiness_status
FROM cgadev.ops_observability.ops_route_health h
JOIN route_policy p
  ON h.route_selected = p.route_selected
CROSS JOIN gold_readiness g;

CREATE OR REPLACE VIEW cgadev.ops_observability.ops_alert_queue AS
SELECT
  event_time,
  request_id,
  tenant_id,
  route_selected,
  response_status,
  latency_ms,
  cost_estimate,
  freshness_watermark,
  CASE
    WHEN response_status = 'error' THEN 'error_spike'
    WHEN latency_ms >= 1000 THEN 'latency_breach'
    WHEN COALESCE(cost_estimate, 0.0) >= 0.05 THEN 'cost_anomaly'
    WHEN freshness_watermark IS NULL OR freshness_watermark IN ('', 'unknown', 'pending') THEN 'freshness_gap'
    WHEN route_selected = 'copilot' AND COALESCE(total_tokens, 0) >= 4000 THEN 'token_spike'
    ELSE 'informational'
  END AS alert_kind
FROM cgadev.ops_observability.ops_usage_events_normalized
WHERE response_status = 'error'
   OR latency_ms >= 1000
   OR COALESCE(cost_estimate, 0.0) >= 0.05
   OR freshness_watermark IS NULL
   OR freshness_watermark IN ('', 'unknown', 'pending')
   OR (route_selected = 'copilot' AND COALESCE(total_tokens, 0) >= 4000);
