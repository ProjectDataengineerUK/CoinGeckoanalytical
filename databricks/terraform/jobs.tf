locals {
  ops_job_names = {
    bronze_migration     = "bronze_market_table_migration_job"
    market_source       = "market_source_ingestion_job"
    usage_ingestion     = "ops_usage_ingestion_job"
    bundle_ingestion    = "ops_bundle_run_ingestion_job"
    sentinela_ingestion = "ops_sentinela_alert_ingestion_job"
    readiness_refresh   = "ops_readiness_refresh_job"
  }
}

resource "databricks_job" "bronze_market_table_migration" {
  name = local.ops_job_names.bronze_migration

  task {
    task_key = "migrate_bronze_market_table"

    spark_python_task {
      python_file = "${var.bundle_root}/bronze_market_table_migration_job.py"
    }

    existing_cluster_id = var.ops_cluster_id
  }
}

resource "databricks_job" "market_source_ingestion" {
  name = local.ops_job_names.market_source

  schedule {
    quartz_cron_expression = "0 */5 * * * ?"
    timezone_id            = "America/Sao_Paulo"
    pause_status           = "UNPAUSED"
  }

  task {
    task_key = "ingest_market_source"

    spark_python_task {
      python_file = "${var.bundle_root}/market_source_ingestion_job.py"
    }

    existing_cluster_id = var.ops_cluster_id
  }
}

resource "databricks_job" "ops_usage_ingestion" {
  name = local.ops_job_names.usage_ingestion

  task {
    task_key = "ingest_usage_events"

    spark_python_task {
      python_file = "${var.bundle_root}/ops_usage_ingestion_job.py"
    }

    existing_cluster_id = var.ops_cluster_id
  }
}

resource "databricks_job" "ops_bundle_run_ingestion" {
  name = local.ops_job_names.bundle_ingestion

  task {
    task_key = "ingest_bundle_runs"

    spark_python_task {
      python_file = "${var.bundle_root}/bundle_run_ingestion_job.py"
    }

    existing_cluster_id = var.ops_cluster_id
  }
}

resource "databricks_job" "ops_sentinela_alert_ingestion" {
  name = local.ops_job_names.sentinela_ingestion

  task {
    task_key = "ingest_sentinela_alerts"

    spark_python_task {
      python_file = "${var.bundle_root}/sentinela_alert_ingestion_job.py"
    }

    existing_cluster_id = var.ops_cluster_id
  }
}

resource "databricks_job" "ops_readiness_refresh" {
  name = local.ops_job_names.readiness_refresh

  schedule {
    quartz_cron_expression = "0 */15 * * * ?"
    timezone_id            = "America/Sao_Paulo"
    pause_status           = "UNPAUSED"
  }

  task {
    task_key = "refresh_readiness_views"

    spark_python_task {
      python_file = "${var.bundle_root}/ops_readiness_refresh_job.py"
    }

    existing_cluster_id = var.ops_cluster_id
  }
}
