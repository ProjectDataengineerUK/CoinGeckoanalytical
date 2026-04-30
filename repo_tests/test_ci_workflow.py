from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class CIWorkflowTests(unittest.TestCase):
    def test_workflow_includes_bundle_validation_and_backend_tests(self) -> None:
        workflow_path = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        jobs = workflow["jobs"]
        self.assertEqual(set(jobs.keys()), {"lint", "contract", "deploy"})

        contract_steps = jobs["contract"]["steps"]
        contract_step_names = [step.get("name", "") for step in contract_steps]
        contract_run_commands = "\n".join(
            step.get("run", "") for step in contract_steps if isinstance(step.get("run"), str)
        )

        deploy_steps = jobs["deploy"]["steps"]
        deploy_step_names = [step.get("name", "") for step in deploy_steps]

        self.assertIn("Compile repository Python", [step.get("name", "") for step in jobs["lint"]["steps"]])
        self.assertIn("Run backend tests", contract_step_names)
        self.assertIn("Run Databricks bundle validation helper", contract_step_names)
        self.assertIn("Run Databricks helper tests", contract_step_names)
        self.assertIn("python3 databricks/validate_bundle.py", contract_run_commands)
        self.assertIn("python3 -m unittest databricks.test_validate_bundle", contract_run_commands)
        self.assertIn("Check deploy prerequisites", deploy_step_names)
        self.assertIn("Validate bundle", deploy_step_names)
        self.assertIn("Deploy bundle", deploy_step_names)


if __name__ == "__main__":
    unittest.main()
