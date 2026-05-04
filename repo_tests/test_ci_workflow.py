from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class CIWorkflowTests(unittest.TestCase):
    def test_workflow_includes_bundle_validation_and_backend_tests(self) -> None:
        workflow_path = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        jobs = workflow["jobs"]
        self.assertEqual(set(jobs.keys()), {"lint", "contract", "deploy", "deploy_apps", "uc_grants", "train_models"})
        triggers = workflow.get("on")
        if triggers is None:
            triggers = workflow.get(True)
        self.assertIsNotNone(triggers)
        self.assertIn("workflow_dispatch", triggers)
        self.assertIn("confirm_deploy", triggers["workflow_dispatch"]["inputs"])

        contract_steps = jobs["contract"]["steps"]
        contract_step_names = [step.get("name", "") for step in contract_steps]
        contract_run_commands = "\n".join(
            step.get("run", "") for step in contract_steps if isinstance(step.get("run"), str)
        )

        deploy_steps = jobs["deploy"]["steps"]
        deploy_step_names = [step.get("name", "") for step in deploy_steps]
        deploy_run_commands = "\n".join(
            step.get("run", "") for step in deploy_steps if isinstance(step.get("run"), str)
        )

        self.assertIn("Compile repository Python", [step.get("name", "") for step in jobs["lint"]["steps"]])
        self.assertIn("Run backend tests", contract_step_names)
        self.assertIn("Run Databricks bundle validation helper", contract_step_names)
        self.assertIn("Run Databricks helper tests", contract_step_names)
        self.assertIn("python3 databricks/tools/validate_bundle.py", contract_run_commands)
        self.assertIn("python3 -m unittest databricks.tests.test_validate_bundle", contract_run_commands)
        self.assertIn("python3 -m unittest databricks.tests.test_live_sql_validation", contract_run_commands)
        self.assertEqual(jobs["deploy"]["needs"], "contract")
        self.assertIn("deploy", jobs["deploy_apps"]["needs"])
        self.assertIn("deploy", jobs["uc_grants"]["needs"])
        self.assertIn("deploy", jobs["train_models"]["needs"])
        self.assertEqual(jobs["deploy"]["if"], "github.event_name == 'workflow_dispatch' && inputs.confirm_deploy")
        self.assertIn("Install deploy dependencies", deploy_step_names)
        self.assertIn("python3 -m pip install --upgrade pip pyyaml", deploy_run_commands)
        self.assertIn("Install Databricks CLI", deploy_step_names)
        cli_step = next(s for s in deploy_steps if s.get("name") == "Install Databricks CLI")
        self.assertIn("databricks/setup-cli", cli_step.get("uses", ""))
        self.assertIn("Check deploy prerequisites", deploy_step_names)
        self.assertIn("Validate bundle", deploy_step_names)
        self.assertIn("Deploy bundle", deploy_step_names)
        self.assertIn("Run live SQL validation", deploy_step_names)
        self.assertIn("Upload live SQL validation artifact", deploy_step_names)


if __name__ == "__main__":
    unittest.main()
