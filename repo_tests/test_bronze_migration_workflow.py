from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class BronzeMigrationWorkflowTests(unittest.TestCase):
    def test_workflow_requires_manual_confirmation(self) -> None:
        workflow_path = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "bronze-migration.yml"
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

        triggers = workflow.get("on")
        if triggers is None:
            triggers = workflow.get(True)

        self.assertIsNotNone(triggers)
        self.assertIn("workflow_dispatch", triggers)
        self.assertIn("confirm_migration", triggers["workflow_dispatch"]["inputs"])

        jobs = workflow["jobs"]
        self.assertEqual(set(jobs.keys()), {"dev-migration"})
        self.assertEqual(jobs["dev-migration"]["if"], "github.event_name == 'workflow_dispatch' && inputs.confirm_migration")

        step_names = [step.get("name", "") for step in jobs["dev-migration"]["steps"]]
        run_commands = "\n".join(step.get("run", "") for step in jobs["dev-migration"]["steps"] if isinstance(step.get("run"), str))

        self.assertIn("Install Databricks CLI", step_names)
        self.assertIn("Validate bundle", step_names)
        self.assertIn("Deploy bundle", step_names)
        self.assertIn("Run Bronze migration", step_names)
        self.assertIn("databricks bundle run bronze_market_table_migration_job -t dev", run_commands)


if __name__ == "__main__":
    unittest.main()
