# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Validate Market Layers
# MAGIC
# MAGIC Visual validation notebook for the first governed market data family.
# MAGIC It checks Bronze, Silver, Gold, and Genie metric views in the dev catalog.

# COMMAND ----------

dbutils.widgets.text("catalog", "cgadev")
catalog = dbutils.widgets.get("catalog")

# COMMAND ----------

validation_queries = {
    # Phase 1 — Market
    "bronze_market_snapshots":     f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_bronze.bronze_market_snapshots",
    "silver_market_snapshots":     f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_market_snapshots",
    "silver_market_changes":       f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_market_changes",
    "silver_market_dominance":     f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_market_dominance",
    "silver_cross_asset_comparison": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_cross_asset_comparison",
    "gold_market_rankings":        f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_market_rankings",
    "gold_top_movers":             f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_top_movers",
    "gold_market_dominance":       f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_market_dominance",
    "gold_cross_asset_comparison": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_cross_asset_comparison",
    "mv_market_rankings":          f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_market_rankings",
    "mv_top_movers":               f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_top_movers",
    "mv_market_dominance":         f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_market_dominance",
    "mv_cross_asset_compare":      f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_cross_asset_compare",
    # Phase 2 — Enrichment
    "bronze_defillama_protocols":  f"SELECT COUNT(*) AS row_count, MAX(ingested_at) AS latest_observed_at FROM {catalog}.market_bronze.bronze_defillama_protocols",
    "bronze_github_activity":      f"SELECT COUNT(*) AS row_count, MAX(ingested_at) AS latest_observed_at FROM {catalog}.market_bronze.bronze_github_activity",
    "bronze_fred_macro":           f"SELECT COUNT(*) AS row_count, MAX(ingested_at) AS latest_observed_at FROM {catalog}.market_bronze.bronze_fred_macro",
    "silver_asset_enriched":       f"SELECT COUNT(*) AS row_count, MAX(ingested_at) AS latest_observed_at FROM {catalog}.market_silver.silver_asset_enriched",
    "silver_macro_context":        f"SELECT COUNT(*) AS row_count, MAX(ingested_at) AS latest_observed_at FROM {catalog}.market_silver.silver_macro_context",
    "gold_enriched_rankings":      f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_enriched_rankings",
    "gold_defi_protocols":         f"SELECT COUNT(*) AS row_count, MAX(ingested_at) AS latest_observed_at FROM {catalog}.market_gold.gold_defi_protocols",
    "gold_macro_regime":           f"SELECT COUNT(*) AS row_count, MAX(observation_date) AS latest_observed_at FROM {catalog}.market_gold.gold_macro_regime",
    "mv_enriched_rankings":        f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_enriched_rankings",
    "mv_defi_protocols":           f"SELECT COUNT(*) AS row_count, MAX(ingested_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_defi_protocols",
    "mv_macro_regime":             f"SELECT COUNT(*) AS row_count, MAX(observation_date) AS latest_observed_at FROM {catalog}.ai_serving.mv_macro_regime",
}

results = []
for object_name, query in validation_queries.items():
    row = spark.sql(query).collect()[0].asDict()
    results.append(
        {
            "object_name": object_name,
            "row_count": row.get("row_count"),
            "latest_observed_at": row.get("latest_observed_at"),
        }
    )

display(spark.createDataFrame(results))

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT
          asset_id,
          symbol,
          name,
          market_cap_usd,
          price_usd,
          volume_24h_usd,
          observed_at
        FROM {catalog}.market_gold.gold_market_rankings
        ORDER BY market_cap_rank ASC
        LIMIT 25
        """
    )
)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Phase 2 — Enrichment Layer Samples

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT asset_id, stars, forks, commits_30d, commits_90d,
               contributors_count, dev_activity_score, last_push_at
        FROM {catalog}.market_gold.gold_enriched_rankings
        ORDER BY dev_activity_score DESC NULLS LAST
        LIMIT 20
        """
    )
)

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT protocol_name, chain, category,
               tvl_usd, fees_usd, mcap_tvl_ratio
        FROM {catalog}.market_gold.gold_defi_protocols
        ORDER BY tvl_usd DESC NULLS LAST
        LIMIT 20
        """
    )
)

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT series_id, series_name, value, observation_date, regime_label
        FROM {catalog}.market_gold.gold_macro_regime
        ORDER BY observation_date DESC
        LIMIT 10
        """
    )
)
