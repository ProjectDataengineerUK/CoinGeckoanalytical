from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class TerraformWorkflowTests(unittest.TestCase):
    def test_terraform_workflow_has_plan_and_apply_jobs(self) -> None:
        workflow_path = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "terraform.yml"
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        jobs = workflow["jobs"]

        self.assertEqual(set(jobs.keys()), {"dev-plan", "dev-apply"})
        triggers = workflow.get("on")
        if triggers is None:
            triggers = workflow.get(True)
        self.assertIsNotNone(triggers)
        self.assertIn("workflow_dispatch", triggers)

        plan_steps = jobs["dev-plan"]["steps"]
        plan_step_names = [step.get("name", "") for step in plan_steps]
        plan_run_commands = "\n".join(step.get("run", "") for step in plan_steps if isinstance(step.get("run"), str))

        apply_steps = jobs["dev-apply"]["steps"]
        apply_step_names = [step.get("name", "") for step in apply_steps]
        apply_run_commands = "\n".join(step.get("run", "") for step in apply_steps if isinstance(step.get("run"), str))

        self.assertIn("Set up Terraform", plan_step_names)
        self.assertIn("Terraform init", plan_step_names)
        self.assertIn("Terraform validate", plan_step_names)
        self.assertIn("Terraform plan dev", plan_step_names)
        self.assertIn("Upload Terraform dev plan artifact", plan_step_names)
        self.assertIn("terraform plan -out=tfplan", plan_run_commands)
        self.assertIn("Terraform apply dev", apply_step_names)
        self.assertIn("Download Terraform dev plan artifact", apply_step_names)
        self.assertIn("terraform apply -auto-approve tfplan", apply_run_commands)


if __name__ == "__main__":
    unittest.main()
