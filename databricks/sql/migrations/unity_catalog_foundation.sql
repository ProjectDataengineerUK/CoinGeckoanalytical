-- Unity Catalog Foundation — cgadev (dev workspace)
-- Staging and prod catalog sections are activated separately when those
-- workspace environments are provisioned by a metastore admin.
--
-- Groups (data_platform, platform_ops, svc_market_ingestion, etc.) are
-- provisioned by the workspace admin separately; the GRANT blocks for them
-- are in unity_catalog_grants_full.sql and should be applied once the
-- groups exist in this workspace.

CREATE CATALOG IF NOT EXISTS cgadev;

CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;
CREATE SCHEMA IF NOT EXISTS cgadev.market_gold;
CREATE SCHEMA IF NOT EXISTS cgadev.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgadev.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgadev.audit_control;
CREATE SCHEMA IF NOT EXISTS cgadev.reference_data;
