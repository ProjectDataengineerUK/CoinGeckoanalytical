-- Unity Catalog Foundation Baseline
-- Purpose: define the first governed Unity Catalog structure for the
-- CoinGeckoAnalytical Phase 1 base.

-- Environment note:
-- Replace `cgadev`, `cgastaging`, and `cgaprod` with the target catalog names
-- chosen for each workspace.

CREATE CATALOG IF NOT EXISTS cgadev;
CREATE CATALOG IF NOT EXISTS cgastaging;
CREATE CATALOG IF NOT EXISTS cgaprod;

CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;
CREATE SCHEMA IF NOT EXISTS cgadev.market_gold;
CREATE SCHEMA IF NOT EXISTS cgadev.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgadev.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgadev.audit_control;
CREATE SCHEMA IF NOT EXISTS cgadev.reference_data;

CREATE SCHEMA IF NOT EXISTS cgastaging.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgastaging.market_silver;
CREATE SCHEMA IF NOT EXISTS cgastaging.market_gold;
CREATE SCHEMA IF NOT EXISTS cgastaging.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgastaging.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgastaging.audit_control;
CREATE SCHEMA IF NOT EXISTS cgastaging.reference_data;

CREATE SCHEMA IF NOT EXISTS cgaprod.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgaprod.market_silver;
CREATE SCHEMA IF NOT EXISTS cgaprod.market_gold;
CREATE SCHEMA IF NOT EXISTS cgaprod.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgaprod.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgaprod.audit_control;
CREATE SCHEMA IF NOT EXISTS cgaprod.reference_data;

-- Example ownership posture for the dev catalog.
ALTER SCHEMA cgadev.market_bronze OWNER TO `data_platform`;
ALTER SCHEMA cgadev.market_silver OWNER TO `data_platform`;
ALTER SCHEMA cgadev.market_gold OWNER TO `data_platform`;
ALTER SCHEMA cgadev.reference_data OWNER TO `data_platform`;
ALTER SCHEMA cgadev.ai_serving OWNER TO `product_analytics`;
ALTER SCHEMA cgadev.ops_observability OWNER TO `platform_ops`;
ALTER SCHEMA cgadev.audit_control OWNER TO `governance_admin`;

-- Environment duplication rule:
-- replicate the same owner posture for staging and prod with environment-appropriate groups.

-- Shared product reads.
GRANT USE CATALOG ON CATALOG cgadev TO `product_backend`, `platform_ops`, `governance_admin`;
GRANT USE SCHEMA ON SCHEMA cgadev.market_gold TO `product_backend`, `platform_ops`, `governance_admin`;
GRANT SELECT ON FUTURE TABLES IN SCHEMA cgadev.market_gold TO `product_backend`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.market_gold TO `product_backend`;

-- Genie analytical scope.
GRANT USE SCHEMA ON SCHEMA cgadev.ai_serving TO `product_backend`, `product_analytics`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.ai_serving TO `product_backend`, `product_analytics`;

-- Operational reads.
GRANT USE SCHEMA ON SCHEMA cgadev.ops_observability TO `platform_ops`, `governance_admin`;
GRANT SELECT ON FUTURE TABLES IN SCHEMA cgadev.ops_observability TO `platform_ops`, `governance_admin`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.ops_observability TO `platform_ops`, `governance_admin`;

-- Audit reads are more restricted.
GRANT USE SCHEMA ON SCHEMA cgadev.audit_control TO `governance_admin`;
GRANT SELECT ON FUTURE TABLES IN SCHEMA cgadev.audit_control TO `governance_admin`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.audit_control TO `governance_admin`;

-- Write posture for service principals and jobs.
GRANT USE SCHEMA ON SCHEMA cgadev.market_bronze TO `svc_market_ingestion`;
GRANT CREATE TABLE, MODIFY ON SCHEMA cgadev.market_bronze TO `svc_market_ingestion`;

GRANT USE SCHEMA ON SCHEMA cgadev.market_silver TO `svc_market_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.market_silver TO `svc_market_pipeline`;

GRANT USE SCHEMA ON SCHEMA cgadev.market_gold TO `svc_market_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.market_gold TO `svc_market_pipeline`;

GRANT USE SCHEMA ON SCHEMA cgadev.ops_observability TO `svc_ops_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.ops_observability TO `svc_ops_pipeline`;

GRANT USE SCHEMA ON SCHEMA cgadev.audit_control TO `svc_audit_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.audit_control TO `svc_audit_pipeline`;

-- Naming guidance:
-- cgadev.market_bronze.bronze_market_snapshots
-- cgadev.market_silver.silver_market_snapshots
-- cgadev.market_silver.silver_market_changes
-- cgadev.market_silver.silver_market_dominance
-- cgadev.market_silver.silver_cross_asset_comparison
-- cgadev.market_gold.gold_market_rankings
-- cgadev.market_gold.gold_top_movers
-- cgadev.market_gold.gold_market_dominance
-- cgadev.market_gold.gold_cross_asset_comparison
-- cgadev.ai_serving.mv_market_rankings
-- cgadev.ai_serving.mv_top_movers
-- cgadev.ai_serving.mv_market_dominance
-- cgadev.ai_serving.mv_cross_asset_compare
-- cgadev.ops_observability.ops_usage_events
-- cgadev.ops_observability.ops_sentinela_alerts
