resource "databricks_cluster_policy" "ops_jobs_policy" {
  name = "coingeckoanalytical-${var.environment}-ops-jobs-policy"

  definition = jsonencode({
    "spark_version" = {
      type   = "fixed"
      value  = var.ops_spark_version
      hidden = false
    }
    "node_type_id" = {
      type   = "fixed"
      value  = var.ops_node_type_id
      hidden = false
    }
    "autotermination_minutes" = {
      type  = "fixed"
      value = 15
    }
    "num_workers" = {
      type    = "range"
      minValue = 1
      maxValue = 2
      defaultValue = 1
    }
    "data_security_mode" = {
      type  = "fixed"
      value = "USER_ISOLATION"
    }
  })
}
