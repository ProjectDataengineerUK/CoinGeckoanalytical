from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class CIWorkflowTests(unittest.TestCase):
    def test_workflow_includes_bundle_validation_and_backend_tests(self) -> None:
        workflow_path = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["backend-tests"]["steps"]
        step_names = [step.get("name", "") for step in steps]
        run_commands = "\n".join(step.get("run", "") for step in steps if isinstance(step.get("run"), str))

        self.assertIn("Run backend tests", step_names)
        self.assertIn("Run Databricks bundle validation helper", step_names)
        self.assertIn("Run Databricks helper tests", step_names)
        self.assertIn("python3 databricks/validate_bundle.py", run_commands)
        self.assertIn("python3 -m unittest databricks.test_validate_bundle", run_commands)


if __name__ == "__main__":
    unittest.main()
