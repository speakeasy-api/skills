"""Claude Agent SDK integration for workspace-based skill evaluation.

Uses standard Claude Code tools (Bash, Read, Write, Glob, Grep) to evaluate
whether skills effectively guide the agent to use the Speakeasy CLI correctly.
"""

import asyncio
import re
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

from .workspace import Workspace
from .assessor import WorkspaceAssessor


class SkillEvaluator:
    """Evaluates skills using workspace-based agentic workflows with standard tools."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.skills_dir = Path(__file__).parent.parent.parent / "skills"

    def load_skill(self, skill_name: str) -> str | None:
        """Load skill content from SKILL.md file."""
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        return skill_path.read_text() if skill_path.exists() else None

    async def evaluate(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a single test case using a real workspace."""
        test_type = test.get("type", "generation")

        handlers = {
            "generation": self._eval_generation,
            "overlay": self._eval_overlay,
            "diagnosis": self._eval_diagnosis,
            "workflow": self._eval_workflow,
        }

        handler = handlers.get(test_type, self._eval_generation)
        return await handler(test)

    async def _run_agent(
        self,
        workspace: Workspace,
        task: str,
        skill_content: str | None,
        max_turns: int = 10,
    ) -> tuple[str, list[dict], float | None]:
        """Run agent with standard Claude Code tools in the workspace."""
        system_prompt = self._build_system_prompt(skill_content, workspace.base_dir)

        options = ClaudeAgentOptions(
            model=self.model,
            system_prompt=system_prompt,
            max_turns=max_turns,
            cwd=workspace.base_dir,
            # Use standard Claude Code tools
            allowed_tools=["Bash", "Read", "Write", "Glob", "Grep"],
            # Auto-accept file edits and bash commands in the workspace
            permission_mode="bypassPermissions",
        )

        tool_calls = []
        agent_output = ""
        total_cost = None

        async with ClaudeSDKClient(options=options) as client:
            await client.query(task)

            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            agent_output += block.text
                        elif isinstance(block, ToolUseBlock):
                            tool_calls.append({
                                "name": block.name,
                                "input": self._summarize_tool_input(block.name, block.input),
                            })
                elif isinstance(msg, ResultMessage):
                    if msg.total_cost_usd:
                        total_cost = msg.total_cost_usd

        return agent_output, tool_calls, total_cost

    def _summarize_tool_input(self, tool_name: str, tool_input: Any) -> Any:
        """Summarize tool input for logging (truncate long content)."""
        if isinstance(tool_input, dict):
            result = {}
            for k, v in tool_input.items():
                if isinstance(v, str) and len(v) > 200:
                    result[k] = v[:200] + "..."
                else:
                    result[k] = v
            return result
        return tool_input

    async def _eval_generation(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate SDK generation with a skill-guided agent."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        target = test.get("target", "typescript")
        task = test.get("task", f"Generate a {target} SDK from the OpenAPI spec at openapi.yaml using the Speakeasy CLI")

        if not spec_content:
            return {"skill": skill_name, "type": "generation", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)

            try:
                agent_output, tool_calls, cost = await self._run_agent(
                    workspace, task, skill_content, max_turns=10
                )
            except Exception as e:
                return {"skill": skill_name, "type": "generation", "passed": False, "error": str(e)}

            # Check if speakeasy commands were used
            speakeasy_commands = self._extract_speakeasy_commands(tool_calls)

            # Assess the result
            assessor = WorkspaceAssessor(workspace.base_dir)
            assessment = assessor.assess_generation(target)

            return {
                "skill": skill_name,
                "type": "generation",
                "target": target,
                "passed": assessment.passed,
                "checks": assessment.checks,
                "summary": assessment.summary,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "changes": workspace.get_changes(),
                "cost_usd": cost,
            }

    async def _eval_overlay(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate overlay creation with a skill-guided agent."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        task = test.get("task", "Create an overlay to improve the SDK naming for the OpenAPI spec at openapi.yaml")
        expected_extensions = test.get("expected_extensions", [])

        if not spec_content:
            return {"skill": skill_name, "type": "overlay", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)

            try:
                agent_output, tool_calls, cost = await self._run_agent(
                    workspace, task, skill_content, max_turns=10
                )
            except Exception as e:
                return {"skill": skill_name, "type": "overlay", "passed": False, "error": str(e)}

            speakeasy_commands = self._extract_speakeasy_commands(tool_calls)

            # Find and assess overlay files
            overlay_files = workspace.list_files("**/*.yaml")
            overlay_files = [f for f in overlay_files if "overlay" in f.lower() or f.startswith("overlays/")]

            if not overlay_files:
                # Check if overlay content was written to any yaml file
                all_yaml = workspace.list_files("**/*.yaml")
                for f in all_yaml:
                    content = workspace.read_file(f) or ""
                    if "overlay:" in content and "actions:" in content:
                        overlay_files.append(f)

            if not overlay_files:
                return {
                    "skill": skill_name,
                    "type": "overlay",
                    "passed": False,
                    "error": "No overlay file created",
                    "tool_calls": tool_calls,
                    "speakeasy_commands": speakeasy_commands,
                    "cost_usd": cost,
                }

            assessor = WorkspaceAssessor(workspace.base_dir)
            all_passed = True
            overlay_results = []

            for overlay_file in overlay_files:
                overlay_path = workspace.base_dir / overlay_file
                assessment = assessor.assess_overlay(overlay_path)

                # Check for expected extensions
                if expected_extensions:
                    content = overlay_path.read_text()
                    for ext in expected_extensions:
                        found = ext in content
                        assessment.add_check(f"has_{ext}", found, f"{ext} {'found' if found else 'not found'}")
                        if not found:
                            assessment.passed = False

                overlay_results.append({
                    "file": overlay_file,
                    "passed": assessment.passed,
                    "checks": assessment.checks,
                })
                if not assessment.passed:
                    all_passed = False

            return {
                "skill": skill_name,
                "type": "overlay",
                "passed": all_passed,
                "overlays": overlay_results,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "cost_usd": cost,
            }

    async def _eval_diagnosis(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate diagnosis of generation issues."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        expected_issues = test.get("expected_issues", [])
        task = test.get("task", "Analyze the OpenAPI spec at openapi.yaml and diagnose any issues that would affect SDK generation quality")

        if not spec_content:
            return {"skill": skill_name, "type": "diagnosis", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)

            try:
                agent_output, tool_calls, cost = await self._run_agent(
                    workspace, task, skill_content, max_turns=10
                )
            except Exception as e:
                return {"skill": skill_name, "type": "diagnosis", "passed": False, "error": str(e)}

            speakeasy_commands = self._extract_speakeasy_commands(tool_calls)

            # Check if expected issues were identified
            checks = []
            for issue in expected_issues:
                found = issue.lower() in agent_output.lower()
                checks.append({"issue": issue, "identified": found})

            passed = all(c["identified"] for c in checks) if checks else len(agent_output) > 100

            return {
                "skill": skill_name,
                "type": "diagnosis",
                "passed": passed,
                "expected_issues": checks,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "output_length": len(agent_output),
                "cost_usd": cost,
            }

    async def _eval_workflow(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a complete workflow (multi-step task)."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        steps = test.get("steps", [])
        task = test.get("task", "Complete the SDK generation workflow for the OpenAPI spec at openapi.yaml")

        if not spec_content:
            return {"skill": skill_name, "type": "workflow", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)

            try:
                agent_output, tool_calls, cost = await self._run_agent(
                    workspace, task, skill_content, max_turns=15
                )
            except Exception as e:
                return {"skill": skill_name, "type": "workflow", "passed": False, "error": str(e)}

            speakeasy_commands = self._extract_speakeasy_commands(tool_calls)

            # Verify expected steps were performed
            step_results = []
            for step in steps:
                step_name = step.get("name", "")
                required_command = step.get("command")  # e.g., "speakeasy lint"
                required_file = step.get("creates_file")

                step_passed = True
                details = []

                if required_command:
                    cmd_used = any(required_command in cmd for cmd in speakeasy_commands)
                    step_passed = step_passed and cmd_used
                    details.append(f"command '{required_command}': {'used' if cmd_used else 'not used'}")

                if required_file:
                    file_exists = workspace.file_exists(required_file)
                    step_passed = step_passed and file_exists
                    details.append(f"file {required_file}: {'created' if file_exists else 'missing'}")

                step_results.append({
                    "name": step_name,
                    "passed": step_passed,
                    "details": "; ".join(details),
                })

            all_passed = all(s["passed"] for s in step_results) if step_results else True

            return {
                "skill": skill_name,
                "type": "workflow",
                "passed": all_passed,
                "steps": step_results,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "changes": workspace.get_changes(),
                "cost_usd": cost,
            }

    def _extract_speakeasy_commands(self, tool_calls: list[dict]) -> list[str]:
        """Extract speakeasy commands from Bash tool calls."""
        commands = []
        for tc in tool_calls:
            if tc["name"] == "Bash":
                cmd = tc.get("input", {})
                if isinstance(cmd, dict):
                    cmd = cmd.get("command", "")
                if isinstance(cmd, str) and "speakeasy" in cmd:
                    commands.append(cmd)
        return commands

    def _build_system_prompt(self, skill_content: str | None, workspace_dir: Path) -> str:
        """Build system prompt with skill context and workspace info."""
        prompt = f"""You are an expert at SDK generation using the Speakeasy CLI.

Your working directory is: {workspace_dir}
The workspace contains an OpenAPI spec at openapi.yaml.

You have access to standard tools: Bash, Read, Write, Glob, Grep.
Use the Bash tool to run speakeasy CLI commands.

Key speakeasy commands:
- speakeasy quickstart -s <spec> -t <target> -n <name> -p <package> --skip-interactive --output console
- speakeasy run --output console
- speakeasy lint openapi -s <spec> --non-interactive
- speakeasy suggest operation-ids -s <spec> -o <overlay>
- speakeasy overlay apply -s <spec> -o <overlay> --out <output>
- speakeasy overlay validate -o <overlay>
"""
        if skill_content:
            prompt += f"""
## Skill Context

The following skill provides guidance for this task:

{skill_content}
"""
        return prompt
