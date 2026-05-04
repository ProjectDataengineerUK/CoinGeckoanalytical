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
    "feature_engineering_job",
    "train_market_model_job",
    "score_market_assets_job",
    "sentinela_evaluation_job",
    "uc_grants_job",
    "rls_migration_job",
    "model_drift_monitoring_job",
}

REQUIRED_NOTEBOOKS = {
    "databricks/notebooks/01_ingest_coingecko_market.py",
    "databricks/notebooks/02_validate_market_layers.py",
    "databricks/notebooks/03_ops_readiness_review.py",
}

REQUIRED_APPS = {
    "cga_analytics": "apps/cga-analytics",
    "cga_admin": "apps/cga-admin",
}


def load_bundle(path: str | Path = "databricks.yml") -> dict[str, Any]:
    bundle_path = Path(path)
    if not bundle_path.is_absolute():
        # Check repo root first (new canonical location), then databricks/ subdirectory
        repo_root = Path(__file__).resolve().parents[2]
        root_candidate = repo_root / bundle_path
        if root_candidate.exists():
            bundle_path = root_candidate
        else:
            bundle_path = Path(__file__).resolve().parent.parent / bundle_path
    return yaml.safe_load(bundle_path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any], root_dir: str | Path | None = None) -> list[str]:
    errors: list[str] = []
    # Default to repo root so ./databricks/jobs/* paths resolve correctly
    if root_dir is not None:
        base_dir = Path(root_dir)
    else:
        repo_root = Path(__file__).resolve().parents[2]
        base_dir = repo_root

    if bundle.get("bundle", {}).get("name") != "coingeckoanalytical-databricks":
        errors.append("bundle name must be coingeckoanalytical-databricks")

    sync_excludes = set(bundle.get("sync", {}).get("exclude", []))
    if not any("notebooks/**" in e for e in sync_excludes):
        errors.append("Databricks notebooks must be excluded from job bundle file sync")

    apps = bundle.get("resources", {}).get("apps", {})
    missing_apps = set(REQUIRED_APPS) - set(apps.keys())
    if missing_apps:
        errors.append(f"missing apps: {', '.join(sorted(missing_apps))}")

    for app_name, expected_path in REQUIRED_APPS.items():
        app = apps.get(app_name)
        if not isinstance(app, dict):
            continue
        if app.get("source_code_path") != f"./{expected_path}":
            errors.append(f"{app_name} source_code_path must be ./{expected_path}")
        app_yaml_path = base_dir / expected_path / "app.yaml"
        if not app_yaml_path.exists():
            errors.append(f"{app_name} app.yaml is missing: {expected_path}/app.yaml")
            continue
        app_yaml = yaml.safe_load(app_yaml_path.read_text(encoding="utf-8")) or {}
        command = app_yaml.get("command")
        if not isinstance(command, list) or not command:
            errors.append(f"{app_name} app.yaml must define a non-empty command sequence")
        env_items = app_yaml.get("env", [])
        if not isinstance(env_items, list):
            errors.append(f"{app_name} app.yaml env must be a list")
            continue
        for idx, item in enumerate(env_items):
            if not isinstance(item, dict):
                errors.append(f"{app_name} app.yaml env[{idx}] must be a mapping")
                continue
            if not item.get("name"):
                errors.append(f"{app_name} app.yaml env[{idx}] must define name")
            if ("value" in item) == ("valueFrom" in item):
                errors.append(f"{app_name} app.yaml env[{idx}] must define exactly one of value or valueFrom")

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
            "train_market_model_job",
            "uc_grants_job",
            "rls_migration_job",
            "model_drift_monitoring_job",
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

    return errors


def main() -> int:
    bundle = load_bundle()
    errors = validate_bundle(bundle, root_dir=Path(__file__).resolve().parents[2])
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Bundle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
