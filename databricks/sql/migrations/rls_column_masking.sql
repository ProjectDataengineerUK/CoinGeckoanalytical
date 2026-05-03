-- Row-Level Security and Column Masking for ops_observability tables
-- Purpose: restrict access to sensitive operational data in the CoinGeckoAnalytical platform.

-- Row filter for ops_usage_events:
-- platform_ops and governance_admin members see all rows;
-- other users see only their own rows.
CREATE OR REPLACE FUNCTION cgadev.audit_control.ops_usage_row_filter(event_user_id STRING)
RETURNS BOOLEAN
RETURN is_member('platform_ops') OR is_member('governance_admin') OR current_user() = event_user_id;

ALTER TABLE cgadev.ops_observability.ops_usage_events
SET ROW FILTER cgadev.audit_control.ops_usage_row_filter ON (user_id);

-- Column mask for cost_usd in ops_usage_events:
-- only platform_ops and governance_admin members see the real cost value;
-- all other users see NULL.
CREATE OR REPLACE FUNCTION cgadev.audit_control.mask_cost_usd(cost DOUBLE)
RETURNS DOUBLE
RETURN CASE WHEN is_member('platform_ops') OR is_member('governance_admin') THEN cost ELSE NULL END;

ALTER TABLE cgadev.ops_observability.ops_usage_events
ALTER COLUMN cost_usd SET MASK cgadev.audit_control.mask_cost_usd;

-- Row filter for ops_sentinela_alerts:
-- only platform_ops and governance_admin members can read alert rows.
CREATE OR REPLACE FUNCTION cgadev.audit_control.sentinela_row_filter(dummy STRING)
RETURNS BOOLEAN
RETURN is_member('platform_ops') OR is_member('governance_admin');

ALTER TABLE cgadev.ops_observability.ops_sentinela_alerts
SET ROW FILTER cgadev.audit_control.sentinela_row_filter ON (alert_id);
