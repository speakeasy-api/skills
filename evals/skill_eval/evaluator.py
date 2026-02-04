"""Claude Agent SDK integration for workspace-based skill evaluation.

Uses the SDK's native skill loading mechanism to evaluate whether skills
effectively guide the agent to use the Speakeasy CLI correctly.

All skills are installed in each workspace's .claude/skills/ directory,
matching a real Claude Code environment where all skills are available.
"""

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
)

from .workspace import Workspace
from .assessor import WorkspaceAssessor


@dataclass
class AgentEvent:
    """Event emitted during agent execution."""
    timestamp: datetime
    type: str  # "thinking" | "text" | "tool_use" | "turn" | "result"
    content: Any


class ExecutionObserver(Protocol):
    """Protocol for observing agent execution events."""

    async def on_event(self, event: AgentEvent) -> None:
        """Called when an event occurs during agent execution."""
        ...


class SkillEvaluator:
    """Evaluates skills using the SDK's native skill loading mechanism."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.skills_dir = Path(__file__).parent.parent.parent / "skills"

    def _setup_skills_in_workspace(self, workspace: Workspace, skill_names: list[str] | None = None) -> int:
        """Copy skills to workspace's .claude/skills/ directory for SDK discovery.

        Args:
            workspace: The workspace to install skills into
            skill_names: Optional list of specific skill names to install. If None, installs all skills.

        Returns the number of skills installed.
        """
        skills_installed = 0
        target_skills_dir = workspace.base_dir / ".claude" / "skills"
        target_skills_dir.mkdir(parents=True, exist_ok=True)

        # Find all skill directories (those containing SKILL.md)
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            # If specific skills requested, only install those
            if skill_names is not None and skill_dir.name not in skill_names:
                continue

            # Copy skill to workspace
            target_skill_dir = target_skills_dir / skill_dir.name
            target_skill_dir.mkdir(parents=True, exist_ok=True)

            for item in skill_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, target_skill_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, target_skill_dir / item.name, dirs_exist_ok=True)

            skills_installed += 1

        return skills_installed

    async def evaluate(
        self,
        test: dict[str, Any],
        with_skills: bool = True,
        skill_names: list[str] | None = None,
        observer: ExecutionObserver | None = None,
    ) -> dict[str, Any]:
        """Evaluate a single test case using a real workspace.

        Args:
            test: Test case definition
            with_skills: If True, install skills in workspace. If False, run without skills.
            skill_names: Optional list of specific skill names to install. If None and with_skills=True, installs all.
            observer: Optional observer for real-time event streaming
        """
        test_type = test.get("type", "generation")

        handlers = {
            "generation": self._eval_generation,
            "overlay": self._eval_overlay,
            "diagnosis": self._eval_diagnosis,
            "workflow": self._eval_workflow,
        }

        handler = handlers.get(test_type, self._eval_generation)
        return await handler(test, with_skills=with_skills, skill_names=skill_names, observer=observer)

    async def _run_agent(
        self,
        workspace: Workspace,
        task: str,
        max_turns: int = 10,
        observer: ExecutionObserver | None = None,
    ) -> tuple[str, list[dict], float | None, int]:
        """Run agent with all skills loaded from workspace .claude/skills/ directory.

        Args:
            workspace: The workspace to run the agent in
            task: The task prompt to send to the agent
            max_turns: Maximum number of turns before stopping
            observer: Optional observer for real-time event streaming

        Returns:
            tuple of (agent_output, tool_calls, total_cost, turns_used)
        """
        options = ClaudeAgentOptions(
            model=self.model,
            max_turns=max_turns,
            cwd=workspace.base_dir,
            # Load skills from the workspace's .claude/skills/ directory
            setting_sources=["project"],
            # Use standard Claude Code tools plus Skill tool for skill invocation
            allowed_tools=["Skill", "Bash", "Read", "Write", "Glob", "Grep"],
            # Auto-accept file edits and bash commands in the workspace
            permission_mode="bypassPermissions",
        )

        tool_calls = []
        agent_output = ""
        total_cost = None
        turns_used = 0

        async with ClaudeSDKClient(options=options) as client:
            await client.query(task)

            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    turns_used += 1
                    if observer:
                        await observer.on_event(AgentEvent(
                            timestamp=datetime.now(),
                            type="turn",
                            content={"turn": turns_used, "max_turns": max_turns},
                        ))
                    for block in msg.content:
                        if isinstance(block, ThinkingBlock):
                            if observer:
                                await observer.on_event(AgentEvent(
                                    timestamp=datetime.now(),
                                    type="thinking",
                                    content=block.thinking,
                                ))
                        elif isinstance(block, TextBlock):
                            agent_output += block.text
                            if observer:
                                await observer.on_event(AgentEvent(
                                    timestamp=datetime.now(),
                                    type="text",
                                    content=block.text,
                                ))
                        elif isinstance(block, ToolUseBlock):
                            tool_call = {
                                "name": block.name,
                                "input": self._summarize_tool_input(block.name, block.input),
                            }
                            tool_calls.append(tool_call)
                            if observer:
                                await observer.on_event(AgentEvent(
                                    timestamp=datetime.now(),
                                    type="tool_use",
                                    content=tool_call,
                                ))
                elif isinstance(msg, ResultMessage):
                    if msg.total_cost_usd:
                        total_cost = msg.total_cost_usd
                    if observer:
                        await observer.on_event(AgentEvent(
                            timestamp=datetime.now(),
                            type="result",
                            content={"cost_usd": total_cost, "turns_used": turns_used},
                        ))

        return agent_output, tool_calls, total_cost, turns_used

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

    def _extract_skill_invocations(self, tool_calls: list[dict]) -> list[str]:
        """Extract which skills were invoked from Skill tool calls."""
        skills = []
        for tc in tool_calls:
            if tc["name"] == "Skill":
                skill_input = tc.get("input", {})
                if isinstance(skill_input, dict):
                    skill_name = skill_input.get("skill", skill_input.get("name", "unknown"))
                    skills.append(skill_name)
        return skills

    def _find_sdk_dir(self, workspace_dir: Path, target: str) -> Path | None:
        """Find the SDK output directory in a workspace."""
        # Check common SDK output patterns
        sdk_patterns = [
            f"sdk/{target}",
            f"sdks/{target}",
            target,
            "sdk",
        ]
        for pattern in sdk_patterns:
            candidate = workspace_dir / pattern
            if candidate.is_dir():
                return candidate

        # Check if SDK was generated at workspace root (common for quickstart)
        gen_yaml = workspace_dir / ".speakeasy" / "gen.yaml"
        if gen_yaml.exists():
            # Check for language-specific indicators at root
            indicators = {
                "typescript": ["package.json", "src"],
                "python": ["pyproject.toml", "setup.py", "src"],
                "go": ["go.mod"],
                "java": ["pom.xml", "build.gradle"],
                "terraform": ["go.mod"],
            }
            for indicator in indicators.get(target, []):
                if (workspace_dir / indicator).exists():
                    return workspace_dir

        return None

    async def _eval_generation(
        self,
        test: dict[str, Any],
        with_skills: bool = True,
        skill_names: list[str] | None = None,
        observer: ExecutionObserver | None = None,
    ) -> dict[str, Any]:
        """Evaluate SDK generation with skill-guided agent."""
        skill_name = test["skill"]  # The skill we expect to be used
        spec_content = test.get("spec")
        target = test.get("target", "typescript")
        task = test.get("task", f"Generate a {target} SDK from the OpenAPI spec at openapi.yaml using the Speakeasy CLI")
        max_turns = test.get("max_turns", 10)

        if not spec_content:
            return {"skill": skill_name, "type": "generation", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)

            # Setup skills in workspace for SDK discovery (only if with_skills=True)
            skills_installed = self._setup_skills_in_workspace(workspace, skill_names) if with_skills else 0

            try:
                agent_output, tool_calls, cost, turns_used = await self._run_agent(
                    workspace, task, max_turns=max_turns, observer=observer
                )
            except Exception as e:
                return {"skill": skill_name, "type": "generation", "passed": False, "error": str(e)}

            # Check which skills were invoked
            skills_invoked = self._extract_skill_invocations(tool_calls)
            expected_skill_invoked = skill_name in skills_invoked

            # Check if speakeasy commands were used
            speakeasy_commands = self._extract_speakeasy_commands(tool_calls)

            # Assess the result
            assessor = WorkspaceAssessor(workspace.base_dir)
            assessment = assessor.assess_generation(target)

            # Add SDK compilation check if generation passed basic checks
            # Mode: "quick" (2-15s) or "full" (30-120s)
            compilation_result = None
            if assessment.passed and test.get("verify_compilation", True):
                sdk_dir = self._find_sdk_dir(workspace.base_dir, target)
                if sdk_dir:
                    # Use quick mode by default, full mode if explicitly requested
                    compile_mode = test.get("compile_mode", "quick")
                    compilation = assessor.assess_sdk_compilation(sdk_dir, target, mode=compile_mode)
                    compilation_result = {
                        "passed": compilation.passed,
                        "checks": compilation.checks,
                        "summary": compilation.summary,
                        "mode": compile_mode,
                    }
                    # Compilation failure doesn't fail the whole test by default
                    # but is tracked separately for trend analysis
                    for check in compilation.checks:
                        assessment.checks.append({
                            **check,
                            "name": f"compile_{check['name']}",
                        })

            # Extended generation checks
            extended_results = {}

            # Verify workflow.yaml structure
            if test.get("verify_workflow", True):
                workflow_assessment = assessor.assess_workflow_structure()
                extended_results["workflow"] = {
                    "passed": workflow_assessment.passed,
                    "checks": workflow_assessment.checks,
                }
                for check in workflow_assessment.checks:
                    if check["name"] not in ["workflow_exists", "valid_yaml"]:  # Already in base
                        assessment.checks.append({
                            **check,
                            "name": f"workflow_{check['name']}",
                        })

            # Verify gen.yaml configuration
            if test.get("verify_gen_yaml", True):
                gen_assessment = assessor.assess_gen_yaml(target)
                extended_results["gen_yaml"] = {
                    "passed": gen_assessment.passed,
                    "checks": gen_assessment.checks,
                }
                for check in gen_assessment.checks:
                    assessment.checks.append({
                        **check,
                        "name": f"gen_{check['name']}",
                    })

            # Check hooks if requested
            if test.get("verify_hooks", False):
                hooks_assessment = assessor.assess_hooks_preserved(target)
                extended_results["hooks"] = {
                    "passed": hooks_assessment.passed,
                    "checks": hooks_assessment.checks,
                }
                for check in hooks_assessment.checks:
                    assessment.checks.append({
                        **check,
                        "name": f"hooks_{check['name']}",
                    })

            # Check MCP configuration if requested
            if test.get("verify_mcp", False):
                mcp_assessment = assessor.assess_mcp_config()
                extended_results["mcp"] = {
                    "passed": mcp_assessment.passed,
                    "checks": mcp_assessment.checks,
                }
                for check in mcp_assessment.checks:
                    assessment.checks.append({
                        **check,
                        "name": f"mcp_{check['name']}",
                    })

            # Check test generation if requested
            if test.get("verify_tests", False):
                test_assessment = assessor.assess_test_generation()
                extended_results["tests"] = {
                    "passed": test_assessment.passed,
                    "checks": test_assessment.checks,
                }
                for check in test_assessment.checks:
                    assessment.checks.append({
                        **check,
                        "name": f"test_{check['name']}",
                    })

            # Check multi-target workflow if requested
            if test.get("verify_multi_target", False):
                multi_assessment = assessor.assess_multi_target_workflow()
                extended_results["multi_target"] = {
                    "passed": multi_assessment.passed,
                    "checks": multi_assessment.checks,
                }
                for check in multi_assessment.checks:
                    assessment.checks.append({
                        **check,
                        "name": f"multi_{check['name']}",
                    })

            return {
                "skill": skill_name,
                "type": "generation",
                "target": target,
                "passed": assessment.passed,
                "checks": assessment.checks,
                "summary": assessment.summary,
                "compilation": compilation_result,
                "extended": extended_results,
                "skills_installed": skills_installed,
                "skills_invoked": skills_invoked,
                "expected_skill_invoked": expected_skill_invoked,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "changes": workspace.get_changes(),
                "cost_usd": cost,
                "turns_used": turns_used,
                "max_turns": max_turns,
            }

    async def _eval_overlay(
        self,
        test: dict[str, Any],
        with_skills: bool = True,
        skill_names: list[str] | None = None,
        observer: ExecutionObserver | None = None,
    ) -> dict[str, Any]:
        """Evaluate overlay creation with skill-guided agent."""
        skill_name = test["skill"]
        spec_content = test.get("spec")
        task = test.get("task", "Create an overlay to improve the SDK naming for the OpenAPI spec at openapi.yaml")
        expected_extensions = test.get("expected_extensions", [])
        max_turns = test.get("max_turns", 10)

        if not spec_content:
            return {"skill": skill_name, "type": "overlay", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)
            skills_installed = self._setup_skills_in_workspace(workspace, skill_names) if with_skills else 0

            try:
                agent_output, tool_calls, cost, turns_used = await self._run_agent(
                    workspace, task, max_turns=max_turns, observer=observer
                )
            except Exception as e:
                return {"skill": skill_name, "type": "overlay", "passed": False, "error": str(e)}

            skills_invoked = self._extract_skill_invocations(tool_calls)
            expected_skill_invoked = skill_name in skills_invoked
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
                    "skills_installed": skills_installed,
                    "skills_invoked": skills_invoked,
                    "expected_skill_invoked": expected_skill_invoked,
                    "tool_calls": tool_calls,
                    "speakeasy_commands": speakeasy_commands,
                    "cost_usd": cost,
                }

            assessor = WorkspaceAssessor(workspace.base_dir)
            all_passed = True
            overlay_results = []

            spec_path = workspace.base_dir / "openapi.yaml"

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

                # Phase 1: Run speakeasy overlay validate
                validation = assessor.assess_overlay_validation(overlay_path, spec_path)
                for check in validation.checks:
                    if check["name"] != "overlay_exists":  # Already checked
                        assessment.checks.append(check)
                        if not check["passed"]:
                            assessment.passed = False

                # Check for pagination-specific validation if pagination extension expected
                if "x-speakeasy-pagination" in expected_extensions:
                    pagination_assessment = assessor.assess_pagination_config(overlay_path)
                    for check in pagination_assessment.checks:
                        if check["name"] not in ["overlay_exists", "valid_yaml"]:  # Already checked
                            assessment.checks.append(check)
                            if not check["passed"]:
                                assessment.passed = False

                # Check for retries-specific validation if retries extension expected
                if "x-speakeasy-retries" in expected_extensions:
                    retries_assessment = assessor.assess_retries_config(overlay_path)
                    for check in retries_assessment.checks:
                        if check["name"] not in ["overlay_exists", "valid_yaml"]:  # Already checked
                            assessment.checks.append(check)
                            if not check["passed"]:
                                assessment.passed = False

                # Check for naming-specific validation if naming extensions expected
                if "x-speakeasy-name-override" in expected_extensions or "x-speakeasy-group" in expected_extensions:
                    naming_assessment = assessor.assess_naming_overlay(overlay_path)
                    for check in naming_assessment.checks:
                        if check["name"] not in ["overlay_exists", "valid_yaml"]:  # Already checked
                            assessment.checks.append(check)
                            if not check["passed"]:
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
                "skills_installed": skills_installed,
                "skills_invoked": skills_invoked,
                "expected_skill_invoked": expected_skill_invoked,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "cost_usd": cost,
                "turns_used": turns_used,
                "max_turns": max_turns,
            }

    async def _eval_diagnosis(
        self,
        test: dict[str, Any],
        with_skills: bool = True,
        skill_names: list[str] | None = None,
        observer: ExecutionObserver | None = None,
    ) -> dict[str, Any]:
        """Evaluate diagnosis of generation issues."""
        skill_name = test["skill"]
        spec_content = test.get("spec")
        expected_issues = test.get("expected_issues", [])
        task = test.get("task", "Analyze the OpenAPI spec at openapi.yaml and diagnose any issues that would affect SDK generation quality")
        max_turns = test.get("max_turns", 10)

        if not spec_content:
            return {"skill": skill_name, "type": "diagnosis", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)
            skills_installed = self._setup_skills_in_workspace(workspace, skill_names) if with_skills else 0

            try:
                agent_output, tool_calls, cost, turns_used = await self._run_agent(
                    workspace, task, max_turns=max_turns, observer=observer
                )
            except Exception as e:
                return {"skill": skill_name, "type": "diagnosis", "passed": False, "error": str(e)}

            skills_invoked = self._extract_skill_invocations(tool_calls)
            expected_skill_invoked = skill_name in skills_invoked
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
                "skills_installed": skills_installed,
                "skills_invoked": skills_invoked,
                "expected_skill_invoked": expected_skill_invoked,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "output_length": len(agent_output),
                "cost_usd": cost,
                "turns_used": turns_used,
                "max_turns": max_turns,
            }

    async def _eval_workflow(
        self,
        test: dict[str, Any],
        with_skills: bool = True,
        skill_names: list[str] | None = None,
        observer: ExecutionObserver | None = None,
    ) -> dict[str, Any]:
        """Evaluate a complete workflow (multi-step task)."""
        skill_name = test["skill"]
        spec_content = test.get("spec")
        steps = test.get("steps", [])
        task = test.get("task", "Complete the SDK generation workflow for the OpenAPI spec at openapi.yaml")
        max_turns = test.get("max_turns", 10)

        if not spec_content:
            return {"skill": skill_name, "type": "workflow", "passed": False, "error": "No spec provided"}

        with Workspace() as workspace:
            workspace.setup(spec_content)
            skills_installed = self._setup_skills_in_workspace(workspace, skill_names) if with_skills else 0

            try:
                agent_output, tool_calls, cost, turns_used = await self._run_agent(
                    workspace, task, max_turns=max_turns, observer=observer
                )
            except Exception as e:
                return {"skill": skill_name, "type": "workflow", "passed": False, "error": str(e)}

            skills_invoked = self._extract_skill_invocations(tool_calls)
            expected_skill_invoked = skill_name in skills_invoked
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
                "skills_installed": skills_installed,
                "skills_invoked": skills_invoked,
                "expected_skill_invoked": expected_skill_invoked,
                "tool_calls": tool_calls,
                "speakeasy_commands": speakeasy_commands,
                "changes": workspace.get_changes(),
                "cost_usd": cost,
                "turns_used": turns_used,
                "max_turns": max_turns,
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
