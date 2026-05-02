from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_JOB_KEYS = {
    "bronze_market_table_migration_job",
    "silver_market_table_migration_job",
    "silver_market_pipeline_job",
    "market_source_ingestion_job",
    "ops_usage_ingestion_job",
    "ops_readiness_refresh_job",
    "ops_bundle_run_ingestion_job",
    "ops_sentinela_alert_ingestion_job",
    "bronze_enrichment_migration_job",
    "silver_enrichment_migration_job",
    "defillama_ingestion_job",
    "github_activity_ingestion_job",
    "fred_macro_ingestion_job",
    "silver_enrichment_pipeline_job",
}

REQUIRED_NOTEBOOKS = {
    "notebooks/01_ingest_coingecko_market.py",
    "notebooks/02_validate_market_layers.py",
    "notebooks/03_ops_readiness_review.py",
}

REQUIRED_MODEL_ENDPOINTS = {
    "coingecko_copilot_light",
    "coingecko_copilot_standard",
    "coingecko_copilot_complex",
}

_ENDPOINT_TIER_MODEL = {
    "coingecko_copilot_light": "claude-haiku",
    "coingecko_copilot_standard": "claude-sonnet",
    "coingecko_copilot_complex": "claude-opus",
}


def load_bundle(path: str | Path = "databricks.yml") -> dict[str, Any]:
    bundle_path = Path(path)
    if not bundle_path.is_absolute():
        bundle_path = Path(__file__).resolve().parent.parent / bundle_path
    return yaml.safe_load(bundle_path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any], root_dir: str | Path | None = None) -> list[str]:
    errors: list[str] = []
    base_dir = Path(root_dir) if root_dir is not None else Path.cwd()

    if bundle.get("bundle", {}).get("name") != "coingeckoanalytical-databricks":
        errors.append("bundle name must be coingeckoanalytical-databricks")

    sync_excludes = set(bundle.get("sync", {}).get("exclude", []))
    if "notebooks/**" not in sync_excludes:
        errors.append("Databricks notebooks must be excluded from job bundle file sync")

    jobs = bundle.get("resources", {}).get("jobs", {})
    missing_jobs = REQUIRED_JOB_KEYS - set(jobs.keys())
    if missing_jobs:
        errors.append(f"missing jobs: {', '.join(sorted(missing_jobs))}")

    for job_name, job in jobs.items():
        schedule = job.get("schedule")
        if job_name not in {
            "bronze_market_table_migration_job",
            "silver_market_table_migration_job",
            "bronze_enrichment_migration_job",
            "silver_enrichment_migration_job",
            "ops_bundle_run_ingestion_job",
            "ops_sentinela_alert_ingestion_job",
        }:
            schedule = schedule or {}
            if schedule.get("pause_status") != "UNPAUSED":
                errors.append(f"{job_name} must be unpaused")
            if "quartz_cron_expression" not in schedule:
                errors.append(f"{job_name} must define a quartz_cron_expression")

        tasks = job.get("tasks", [])
        if not tasks:
            errors.append(f"{job_name} must define at least one task")
            continue

        task = tasks[0]
        python_file = task.get("spark_python_task", {}).get("python_file")
        if not python_file:
            errors.append(f"{job_name} must define a spark_python_task python_file")
            continue

        python_path = (base_dir / python_file).resolve()
        if not python_path.exists():
            errors.append(f"{job_name} python_file does not exist: {python_file}")

        if task.get("environment_key") != "default":
            errors.append(f"{job_name} must use environment_key default")

    for notebook in sorted(REQUIRED_NOTEBOOKS):
        notebook_path = base_dir / notebook
        if not notebook_path.exists():
            errors.append(f"missing Databricks notebook asset: {notebook}")

    endpoints = bundle.get("resources", {}).get("model_serving_endpoints", {})
    missing_endpoints = REQUIRED_MODEL_ENDPOINTS - set(endpoints.keys())
    if missing_endpoints:
        errors.append(f"missing model_serving_endpoints: {', '.join(sorted(missing_endpoints))}")

    for ep_key, ep in endpoints.items():
        if ep_key not in REQUIRED_MODEL_ENDPOINTS:
            continue
        served = (ep.get("config") or {}).get("served_entities") or []
        if not served:
            errors.append(f"{ep_key} must define at least one served_entity")
            continue
        ext = served[0].get("external_model") or {}
        if ext.get("provider") != "anthropic":
            errors.append(f"{ep_key} external_model.provider must be anthropic")
        if ext.get("task") != "llm/v1/chat":
            errors.append(f"{ep_key} external_model.task must be llm/v1/chat")
        model_name = ext.get("name", "")
        expected_fragment = _ENDPOINT_TIER_MODEL[ep_key]
        if expected_fragment not in model_name:
            errors.append(f"{ep_key} model name must contain '{expected_fragment}', got '{model_name}'")
        anthropic_cfg = ext.get("anthropic_config") or {}
        api_key_ref = anthropic_cfg.get("anthropic_api_key", "")
        if not api_key_ref.startswith("{{secrets/"):
            errors.append(f"{ep_key} anthropic_api_key must be a secret reference ({{{{secrets/...}}}})")

    return errors


def main() -> int:
    bundle = load_bundle()
    errors = validate_bundle(bundle, root_dir=Path(__file__).resolve().parent.parent)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Bundle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
