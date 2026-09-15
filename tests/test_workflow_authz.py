import unittest
import re
from pathlib import Path


WORKFLOWS = Path(__file__).parents[1] / ".github" / "workflows"


class WorkflowAuthorizationTests(unittest.TestCase):
    def test_privileged_workflows_are_manual_only(self):
        for path in WORKFLOWS.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            trigger_block = text.split("permissions:", 1)[0]
            self.assertIn("workflow_dispatch:", trigger_block, path.name)
            self.assertNotIn("issues:", trigger_block, path.name)
            self.assertNotIn("github.event.issue", text, path.name)
            self.assertNotIn("github.event_name == 'issues'", text, path.name)

    def test_issue_number_input_is_required_and_validated(self):
        for path in WORKFLOWS.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("issue_number:", text, path.name)
            self.assertIn("required: true", text, path.name)
            self.assertIn("ISSUE_NUMBER: ${{ inputs.issue_number }}", text, path.name)
            self.assertIn('[[ "$ISSUE_NUMBER" =~ ^[1-9][0-9]*$ ]]', text, path.name)
            steps = text.split("    steps:", 1)[1]
            self.assertTrue(
                steps.lstrip().startswith("- name: Validate dispatch input"),
                f"input validation must be the first step in {path.name}",
            )

    def test_workflow_tokens_are_not_sourced_from_issue_input(self):
        for path in WORKFLOWS.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("secrets.GITHUB_TOKEN", text, path.name)
            if "GH_TOKEN:" in text:
                self.assertIn("GH_TOKEN: ${{ github.token }}", text, path.name)

    def test_actions_are_pinned_to_full_commit_sha(self):
        for path in WORKFLOWS.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            for action_ref in re.findall(r"uses:\s+([^\s#]+)", text):
                self.assertRegex(action_ref, r"^[^@\s]+@[0-9a-f]{40}$", f"unpinned action in {path.name}")


if __name__ == "__main__":
    unittest.main()
