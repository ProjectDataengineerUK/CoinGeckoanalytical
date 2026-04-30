variable "databricks_host" {
  description = "Databricks workspace host."
  type        = string
}

variable "databricks_token" {
  description = "Databricks workspace token."
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "catalog_name" {
  description = "Unity Catalog name for the environment."
  type        = string
}

variable "data_platform_group" {
  description = "Principal for the data platform ownership domain."
  type        = string
}

variable "product_backend_group" {
  description = "Principal used by the product backend."
  type        = string
}

variable "product_analytics_group" {
  description = "Principal used by product analytics and Genie-related governed assets."
  type        = string
}

variable "platform_ops_group" {
  description = "Principal used by operations and Sentinela review."
  type        = string
}

variable "governance_admin_group" {
  description = "Principal used by governance and audit review."
  type        = string
}

variable "svc_market_ingestion" {
  description = "Service principal for market ingestion."
  type        = string
}

variable "svc_market_pipeline" {
  description = "Service principal for Silver and Gold pipelines."
  type        = string
}

variable "svc_ops_pipeline" {
  description = "Service principal for operational ingestion and readiness jobs."
  type        = string
}

variable "svc_audit_pipeline" {
  description = "Service principal for audit-sensitive pipelines."
  type        = string
}

variable "bundle_root" {
  description = "Workspace path where bundle files are available for Terraform-managed jobs."
  type        = string
  default     = "/Workspace/Shared/coingeckoanalytical/databricks"
}

variable "ops_cluster_id" {
  description = "Existing cluster id for Phase 1 operational jobs."
  type        = string
}

variable "ops_spark_version" {
  description = "Spark runtime version for operational jobs."
  type        = string
  default     = "15.4.x-scala2.12"
}

variable "ops_node_type_id" {
  description = "Node type for operational jobs."
  type        = string
  default     = "Standard_DS3_v2"
}
