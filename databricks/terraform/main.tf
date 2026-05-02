locals {
  schemas = {
    market_bronze     = var.data_platform_group
    market_silver     = var.data_platform_group
    market_gold       = var.data_platform_group
    reference_data    = var.data_platform_group
    ai_serving        = var.product_analytics_group
    ops_observability = var.platform_ops_group
    audit_control     = var.governance_admin_group
  }
}

resource "databricks_catalog" "env" {
  name         = var.catalog_name
  comment      = "CoinGeckoAnalytical ${var.environment} catalog"
  force_destroy = false
}

resource "databricks_schema" "schemas" {
  for_each     = local.schemas
  catalog_name = databricks_catalog.env.name
  name         = each.key
  comment      = "CoinGeckoAnalytical ${each.key} schema for ${var.environment}"
}

resource "databricks_grants" "catalog_use" {
  catalog = databricks_catalog.env.name

  grant {
    principal  = var.product_backend_group
    privileges = ["USE_CATALOG"]
  }

  grant {
    principal  = var.platform_ops_group
    privileges = ["USE_CATALOG"]
  }

  grant {
    principal  = var.governance_admin_group
    privileges = ["USE_CATALOG"]
  }
}

resource "databricks_grants" "market_gold" {
  schema = "${databricks_catalog.env.name}.market_gold"

  grant {
    principal  = var.product_backend_group
    privileges = ["USE_SCHEMA", "SELECT"]
  }

  grant {
    principal  = var.platform_ops_group
    privileges = ["USE_SCHEMA"]
  }
}

resource "databricks_grants" "ai_serving" {
  schema = "${databricks_catalog.env.name}.ai_serving"

  grant {
    principal  = var.product_backend_group
    privileges = ["USE_SCHEMA", "SELECT"]
  }

  grant {
    principal  = var.product_analytics_group
    privileges = ["USE_SCHEMA", "SELECT", "MODIFY"]
  }
}

resource "databricks_grants" "ops_observability" {
  schema = "${databricks_catalog.env.name}.ops_observability"

  grant {
    principal  = var.platform_ops_group
    privileges = ["USE_SCHEMA", "SELECT", "MODIFY"]
  }

  grant {
    principal  = var.governance_admin_group
    privileges = ["USE_SCHEMA", "SELECT"]
  }
}

resource "databricks_grants" "audit_control" {
  schema = "${databricks_catalog.env.name}.audit_control"

  grant {
    principal  = var.governance_admin_group
    privileges = ["USE_SCHEMA", "SELECT", "MODIFY"]
  }
}
