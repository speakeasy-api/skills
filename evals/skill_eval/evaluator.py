"""Claude Agent SDK integration for workspace-based skill evaluation."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)

from .workspace import Workspace
from .cli import SpeakeasyCLI, CLIResult
from .assessor import WorkspaceAssessor, AssessmentResult


class SkillEvaluator:
    """Evaluates skills using workspace-based agentic workflows."""

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

    async def _eval_generation(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate SDK generation with a skill-guided agent."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        target = test.get("target", "typescript")
        task = test.get("task", f"Generate a {target} SDK from the provided OpenAPI spec")

        if not spec_content:
            return {"skill": skill_name, "type": "generation", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            # Setup workspace with the spec
            workspace.setup(spec_content)
            cli = SpeakeasyCLI(workspace.base_dir)

            # Check CLI availability
            if not await cli.is_available():
                return {"skill": skill_name, "type": "generation", "passed": False, "error": "speakeasy CLI not available"}

            # Create tools for the agent
            tools = self._create_workspace_tools(workspace, cli)
            mcp_server = create_sdk_mcp_server(
                name="workspace",
                version="1.0.0",
                tools=tools,
            )

            # Build system prompt with skill context
            system_prompt = self._build_system_prompt(skill_content, workspace.base_dir)

            # Run the agent
            options = ClaudeAgentOptions(
                model=self.model,
                system_prompt=system_prompt,
                max_turns=10,
                mcp_servers={"workspace": mcp_server},
                allowed_tools=[
                    "mcp__workspace__read_file",
                    "mcp__workspace__write_file",
                    "mcp__workspace__list_files",
                    "mcp__workspace__speakeasy_quickstart",
                    "mcp__workspace__speakeasy_run",
                    "mcp__workspace__speakeasy_lint",
                    "mcp__workspace__speakeasy_suggest",
                    "mcp__workspace__speakeasy_overlay_apply",
                ],
            )

            tool_calls = []
            agent_output = ""

            try:
                async with ClaudeSDKClient(options=options) as client:
                    await client.query(task)

                    async for msg in client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            for block in msg.content:
                                if isinstance(block, TextBlock):
                                    agent_output += block.text
                                elif isinstance(block, ToolUseBlock):
                                    tool_calls.append({"name": block.name, "input": block.input})
            except Exception as e:
                return {"skill": skill_name, "type": "generation", "passed": False, "error": str(e)}

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
                "changes": workspace.get_changes(),
            }

    async def _eval_overlay(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate overlay creation with a skill-guided agent."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        task = test.get("task", "Create an overlay to improve the SDK naming")
        expected_extensions = test.get("expected_extensions", [])

        if not spec_content:
            return {"skill": skill_name, "type": "overlay", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)
            cli = SpeakeasyCLI(workspace.base_dir)

            if not await cli.is_available():
                return {"skill": skill_name, "type": "overlay", "passed": False, "error": "speakeasy CLI not available"}

            tools = self._create_workspace_tools(workspace, cli)
            mcp_server = create_sdk_mcp_server(
                name="workspace",
                version="1.0.0",
                tools=tools,
            )

            system_prompt = self._build_system_prompt(skill_content, workspace.base_dir)

            options = ClaudeAgentOptions(
                model=self.model,
                system_prompt=system_prompt,
                max_turns=10,
                mcp_servers={"workspace": mcp_server},
                allowed_tools=[
                    "mcp__workspace__read_file",
                    "mcp__workspace__write_file",
                    "mcp__workspace__list_files",
                    "mcp__workspace__speakeasy_lint",
                    "mcp__workspace__speakeasy_suggest",
                    "mcp__workspace__speakeasy_overlay_apply",
                    "mcp__workspace__speakeasy_overlay_validate",
                ],
            )

            tool_calls = []

            try:
                async with ClaudeSDKClient(options=options) as client:
                    await client.query(task)

                    async for msg in client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            for block in msg.content:
                                if isinstance(block, ToolUseBlock):
                                    tool_calls.append({"name": block.name, "input": block.input})
            except Exception as e:
                return {"skill": skill_name, "type": "overlay", "passed": False, "error": str(e)}

            # Find and assess overlay files
            overlay_files = workspace.list_files("**/*.yaml")
            overlay_files = [f for f in overlay_files if "overlay" in f.lower() or f.startswith("overlays/")]

            if not overlay_files:
                return {
                    "skill": skill_name,
                    "type": "overlay",
                    "passed": False,
                    "error": "No overlay file created",
                    "tool_calls": tool_calls,
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
            }

    async def _eval_diagnosis(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate diagnosis of generation failures."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        expected_issues = test.get("expected_issues", [])
        task = test.get("task", "Diagnose why SDK generation is failing and suggest fixes")

        if not spec_content:
            return {"skill": skill_name, "type": "diagnosis", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)
            cli = SpeakeasyCLI(workspace.base_dir)

            if not await cli.is_available():
                return {"skill": skill_name, "type": "diagnosis", "passed": False, "error": "speakeasy CLI not available"}

            tools = self._create_workspace_tools(workspace, cli)
            mcp_server = create_sdk_mcp_server(
                name="workspace",
                version="1.0.0",
                tools=tools,
            )

            system_prompt = self._build_system_prompt(skill_content, workspace.base_dir)

            options = ClaudeAgentOptions(
                model=self.model,
                system_prompt=system_prompt,
                max_turns=10,
                mcp_servers={"workspace": mcp_server},
                allowed_tools=[
                    "mcp__workspace__read_file",
                    "mcp__workspace__write_file",
                    "mcp__workspace__list_files",
                    "mcp__workspace__speakeasy_lint",
                    "mcp__workspace__speakeasy_run",
                ],
            )

            agent_output = ""
            tool_calls = []

            try:
                async with ClaudeSDKClient(options=options) as client:
                    await client.query(task)

                    async for msg in client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            for block in msg.content:
                                if isinstance(block, TextBlock):
                                    agent_output += block.text
                                elif isinstance(block, ToolUseBlock):
                                    tool_calls.append({"name": block.name, "input": block.input})
            except Exception as e:
                return {"skill": skill_name, "type": "diagnosis", "passed": False, "error": str(e)}

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
                "output_length": len(agent_output),
            }

    async def _eval_workflow(self, test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a complete workflow (multi-step task)."""
        skill_name = test["skill"]
        skill_content = self.load_skill(skill_name)
        spec_content = test.get("spec")
        steps = test.get("steps", [])
        task = test.get("task", "Complete the SDK generation workflow")

        if not spec_content:
            return {"skill": skill_name, "type": "workflow", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)
            cli = SpeakeasyCLI(workspace.base_dir)

            if not await cli.is_available():
                return {"skill": skill_name, "type": "workflow", "passed": False, "error": "speakeasy CLI not available"}

            tools = self._create_workspace_tools(workspace, cli)
            mcp_server = create_sdk_mcp_server(
                name="workspace",
                version="1.0.0",
                tools=tools,
            )

            system_prompt = self._build_system_prompt(skill_content, workspace.base_dir)

            options = ClaudeAgentOptions(
                model=self.model,
                system_prompt=system_prompt,
                max_turns=15,
                mcp_servers={"workspace": mcp_server},
                allowed_tools=[
                    "mcp__workspace__read_file",
                    "mcp__workspace__write_file",
                    "mcp__workspace__list_files",
                    "mcp__workspace__speakeasy_quickstart",
                    "mcp__workspace__speakeasy_run",
                    "mcp__workspace__speakeasy_lint",
                    "mcp__workspace__speakeasy_suggest",
                    "mcp__workspace__speakeasy_overlay_apply",
                    "mcp__workspace__speakeasy_overlay_validate",
                ],
            )

            tool_calls = []

            try:
                async with ClaudeSDKClient(options=options) as client:
                    await client.query(task)

                    async for msg in client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            for block in msg.content:
                                if isinstance(block, ToolUseBlock):
                                    tool_calls.append({"name": block.name, "input": block.input})
            except Exception as e:
                return {"skill": skill_name, "type": "workflow", "passed": False, "error": str(e)}

            # Verify expected steps were performed
            step_results = []
            for step in steps:
                step_name = step.get("name", "")
                required_tool = step.get("tool")
                required_file = step.get("creates_file")

                step_passed = True
                details = []

                if required_tool:
                    tool_used = any(required_tool in tc["name"] for tc in tool_calls)
                    step_passed = step_passed and tool_used
                    details.append(f"tool {required_tool}: {'used' if tool_used else 'not used'}")

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
                "changes": workspace.get_changes(),
            }

    def _build_system_prompt(self, skill_content: str | None, workspace_dir: Path) -> str:
        """Build system prompt with skill context and workspace info."""
        prompt = f"""You are an expert at SDK generation using the Speakeasy CLI.

You have access to a workspace at: {workspace_dir}
The workspace contains an OpenAPI spec at openapi.yaml.

Use the provided tools to accomplish the task. Always use --output console for speakeasy commands.
"""
        if skill_content:
            prompt += f"""
## Skill Context

The following skill provides guidance for this task:

{skill_content}
"""
        return prompt

    def _create_workspace_tools(self, workspace: Workspace, cli: SpeakeasyCLI) -> list:
        """Create MCP tools for workspace and CLI operations."""

        @tool("read_file", "Read a file from the workspace", {"path": str})
        async def read_file(args: dict[str, Any]) -> dict[str, Any]:
            content = workspace.read_file(args["path"])
            if content is None:
                return {"content": [{"type": "text", "text": f"File not found: {args['path']}"}], "is_error": True}
            return {"content": [{"type": "text", "text": content}]}

        @tool("write_file", "Write a file to the workspace", {"path": str, "content": str})
        async def write_file(args: dict[str, Any]) -> dict[str, Any]:
            workspace.write_file(args["path"], args["content"])
            return {"content": [{"type": "text", "text": f"Wrote {len(args['content'])} bytes to {args['path']}"}]}

        @tool("list_files", "List files in the workspace", {"pattern": str})
        async def list_files(args: dict[str, Any]) -> dict[str, Any]:
            files = workspace.list_files(args.get("pattern", "**/*"))
            return {"content": [{"type": "text", "text": "\n".join(files) if files else "No files found"}]}

        @tool("speakeasy_quickstart", "Initialize a new SDK project", {"target": str, "sdk_name": str, "package_name": str})
        async def speakeasy_quickstart(args: dict[str, Any]) -> dict[str, Any]:
            result = await cli.quickstart(
                spec="openapi.yaml",
                target=args["target"],
                sdk_name=args["sdk_name"],
                package_name=args["package_name"],
            )
            return {"content": [{"type": "text", "text": f"Exit code: {result.exit_code}\n{result.output}"}]}

        @tool("speakeasy_run", "Regenerate SDK from workflow configuration", {})
        async def speakeasy_run(args: dict[str, Any]) -> dict[str, Any]:
            result = await cli.generate()
            return {"content": [{"type": "text", "text": f"Exit code: {result.exit_code}\n{result.output}"}]}

        @tool("speakeasy_lint", "Lint an OpenAPI spec", {"spec": str})
        async def speakeasy_lint(args: dict[str, Any]) -> dict[str, Any]:
            result = await cli.lint(args.get("spec", "openapi.yaml"))
            return {"content": [{"type": "text", "text": f"Exit code: {result.exit_code}\n{result.output}"}]}

        @tool("speakeasy_suggest", "Generate AI-suggested operation IDs", {"spec": str, "output": str})
        async def speakeasy_suggest(args: dict[str, Any]) -> dict[str, Any]:
            result = await cli.suggest_operation_ids(
                args.get("spec", "openapi.yaml"),
                args.get("output", "overlays/naming.yaml"),
            )
            return {"content": [{"type": "text", "text": f"Exit code: {result.exit_code}\n{result.output}"}]}

        @tool("speakeasy_overlay_apply", "Apply an overlay to a spec", {"spec": str, "overlay": str, "output": str})
        async def speakeasy_overlay_apply(args: dict[str, Any]) -> dict[str, Any]:
            result = await cli.overlay_apply(
                args.get("spec", "openapi.yaml"),
                args["overlay"],
                args.get("output", "openapi-modified.yaml"),
            )
            return {"content": [{"type": "text", "text": f"Exit code: {result.exit_code}\n{result.output}"}]}

        @tool("speakeasy_overlay_validate", "Validate an overlay file", {"overlay": str})
        async def speakeasy_overlay_validate(args: dict[str, Any]) -> dict[str, Any]:
            result = await cli.overlay_validate(args["overlay"])
            return {"content": [{"type": "text", "text": f"Exit code: {result.exit_code}\n{result.output}"}]}

        return [
            read_file,
            write_file,
            list_files,
            speakeasy_quickstart,
            speakeasy_run,
            speakeasy_lint,
            speakeasy_suggest,
            speakeasy_overlay_apply,
            speakeasy_overlay_validate,
        ]
