-- Unity Catalog Full Governance Grants
-- Apply this file manually (via a metastore admin account) AFTER:
--   1. cgastaging and cgaprod catalogs are provisioned by metastore admin
--   2. Workspace groups are created: data_platform, product_analytics, platform_ops,
--      product_backend, governance_admin, svc_market_ingestion, svc_market_pipeline,
--      svc_ops_pipeline, svc_audit_pipeline
--
-- Do NOT run this via uc_grants_job — it requires metastore admin privileges
-- that the CI service principal does not hold.

CREATE CATALOG IF NOT EXISTS cgastaging;
CREATE CATALOG IF NOT EXISTS cgaprod;

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

-- Ownership posture (cgadev).
ALTER SCHEMA cgadev.market_bronze OWNER TO `data_platform`;
ALTER SCHEMA cgadev.market_silver OWNER TO `data_platform`;
ALTER SCHEMA cgadev.market_gold OWNER TO `data_platform`;
ALTER SCHEMA cgadev.reference_data OWNER TO `data_platform`;
ALTER SCHEMA cgadev.ai_serving OWNER TO `product_analytics`;
ALTER SCHEMA cgadev.ops_observability OWNER TO `platform_ops`;
ALTER SCHEMA cgadev.audit_control OWNER TO `governance_admin`;

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

-- Audit reads.
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
