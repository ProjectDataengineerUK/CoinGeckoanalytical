locals {
  service_principals = {
    market_ingestion = var.svc_market_ingestion
    market_pipeline  = var.svc_market_pipeline
    ops_pipeline     = var.svc_ops_pipeline
    audit_pipeline   = var.svc_audit_pipeline
  }
}

resource "databricks_group_role" "service_principal_roles" {
  for_each = local.service_principals

  group_id = each.value
  role     = "account_user"
}
