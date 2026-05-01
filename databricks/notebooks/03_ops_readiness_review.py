# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Ops Readiness Review
# MAGIC
# MAGIC Operator-facing notebook for readiness and observability checks.

# COMMAND ----------

dbutils.widgets.text("catalog", "cgadev")
catalog = dbutils.widgets.get("catalog")

# COMMAND ----------

display(spark.sql(f"SELECT * FROM {catalog}.ops_observability.ops_ready_overview"))

# COMMAND ----------

display(spark.sql(f"SELECT * FROM {catalog}.ops_observability.ops_route_readiness_latest ORDER BY route_selected"))

# COMMAND ----------

display(spark.sql(f"SELECT * FROM {catalog}.ops_observability.ops_bundle_run_status ORDER BY latest_update_time DESC"))

# COMMAND ----------

display(spark.sql(f"SELECT * FROM {catalog}.ops_observability.ops_sentinela_alert_status"))

# COMMAND ----------

display(spark.sql(f"SELECT * FROM {catalog}.ops_observability.ops_alert_backlog ORDER BY alert_count DESC, latest_event_time DESC"))
