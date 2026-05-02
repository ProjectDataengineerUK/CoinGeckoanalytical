# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - AI-Powered Ops Analysis (Genie Code)
# MAGIC
# MAGIC Uses Unity AI Gateway models via `ai_query()` to generate natural language
# MAGIC summaries of pipeline health, data freshness, and enrichment quality.
# MAGIC
# MAGIC **Endpoints used (no additional config required):**
# MAGIC - Standard analysis: `databricks-gpt-oss-120b`
# MAGIC - Quick classification: `databricks-gemma-3-12b`

# COMMAND ----------

dbutils.widgets.text("catalog", "cgadev")
dbutils.widgets.text("model_standard", "databricks-gpt-oss-120b")
dbutils.widgets.text("model_light", "databricks-gemma-3-12b")
catalog = dbutils.widgets.get("catalog")
model_standard = dbutils.widgets.get("model_standard")
model_light = dbutils.widgets.get("model_light")

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Pipeline Health Summary

# COMMAND ----------

pipeline_health = spark.sql(f"""
  SELECT
    route_selected,
    is_ready,
    row_count,
    latest_event_time,
    staleness_hours
  FROM {catalog}.ops_observability.ops_route_readiness_latest
  ORDER BY route_selected
""")

display(pipeline_health)

# COMMAND ----------

health_summary_df = spark.sql(f"""
  SELECT ai_query(
    '{model_standard}',
    CONCAT(
      'You are a data platform ops assistant. ',
      'Analyze the following pipeline readiness data and produce a 3-bullet executive summary. ',
      'Flag any staleness_hours > 2 or is_ready = false as critical. ',
      'Be concise. Data: ',
      to_json(collect_list(struct(route_selected, is_ready, row_count, staleness_hours)))
    )
  ) AS health_summary
  FROM {catalog}.ops_observability.ops_route_readiness_latest
""")

print(health_summary_df.collect()[0]["health_summary"])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Token & Cost Usage by Tier

# COMMAND ----------

display(spark.sql(f"""
  SELECT
    model_tier,
    COUNT(*)           AS request_count,
    SUM(total_tokens)  AS total_tokens,
    SUM(cost_estimate) AS total_cost_usd,
    AVG(latency_ms)    AS avg_latency_ms,
    MAX(event_time)    AS latest_request
  FROM {catalog}.ops_observability.ops_usage_events
  WHERE event_time >= CURRENT_TIMESTAMP - INTERVAL 24 HOURS
  GROUP BY model_tier
  ORDER BY total_cost_usd DESC NULLS LAST
"""))

# COMMAND ----------

cost_insight = spark.sql(f"""
  SELECT ai_query(
    '{model_light}',
    CONCAT(
      'Summarize LLM cost breakdown by tier in one sentence each. ',
      'Highlight if complex tier usage exceeds 20% of total requests. ',
      'Data: ',
      to_json(collect_list(struct(model_tier, request_count, total_tokens, total_cost_usd)))
    )
  ) AS cost_summary
  FROM (
    SELECT
      model_tier,
      COUNT(*)           AS request_count,
      SUM(total_tokens)  AS total_tokens,
      SUM(cost_estimate) AS total_cost_usd
    FROM {catalog}.ops_observability.ops_usage_events
    WHERE event_time >= CURRENT_TIMESTAMP - INTERVAL 24 HOURS
    GROUP BY model_tier
  )
""")

print(cost_insight.collect()[0]["cost_summary"])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Enrichment Data Quality Check

# COMMAND ----------

enrichment_health = spark.sql(f"""
  SELECT
    'defillama'   AS source,
    COUNT(*)      AS row_count,
    MAX(ingested_at) AS latest_ingest,
    COUNT(DISTINCT protocol_slug) AS unique_protocols,
    AVG(tvl_usd)  AS avg_tvl_usd
  FROM {catalog}.market_bronze.bronze_defillama_protocols
  UNION ALL
  SELECT
    'github'      AS source,
    COUNT(*)      AS row_count,
    MAX(ingested_at) AS latest_ingest,
    COUNT(DISTINCT asset_id) AS unique_protocols,
    AVG(stars)    AS avg_tvl_usd
  FROM {catalog}.market_bronze.bronze_github_activity
  UNION ALL
  SELECT
    'fred_macro'  AS source,
    COUNT(*)      AS row_count,
    MAX(ingested_at) AS latest_ingest,
    COUNT(DISTINCT series_id) AS unique_protocols,
    AVG(value)    AS avg_tvl_usd
  FROM {catalog}.market_bronze.bronze_fred_macro
""")

display(enrichment_health)

# COMMAND ----------

enrichment_summary = spark.sql(f"""
  SELECT ai_query(
    '{model_standard}',
    CONCAT(
      'You are a data quality analyst. ',
      'Review the following enrichment source health metrics and identify any gaps or anomalies. ',
      'Comment on data freshness and coverage. ',
      'Data: ',
      to_json(collect_list(struct(source, row_count, latest_ingest, unique_protocols)))
    )
  ) AS enrichment_analysis
  FROM (
    SELECT 'defillama' AS source, COUNT(*) AS row_count,
           MAX(ingested_at) AS latest_ingest, COUNT(DISTINCT protocol_slug) AS unique_protocols
    FROM {catalog}.market_bronze.bronze_defillama_protocols
    UNION ALL
    SELECT 'github', COUNT(*), MAX(ingested_at), COUNT(DISTINCT asset_id)
    FROM {catalog}.market_bronze.bronze_github_activity
    UNION ALL
    SELECT 'fred_macro', COUNT(*), MAX(ingested_at), COUNT(DISTINCT series_id)
    FROM {catalog}.market_bronze.bronze_fred_macro
  )
""")

print(enrichment_summary.collect()[0]["enrichment_analysis"])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Macro Regime Classification

# COMMAND ----------

macro_latest = spark.sql(f"""
  SELECT
    series_id,
    series_name,
    value,
    observation_date,
    regime_label
  FROM {catalog}.market_gold.gold_macro_regime
  ORDER BY observation_date DESC
  LIMIT 10
""")

display(macro_latest)

# COMMAND ----------

macro_narrative = spark.sql(f"""
  SELECT ai_query(
    '{model_standard}',
    CONCAT(
      'You are a macro analyst covering crypto markets. ',
      'Given the latest macro indicators below, write a 2-paragraph market context summary. ',
      'Include the current rate environment and USD trend implications for crypto assets. ',
      'Data: ',
      to_json(collect_list(struct(series_id, series_name, value, observation_date, regime_label)))
    )
  ) AS macro_narrative
  FROM (
    SELECT series_id, series_name, value, observation_date, regime_label
    FROM {catalog}.market_gold.gold_macro_regime
    ORDER BY observation_date DESC
    LIMIT 8
  )
""")

print(macro_narrative.collect()[0]["macro_narrative"])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Top DeFi Protocols vs Market

# COMMAND ----------

display(spark.sql(f"""
  SELECT
    protocol_name,
    chain,
    category,
    tvl_usd,
    fees_usd,
    revenue_usd,
    mcap_tvl_ratio,
    ingested_at
  FROM {catalog}.market_gold.gold_defi_protocols
  ORDER BY tvl_usd DESC
  LIMIT 20
"""))

# COMMAND ----------

defi_insight = spark.sql(f"""
  SELECT ai_query(
    '{model_standard}',
    CONCAT(
      'You are a DeFi analyst. Summarize the top 5 protocols by TVL and comment on ',
      'any interesting mcap_tvl_ratio outliers. Be concise (3 bullets). ',
      'Data: ',
      to_json(collect_list(struct(protocol_name, chain, category, tvl_usd, mcap_tvl_ratio)))
    )
  ) AS defi_summary
  FROM (
    SELECT protocol_name, chain, category, tvl_usd, mcap_tvl_ratio
    FROM {catalog}.market_gold.gold_defi_protocols
    ORDER BY tvl_usd DESC
    LIMIT 10
  )
""")

print(defi_insight.collect()[0]["defi_summary"])

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Alert Backlog Triage

# COMMAND ----------

alert_backlog = spark.sql(f"""
  SELECT * FROM {catalog}.ops_observability.ops_alert_backlog
  ORDER BY alert_count DESC, latest_event_time DESC
  LIMIT 20
""")

display(alert_backlog)

# COMMAND ----------

if alert_backlog.count() > 0:
    triage = spark.sql(f"""
      SELECT ai_query(
        '{model_light}',
        CONCAT(
          'Triage the following Sentinela alert backlog. ',
          'Classify each alert type as: critical / warning / info. ',
          'Return a JSON list: [{{"alert_type": "...", "severity": "...", "action": "..."}}]. ',
          'Data: ',
          to_json(collect_list(struct(alert_type, alert_count, latest_event_time)))
        )
      ) AS triage_result
      FROM {catalog}.ops_observability.ops_alert_backlog
      WHERE alert_count > 0
    """)
    print(triage.collect()[0]["triage_result"])
else:
    print("No active alerts in backlog.")
