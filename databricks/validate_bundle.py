from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_JOB_KEYS = {
    "ops_usage_ingestion_job",
    "ops_readiness_refresh_job",
    "ops_bundle_run_ingestion_job",
    "ops_sentinela_alert_ingestion_job",
}


def load_bundle(path: str | Path = "databricks.yml") -> dict[str, Any]:
    bundle_path = Path(path)
    if not bundle_path.is_absolute():
        bundle_path = Path(__file__).resolve().parent / bundle_path
    return yaml.safe_load(bundle_path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any], root_dir: str | Path | None = None) -> list[str]:
    errors: list[str] = []
    base_dir = Path(root_dir) if root_dir is not None else Path.cwd()

    if bundle.get("bundle", {}).get("name") != "coingeckoanalytical-databricks":
        errors.append("bundle name must be coingeckoanalytical-databricks")

    jobs = bundle.get("resources", {}).get("jobs", {})
    missing_jobs = REQUIRED_JOB_KEYS - set(jobs.keys())
    if missing_jobs:
        errors.append(f"missing jobs: {', '.join(sorted(missing_jobs))}")

    for job_name, job in jobs.items():
        schedule = job.get("schedule")
        if job_name not in {"ops_bundle_run_ingestion_job", "ops_sentinela_alert_ingestion_job"}:
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

    return errors


def main() -> int:
    bundle = load_bundle()
    errors = validate_bundle(bundle, root_dir=Path(__file__).resolve().parent)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Bundle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
