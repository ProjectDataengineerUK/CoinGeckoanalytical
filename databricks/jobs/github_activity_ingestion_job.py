from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_TARGET_TABLE = "cgadev.market_bronze.bronze_github_activity"
DEFAULT_REPO_MAP_PATH = "../config/github_asset_repo_map.json"
GITHUB_API_BASE = "https://api.github.com"


@dataclass(frozen=True)
class IngestionResult:
    rows_written: int
    target_table: str


def load_repo_map(map_path: str | Path) -> list[dict[str, str]]:
    path = Path(map_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / map_path
    data = json.loads(path.read_text(encoding="utf-8"))
    return [entry for entry in data if entry.get("asset_id") and entry.get("owner") and entry.get("repo")]


def _request_json(url: str, token: str | None, max_retries: int = 3) -> Any:
    headers = {"accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    attempt = 0
    while True:
        try:
            request = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 202:
                attempt += 1
                if attempt >= max_retries:
                    return None
                time.sleep(5.0)
                continue
            attempt += 1
            if exc.code in {403, 404} or attempt >= max_retries:
                return None
            if exc.code in {429, 500, 502, 503}:
                time.sleep(attempt * 2.0)
                continue
            return None
        except urllib.error.URLError:
            attempt += 1
            if attempt >= max_retries:
                return None
            time.sleep(attempt * 2.0)


def fetch_repo_metrics(owner: str, repo: str, token: str | None) -> dict[str, Any] | None:
    repo_data = _request_json(f"{GITHUB_API_BASE}/repos/{owner}/{repo}", token)
    if not repo_data or not isinstance(repo_data, dict):
        return None

    commit_activity = _request_json(
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}/stats/commit_activity", token
    )

    commits_30d = 0
    commits_90d = 0
    contributors_count = 0
    if isinstance(commit_activity, list) and len(commit_activity) >= 4:
        weeks = commit_activity[-13:] if len(commit_activity) >= 13 else commit_activity
        commits_90d = sum(w.get("total", 0) for w in weeks)
        commits_30d = sum(w.get("total", 0) for w in commit_activity[-4:])
        contributors_count = sum(1 for w in commit_activity[-13:] if w.get("total", 0) > 0)

    pushed_at = repo_data.get("pushed_at") or ""
    created_at = repo_data.get("created_at") or ""
    repo_age_days = 0
    if created_at:
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            repo_age_days = (datetime.now(timezone.utc) - created).days
        except ValueError:
            pass

    return {
        "repo_full_name": f"{owner}/{repo}",
        "stars": int(repo_data.get("stargazers_count") or 0),
        "forks": int(repo_data.get("forks_count") or 0),
        "open_issues": int(repo_data.get("open_issues_count") or 0),
        "contributors_count": contributors_count,
        "commits_30d": commits_30d,
        "commits_90d": commits_90d,
        "repo_age_days": repo_age_days,
        "last_push_at": pushed_at,
    }


def normalize_activity_row(asset_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
    now = _utc_now_isoformat()
    return {
        "source_system": "github",
        "source_record_id": asset_id,
        "asset_id": asset_id,
        "repo_full_name": metrics["repo_full_name"],
        "stars": metrics["stars"],
        "forks": metrics["forks"],
        "open_issues": metrics["open_issues"],
        "contributors_count": metrics["contributors_count"],
        "commits_30d": metrics["commits_30d"],
        "commits_90d": metrics["commits_90d"],
        "repo_age_days": metrics["repo_age_days"],
        "last_push_at": metrics["last_push_at"],
        "observed_at": now,
        "ingested_at": now,
        "payload_version": "github_activity_v1",
    }


def fetch_all_activity(
    repo_map: list[dict[str, str]],
    token: str | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for entry in repo_map:
        metrics = fetch_repo_metrics(entry["owner"], entry["repo"], token)
        if metrics is not None:
            rows.append(normalize_activity_row(entry["asset_id"], metrics))
    return rows


def write_activity_rows(
    spark: Any,
    rows: list[dict[str, Any]],
    target_table: str = DEFAULT_TARGET_TABLE,
) -> IngestionResult:
    if not rows:
        return IngestionResult(rows_written=0, target_table=target_table)
    df = spark.createDataFrame(rows)
    df = df.dropDuplicates(["source_system", "source_record_id"])
    df.write.mode("append").format("delta").saveAsTable(target_table)
    return IngestionResult(rows_written=df.count(), target_table=target_table)


def main(
    spark: Any,
    target_table: str = DEFAULT_TARGET_TABLE,
    repo_map_path: str = DEFAULT_REPO_MAP_PATH,
    github_token: str | None = None,
) -> IngestionResult:
    repo_map = load_repo_map(repo_map_path)
    rows = fetch_all_activity(repo_map, token=github_token)
    return write_activity_rows(spark, rows, target_table=target_table)


def parse_runtime_args(argv: list[str]) -> dict[str, str | None]:
    parsed: dict[str, str | None] = {"target_table": None}
    index = 0
    while index < len(argv):
        if argv[index] == "--target-table" and index + 1 < len(argv):
            parsed["target_table"] = argv[index + 1]
            index += 2
            continue
        index += 1
    return parsed


def _utc_now_isoformat() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    widgets: dict[str, Any] = {}
    try:
        widgets["target_table"] = dbutils.widgets.get("target_table")  # type: ignore[name-defined]
    except Exception:
        widgets["target_table"] = DEFAULT_TARGET_TABLE

    runtime_args = parse_runtime_args(sys.argv[1:])
    target = widgets["target_table"] or runtime_args["target_table"] or DEFAULT_TARGET_TABLE

    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        try:
            github_token = dbutils.secrets.get("github", "token")  # type: ignore[name-defined]
        except Exception:
            github_token = None

    result = main(spark_session, target_table=target, github_token=github_token)
    print(json.dumps({"rows_written": result.rows_written, "target_table": result.target_table}))
