from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parent / "live_sql_validation.py"
SPEC = importlib.util.spec_from_file_location("live_sql_validation", MODULE_PATH)
live_sql_validation = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = live_sql_validation
SPEC.loader.exec_module(live_sql_validation)


class LiveSqlValidationTests(unittest.TestCase):
    def test_build_statement_request_uses_expected_shape(self) -> None:
        payload = live_sql_validation.build_statement_request("SELECT 1", "warehouse-1")

        self.assertEqual(payload["warehouse_id"], "warehouse-1")
        self.assertEqual(payload["disposition"], "INLINE")
        self.assertEqual(payload["format"], "JSON_ARRAY")

    def test_summarize_statement_response_extracts_first_value(self) -> None:
        summary = live_sql_validation.summarize_statement_response(
            {
                "statement_id": "stmt-1",
                "status": {"state": "SUCCEEDED"},
                "result": {"data_array": [[3]], "manifest": {"format": "JSON_ARRAY"}},
            }
        )

        self.assertEqual(summary["statement_id"], "stmt-1")
        self.assertEqual(summary["state"], "SUCCEEDED")
        self.assertEqual(summary["row_count_value"], 3)

    def test_main_skips_when_warehouse_env_missing(self) -> None:
        env = {
            "DATABRICKS_HOST": "https://example.cloud.databricks.com",
            "DATABRICKS_TOKEN": "token",
        }
        with patch.dict(os.environ, env, clear=True):
            result = live_sql_validation.main()

        self.assertEqual(result, 0)

    def test_write_results_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "results.json"
            written = live_sql_validation.write_results(path, {"bronze_rows": {"row_count_value": 3}})
            payload = json.loads(written.read_text(encoding="utf-8"))

        self.assertEqual(payload["bronze_rows"]["row_count_value"], 3)


if __name__ == "__main__":
    unittest.main()
