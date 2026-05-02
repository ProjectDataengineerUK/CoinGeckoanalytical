from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_JOB_PATH = Path(__file__).resolve().parent.parent / "jobs" / "github_activity_ingestion_job.py"
spec = importlib.util.spec_from_file_location("github_activity_ingestion_job", _JOB_PATH)
github_activity_ingestion_job = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules[spec.name] = github_activity_ingestion_job
spec.loader.exec_module(github_activity_ingestion_job)  # type: ignore[union-attr]


class GitHubActivityIngestionJobTests(unittest.TestCase):
    def _sample_repo_data(self) -> dict:
        return {
            "stargazers_count": 5000,
            "forks_count": 800,
            "open_issues_count": 120,
            "pushed_at": "2026-04-15T10:00:00Z",
            "created_at": "2020-01-01T00:00:00Z",
        }

    def _sample_commit_activity(self) -> list:
        return [{"total": i % 5} for i in range(52)]

    def test_load_repo_map_returns_entries(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"asset_id": "ethereum", "owner": "ethereum", "repo": "go-ethereum"}], f)
            tmp_path = f.name
        entries = github_activity_ingestion_job.load_repo_map(tmp_path)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["asset_id"], "ethereum")

    def test_load_repo_map_filters_incomplete_entries(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([
                {"asset_id": "ethereum", "owner": "ethereum", "repo": "go-ethereum"},
                {"asset_id": "missing_owner"},
            ], f)
            tmp_path = f.name
        entries = github_activity_ingestion_job.load_repo_map(tmp_path)
        self.assertEqual(len(entries), 1)

    def test_normalize_activity_row_computes_fields(self):
        metrics = {
            "repo_full_name": "ethereum/go-ethereum",
            "stars": 5000, "forks": 800, "open_issues": 120,
            "contributors_count": 8, "commits_30d": 42, "commits_90d": 110,
            "repo_age_days": 2000, "last_push_at": "2026-04-15T10:00:00Z",
        }
        row = github_activity_ingestion_job.normalize_activity_row("ethereum", metrics)
        self.assertEqual(row["source_system"], "github")
        self.assertEqual(row["source_record_id"], "ethereum")
        self.assertEqual(row["asset_id"], "ethereum")
        self.assertEqual(row["stars"], 5000)
        self.assertEqual(row["commits_30d"], 42)
        self.assertEqual(row["payload_version"], "github_activity_v1")

    def test_fetch_repo_metrics_handles_202_retry(self):
        import urllib.error
        call_count = {"n": 0}

        def fake_urlopen(request, timeout=None):
            call_count["n"] += 1
            if call_count["n"] == 1:
                err = urllib.error.HTTPError(None, 202, "Computing", {}, None)  # type: ignore
                raise err
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(self._sample_repo_data()).encode()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            return mock_response

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            with patch("time.sleep"):
                result = github_activity_ingestion_job.fetch_repo_metrics("ethereum", "go-ethereum", None)
        self.assertIsNotNone(result)

    def test_default_target_table_is_fully_qualified(self):
        self.assertEqual(
            github_activity_ingestion_job.DEFAULT_TARGET_TABLE,
            "cgadev.market_bronze.bronze_github_activity",
        )

    def test_main_returns_zero_rows_when_skip_live(self):
        class FakeSpark:
            pass
        result = github_activity_ingestion_job.main(FakeSpark(), skip_live=True)
        self.assertEqual(result.rows_written, 0)

    def test_parse_runtime_args_recognises_skip_live(self):
        args = github_activity_ingestion_job.parse_runtime_args(["--skip-live"])
        self.assertTrue(args["skip_live"])


if __name__ == "__main__":
    unittest.main()
