# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Ingest CoinGecko Market Data
# MAGIC
# MAGIC Notebook entrypoint for the governed CoinGecko market ingestion path.
# MAGIC The production logic lives in `market_source_ingestion_job.py`; this notebook
# MAGIC keeps the Databricks workspace experience familiar without duplicating code.

# COMMAND ----------

dbutils.widgets.text("target_table", "cgadev.market_bronze.bronze_market_snapshots")
dbutils.widgets.text("payload_json", "")
dbutils.widgets.text("payload_path", "")

# COMMAND ----------

import sys
from pathlib import Path

current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from market_source_ingestion_job import main

target_table = dbutils.widgets.get("target_table")
payload_json = dbutils.widgets.get("payload_json") or None
payload_path = dbutils.widgets.get("payload_path") or None

result = main(
    spark,
    payload_json=payload_json,
    payload_path=payload_path,
    target_table=target_table,
)

display(
    spark.createDataFrame(
        [
            {
                "rows_written": result.rows_written,
                "target_table": result.target_table,
            }
        ]
    )
)

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT
          COUNT(*) AS bronze_rows,
          MAX(observed_at) AS latest_observed_at,
          MAX(ingested_at) AS latest_ingested_at
        FROM {target_table}
        """
    )
)
