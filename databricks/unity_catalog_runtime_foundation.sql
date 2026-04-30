-- Databricks Unity Catalog Runtime Foundation
-- Purpose: ensure the catalog and schemas exist for runtime refresh jobs
-- without applying ownership or grant changes that require external principals.

CREATE CATALOG IF NOT EXISTS cgadev;
CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;
CREATE SCHEMA IF NOT EXISTS cgadev.market_gold;
CREATE SCHEMA IF NOT EXISTS cgadev.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgadev.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgadev.audit_control;
CREATE SCHEMA IF NOT EXISTS cgadev.reference_data;
