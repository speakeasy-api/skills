"""State assessment for evaluating SDK generation outcomes."""

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AssessmentResult:
    """Result of assessing a workspace state."""
    passed: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""

    def add_check(self, name: str, passed: bool, details: str = "") -> None:
        self.checks.append({"name": name, "passed": passed, "details": details})

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c["passed"])

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c["passed"])


class WorkspaceAssessor:
    """Assesses workspace state to determine SDK generation success."""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def assess_generation(self, target: str, expected_artifacts: list[str] | None = None) -> AssessmentResult:
        """Assess whether SDK generation succeeded."""
        result = AssessmentResult(passed=True)

        # Check workflow file exists
        workflow_path = self.workspace_dir / ".speakeasy" / "workflow.yaml"
        workflow_exists = workflow_path.exists()
        result.add_check(
            "workflow_exists",
            workflow_exists,
            f".speakeasy/workflow.yaml {'found' if workflow_exists else 'missing'}"
        )
        if not workflow_exists:
            result.passed = False

        # Check for SDK output directory
        # Speakeasy can generate SDK in subdirectories or directly in workspace root
        sdk_patterns = [
            f"sdk/{target}",
            f"sdks/{target}",
            target,
            "sdk",
        ]
        sdk_dir = None
        for pattern in sdk_patterns:
            candidate = self.workspace_dir / pattern
            if candidate.is_dir():
                sdk_dir = candidate
                break

        # Also check if SDK was generated directly in workspace root
        # (common for speakeasy quickstart)
        if sdk_dir is None:
            # Check for .speakeasy/gen.yaml which indicates SDK generation happened
            gen_yaml = self.workspace_dir / ".speakeasy" / "gen.yaml"
            if gen_yaml.exists():
                # Check for language-specific indicators at workspace root
                # Python/TypeScript: src/ directory
                # Go: go.mod file
                # Java: pom.xml or build.gradle
                src_dir = self.workspace_dir / "src"
                go_mod = self.workspace_dir / "go.mod"
                pyproject = self.workspace_dir / "pyproject.toml"
                package_json = self.workspace_dir / "package.json"
                if src_dir.is_dir() or go_mod.exists() or pyproject.exists() or package_json.exists():
                    sdk_dir = self.workspace_dir  # SDK was generated at root

        sdk_dir_exists = sdk_dir is not None
        result.add_check(
            "sdk_directory_exists",
            sdk_dir_exists,
            f"SDK output directory {'found at ' + (str(sdk_dir.relative_to(self.workspace_dir)) if sdk_dir != self.workspace_dir else '(workspace root)') if sdk_dir else 'not found'}"
        )
        if not sdk_dir_exists:
            result.passed = False
            return result

        # Check for expected artifacts
        if expected_artifacts:
            for artifact in expected_artifacts:
                artifact_path = sdk_dir / artifact
                exists = artifact_path.exists()
                result.add_check(
                    f"artifact_{artifact}",
                    exists,
                    f"{artifact} {'found' if exists else 'missing'}"
                )
                if not exists:
                    result.passed = False

        # Check for language-specific indicators
        language_checks = self._get_language_checks(target)
        for check_name, check_fn in language_checks.items():
            passed, details = check_fn(sdk_dir)
            result.add_check(check_name, passed, details)
            if not passed:
                result.passed = False

        result.summary = f"{result.passed_count}/{len(result.checks)} checks passed"
        return result

    def _get_language_checks(self, target: str) -> dict[str, Any]:
        """Get language-specific validation checks."""
        checks = {
            "typescript": {
                "has_package_json": lambda d: self._check_file_exists(d, "package.json"),
                "has_src_directory": lambda d: self._check_dir_exists(d, "src"),
                "has_sdk_entrypoint": lambda d: self._check_any_file_exists(d, ["src/index.ts", "src/sdk.ts"]),
            },
            "python": {
                "has_pyproject": lambda d: self._check_any_file_exists(d, ["pyproject.toml", "setup.py"]),
                "has_src_directory": lambda d: self._check_dir_exists(d, "src"),
                "has_init_py": lambda d: self._check_file_pattern(d, "**/__init__.py"),
            },
            "go": {
                "has_go_mod": lambda d: self._check_file_exists(d, "go.mod"),
                "has_go_files": lambda d: self._check_file_pattern(d, "*.go"),
            },
            "java": {
                "has_pom_or_gradle": lambda d: self._check_any_file_exists(d, ["pom.xml", "build.gradle"]),
                "has_src_main": lambda d: self._check_dir_exists(d, "src/main"),
            },
            "terraform": {
                "has_provider_go": lambda d: self._check_file_pattern(d, "**/provider.go"),
                "has_go_mod": lambda d: self._check_file_exists(d, "go.mod"),
            },
        }
        return checks.get(target, {})

    def _check_file_exists(self, base: Path, rel_path: str) -> tuple[bool, str]:
        path = base / rel_path
        exists = path.exists()
        return exists, f"{rel_path} {'found' if exists else 'missing'}"

    def _check_dir_exists(self, base: Path, rel_path: str) -> tuple[bool, str]:
        path = base / rel_path
        exists = path.is_dir()
        return exists, f"{rel_path}/ {'found' if exists else 'missing'}"

    def _check_any_file_exists(self, base: Path, paths: list[str]) -> tuple[bool, str]:
        for p in paths:
            if (base / p).exists():
                return True, f"Found {p}"
        return False, f"None of {paths} found"

    def _check_file_pattern(self, base: Path, pattern: str) -> tuple[bool, str]:
        matches = list(base.glob(pattern))
        if matches:
            return True, f"Found {len(matches)} files matching {pattern}"
        return False, f"No files matching {pattern}"

    def assess_overlay(self, overlay_path: Path) -> AssessmentResult:
        """Assess whether an overlay file is valid."""
        result = AssessmentResult(passed=True)

        # Check file exists
        exists = overlay_path.exists()
        result.add_check("overlay_exists", exists, f"{overlay_path.name} {'found' if exists else 'missing'}")
        if not exists:
            result.passed = False
            return result

        # Parse YAML
        try:
            content = yaml.safe_load(overlay_path.read_text())
            result.add_check("valid_yaml", True, "Valid YAML syntax")
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        # Check required fields
        has_overlay_version = "overlay" in content
        result.add_check("has_overlay_version", has_overlay_version, "'overlay' field " + ("present" if has_overlay_version else "missing"))

        has_info = "info" in content
        result.add_check("has_info", has_info, "'info' field " + ("present" if has_info else "missing"))

        has_actions = "actions" in content and isinstance(content.get("actions"), list)
        result.add_check("has_actions", has_actions, "'actions' field " + ("present with entries" if has_actions else "missing or empty"))

        if not all([has_overlay_version, has_info, has_actions]):
            result.passed = False

        # Check actions have required structure
        if has_actions:
            for i, action in enumerate(content["actions"]):
                has_target = "target" in action
                has_update = "update" in action or "remove" in action
                valid = has_target and has_update
                result.add_check(
                    f"action_{i}_valid",
                    valid,
                    f"Action {i}: " + ("valid" if valid else "missing target or update/remove")
                )
                if not valid:
                    result.passed = False

        result.summary = f"{result.passed_count}/{len(result.checks)} checks passed"
        return result

    def assess_lint_output(self, lint_output: str) -> AssessmentResult:
        """Assess lint output for errors and warnings."""
        result = AssessmentResult(passed=True)

        # Count errors and warnings
        error_count = len(re.findall(r"\berror\b", lint_output, re.IGNORECASE))
        warning_count = len(re.findall(r"\bwarning\b", lint_output, re.IGNORECASE))

        result.add_check("no_errors", error_count == 0, f"{error_count} errors found")
        result.add_check("warnings_only", True, f"{warning_count} warnings found")

        if error_count > 0:
            result.passed = False

        # Check for common issues
        common_issues = [
            (r"missing operationId", "missing_operation_ids"),
            (r"missing description", "missing_descriptions"),
            (r"invalid.*\$ref", "invalid_refs"),
        ]
        for pattern, name in common_issues:
            found = bool(re.search(pattern, lint_output, re.IGNORECASE))
            result.add_check(name, not found, f"{name.replace('_', ' ')} {'found' if found else 'not found'}")

        result.summary = f"{error_count} errors, {warning_count} warnings"
        return result

    def assess_naming(self, sdk_dir: Path, expected_methods: list[str] | None = None) -> AssessmentResult:
        """Assess SDK naming quality (method names, groupings)."""
        result = AssessmentResult(passed=True)

        # Find SDK source files
        source_files = list(sdk_dir.rglob("*.ts")) + list(sdk_dir.rglob("*.py")) + list(sdk_dir.rglob("*.go"))

        if not source_files:
            result.add_check("has_source_files", False, "No source files found")
            result.passed = False
            return result

        result.add_check("has_source_files", True, f"Found {len(source_files)} source files")

        # Check for poor naming patterns
        poor_patterns = [
            r"api_v\d+_\w+_\w+",  # api_v1_users_get style
            r"endpoint\d+",       # endpoint1, endpoint2
            r"operation\d+",      # operation1, operation2
        ]

        all_content = ""
        for f in source_files[:20]:  # Sample first 20 files
            try:
                all_content += f.read_text()
            except Exception:
                pass

        poor_naming_found = False
        for pattern in poor_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                poor_naming_found = True
                result.add_check(f"no_{pattern}", False, f"Poor naming pattern found: {pattern}")

        if not poor_naming_found:
            result.add_check("good_naming", True, "No poor naming patterns detected")

        # Check for expected methods if provided
        if expected_methods:
            for method in expected_methods:
                found = method in all_content
                result.add_check(f"has_method_{method}", found, f"Method {method} {'found' if found else 'not found'}")
                if not found:
                    result.passed = False

        result.summary = f"{result.passed_count}/{len(result.checks)} naming checks passed"
        return result

    def assess_sdk_compilation(self, sdk_dir: Path, target: str) -> AssessmentResult:
        """Assess whether the generated SDK compiles successfully.

        This is a Phase 1 assertion that verifies functional correctness
        beyond just file existence.
        """
        result = AssessmentResult(passed=True)

        # Language-specific build commands
        build_commands: dict[str, list[tuple[str, list[str]]]] = {
            "typescript": [
                ("install_deps", ["npm", "install"]),
                ("compile", ["npm", "run", "build"]),
            ],
            "python": [
                # Use pip install in editable mode to verify package is valid
                ("install_check", ["pip", "install", "-e", ".", "--dry-run"]),
            ],
            "go": [
                ("compile", ["go", "build", "./..."]),
            ],
            "java": [
                ("compile_maven", ["mvn", "compile", "-q"]),
            ],
            "terraform": [
                ("compile", ["go", "build", "./..."]),
            ],
        }

        commands = build_commands.get(target, [])
        if not commands:
            result.add_check(
                "build_commands_available",
                False,
                f"No build commands defined for target: {target}"
            )
            result.passed = False
            return result

        result.add_check("build_commands_available", True, f"Build commands defined for {target}")

        for step_name, cmd in commands:
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=sdk_dir,
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minute timeout per step
                )
                success = proc.returncode == 0
                details = f"exit code {proc.returncode}"
                if not success and proc.stderr:
                    # Truncate error output for readability
                    error_preview = proc.stderr[:200].replace('\n', ' ')
                    details += f": {error_preview}..."

                result.add_check(f"build_{step_name}", success, details)
                if not success:
                    result.passed = False
                    # Don't continue if a step fails
                    break

            except subprocess.TimeoutExpired:
                result.add_check(f"build_{step_name}", False, "timed out after 120s")
                result.passed = False
                break
            except FileNotFoundError as e:
                result.add_check(f"build_{step_name}", False, f"command not found: {e}")
                result.passed = False
                break
            except Exception as e:
                result.add_check(f"build_{step_name}", False, f"error: {e}")
                result.passed = False
                break

        result.summary = f"{result.passed_count}/{len(result.checks)} build checks passed"
        return result

    def assess_command_success(self, command: list[str], cwd: Path | None = None) -> AssessmentResult:
        """Assess whether a command executes successfully.

        Useful for running validation commands like:
        - speakeasy overlay validate -o overlay.yaml
        - speakeasy lint openapi -s spec.yaml
        """
        result = AssessmentResult(passed=True)
        work_dir = cwd or self.workspace_dir

        cmd_str = " ".join(command)
        try:
            proc = subprocess.run(
                command,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            success = proc.returncode == 0
            details = f"exit code {proc.returncode}"
            if not success:
                # Include stderr for debugging
                if proc.stderr:
                    error_preview = proc.stderr[:300].replace('\n', ' ')
                    details += f": {error_preview}"
                elif proc.stdout:
                    output_preview = proc.stdout[:300].replace('\n', ' ')
                    details += f": {output_preview}"

            result.add_check(f"command_success", success, details)
            result.passed = success

            # Store full output for potential further analysis
            result.checks[-1]["stdout"] = proc.stdout
            result.checks[-1]["stderr"] = proc.stderr

        except subprocess.TimeoutExpired:
            result.add_check("command_success", False, f"timed out after 60s: {cmd_str}")
            result.passed = False
        except FileNotFoundError:
            result.add_check("command_success", False, f"command not found: {command[0]}")
            result.passed = False
        except Exception as e:
            result.add_check("command_success", False, f"error running '{cmd_str}': {e}")
            result.passed = False

        result.summary = f"Command {'succeeded' if result.passed else 'failed'}: {cmd_str}"
        return result

    def assess_overlay_validation(self, overlay_path: Path, spec_path: Path | None = None) -> AssessmentResult:
        """Assess whether an overlay passes speakeasy validation.

        This runs `speakeasy overlay validate` to check the overlay is valid
        and can be applied to a spec.
        """
        result = AssessmentResult(passed=True)

        if not overlay_path.exists():
            result.add_check("overlay_exists", False, f"{overlay_path} not found")
            result.passed = False
            return result

        result.add_check("overlay_exists", True, f"{overlay_path.name} found")

        # Run speakeasy overlay validate
        cmd = ["speakeasy", "overlay", "validate", "-o", str(overlay_path)]
        if spec_path and spec_path.exists():
            cmd.extend(["-s", str(spec_path)])

        validation_result = self.assess_command_success(cmd, cwd=overlay_path.parent)

        # Merge results
        for check in validation_result.checks:
            check["name"] = f"speakeasy_validate_{check['name']}"
            result.checks.append(check)
            if not check["passed"]:
                result.passed = False

        result.summary = f"Overlay validation {'passed' if result.passed else 'failed'}"
        return result

    def assess_pagination_config(self, overlay_path: Path) -> AssessmentResult:
        """Assess whether x-speakeasy-pagination is correctly configured.

        Validates the semantic structure of pagination extensions,
        not just their presence.
        """
        result = AssessmentResult(passed=True)

        if not overlay_path.exists():
            result.add_check("overlay_exists", False, f"{overlay_path} not found")
            result.passed = False
            return result

        try:
            content = yaml.safe_load(overlay_path.read_text())
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        result.add_check("valid_yaml", True, "Valid YAML")

        # Find pagination extensions in actions
        pagination_configs = []
        actions = content.get("actions", [])

        for i, action in enumerate(actions):
            update = action.get("update", {})
            if "x-speakeasy-pagination" in str(update):
                # Extract the pagination config
                if isinstance(update, dict) and "x-speakeasy-pagination" in update:
                    pagination_configs.append((i, update["x-speakeasy-pagination"]))

        if not pagination_configs:
            result.add_check("has_pagination", False, "No x-speakeasy-pagination found in actions")
            result.passed = False
            return result

        result.add_check("has_pagination", True, f"Found {len(pagination_configs)} pagination config(s)")

        # Validate each pagination config
        for action_idx, config in pagination_configs:
            prefix = f"action_{action_idx}_pagination"

            # Check for required 'type' field
            has_type = "type" in config
            result.add_check(
                f"{prefix}_has_type",
                has_type,
                f"type: {config.get('type', 'missing')}"
            )
            if not has_type:
                result.passed = False
                continue

            pag_type = config.get("type")
            valid_types = ["cursor", "offsetLimit", "offset"]
            type_valid = pag_type in valid_types
            result.add_check(
                f"{prefix}_valid_type",
                type_valid,
                f"type '{pag_type}' {'is valid' if type_valid else f'not in {valid_types}'}"
            )
            if not type_valid:
                result.passed = False

            # Check for inputs
            has_inputs = "inputs" in config and isinstance(config["inputs"], list)
            result.add_check(
                f"{prefix}_has_inputs",
                has_inputs,
                f"inputs: {len(config.get('inputs', []))} defined" if has_inputs else "inputs missing or invalid"
            )
            if not has_inputs:
                result.passed = False

            # Check for outputs
            has_outputs = "outputs" in config and isinstance(config["outputs"], dict)
            result.add_check(
                f"{prefix}_has_outputs",
                has_outputs,
                f"outputs: {list(config.get('outputs', {}).keys())}" if has_outputs else "outputs missing or invalid"
            )
            if not has_outputs:
                result.passed = False

            # Type-specific validation
            if pag_type == "cursor" and has_outputs:
                outputs = config["outputs"]
                has_next_cursor = "nextCursor" in outputs
                result.add_check(
                    f"{prefix}_cursor_has_next",
                    has_next_cursor,
                    "nextCursor output " + ("present" if has_next_cursor else "missing for cursor pagination")
                )
                if not has_next_cursor:
                    result.passed = False

        result.summary = f"{result.passed_count}/{len(result.checks)} pagination checks passed"
        return result
