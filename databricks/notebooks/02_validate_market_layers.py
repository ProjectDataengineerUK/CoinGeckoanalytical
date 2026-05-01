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
    "bronze_market_snapshots": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_bronze.bronze_market_snapshots",
    "silver_market_snapshots": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_market_snapshots",
    "silver_market_changes": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_market_changes",
    "silver_market_dominance": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_market_dominance",
    "silver_cross_asset_comparison": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_silver.silver_cross_asset_comparison",
    "gold_market_rankings": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_market_rankings",
    "gold_top_movers": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_top_movers",
    "gold_market_dominance": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_market_dominance",
    "gold_cross_asset_comparison": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.market_gold.gold_cross_asset_comparison",
    "mv_market_rankings": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_market_rankings",
    "mv_top_movers": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_top_movers",
    "mv_market_dominance": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_market_dominance",
    "mv_cross_asset_compare": f"SELECT COUNT(*) AS row_count, MAX(observed_at) AS latest_observed_at FROM {catalog}.ai_serving.mv_cross_asset_compare",
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
