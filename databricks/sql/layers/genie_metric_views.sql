-- Databricks Genie Metric Views
-- Purpose: governed views in cgadev.ai_serving that expose Gold analytical
-- tables for AI/BI Genie, dashboards, and SQL consumers.

CREATE OR REPLACE VIEW cgadev.ai_serving.mv_market_rankings AS
SELECT * FROM cgadev.market_gold.gold_market_rankings;

CREATE OR REPLACE VIEW cgadev.ai_serving.mv_top_movers AS
SELECT * FROM cgadev.market_gold.gold_top_movers;

CREATE OR REPLACE VIEW cgadev.ai_serving.mv_market_dominance AS
SELECT * FROM cgadev.market_gold.gold_market_dominance;

CREATE OR REPLACE VIEW cgadev.ai_serving.mv_cross_asset_compare AS
SELECT * FROM cgadev.market_gold.gold_cross_asset_comparison;
