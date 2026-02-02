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

    def assess_sdk_compilation(
        self, sdk_dir: Path, target: str, mode: str = "quick"
    ) -> AssessmentResult:
        """Assess whether the generated SDK compiles successfully.

        Args:
            sdk_dir: Path to the SDK directory
            target: Target language (typescript, python, go, etc.)
            mode: Validation mode
                - "quick": Fast syntax/type checks only (2-10s)
                - "full": Complete build with dependencies (30-120s)

        Quick mode uses:
            - TypeScript: tsc --noEmit (type check without emit)
            - Python: python -m py_compile + mypy (if available)
            - Go: go vet ./... (fast static analysis)
            - Java: gradle classes (compile only, no tests)
            - PHP: php -l (syntax check)
            - Ruby: ruby -c (syntax check)
        """
        result = AssessmentResult(passed=True)

        # Quick validation commands (fast, no dependency install)
        quick_commands: dict[str, list[tuple[str, list[str], int]]] = {
            "typescript": [
                # tsc --noEmit requires node_modules, so we need a minimal install first
                # Use --ignore-scripts to skip postinstall hooks for speed
                ("install_deps", ["npm", "install", "--ignore-scripts", "--prefer-offline"], 30),
                ("typecheck", ["npx", "tsc", "--noEmit"], 15),
            ],
            "python": [
                # Syntax check all Python files - very fast
                ("syntax_check", ["python", "-m", "compileall", "-q", "src"], 5),
            ],
            "go": [
                # go vet is fast and catches common issues
                ("vet", ["go", "vet", "./..."], 15),
            ],
            "java": [
                # gradle classes compiles without running tests
                ("compile", ["./gradlew", "classes", "-q", "--no-daemon"], 60),
            ],
            "csharp": [
                ("build", ["dotnet", "build", "--no-restore", "-v", "q"], 30),
            ],
            "php": [
                # PHP lint is extremely fast
                ("syntax", ["php", "-l", "src/"], 5),
            ],
            "ruby": [
                # Ruby syntax check
                ("syntax", ["ruby", "-c", "-W0", "lib/"], 5),
            ],
            "terraform": [
                ("vet", ["go", "vet", "./..."], 15),
            ],
        }

        # Full build commands (slow, includes dependency install)
        full_commands: dict[str, list[tuple[str, list[str], int]]] = {
            "typescript": [
                ("install_deps", ["npm", "install"], 60),
                ("compile", ["npm", "run", "build"], 30),
            ],
            "python": [
                ("install_check", ["pip", "install", "-e", ".", "--dry-run"], 15),
                ("typecheck", ["mypy", "src", "--ignore-missing-imports"], 30),
            ],
            "go": [
                ("compile", ["go", "build", "./..."], 30),
            ],
            "java": [
                ("compile", ["./gradlew", "build", "-x", "test", "--no-daemon"], 90),
            ],
            "csharp": [
                ("restore", ["dotnet", "restore"], 30),
                ("build", ["dotnet", "build"], 30),
            ],
            "php": [
                ("install", ["composer", "install", "--no-dev"], 30),
                ("analyze", ["./vendor/bin/phpstan", "analyse", "src"], 15),
            ],
            "ruby": [
                ("install", ["bundle", "install"], 30),
                ("typecheck", ["bundle", "exec", "srb", "tc"], 15),
            ],
            "terraform": [
                ("compile", ["go", "build", "./..."], 30),
            ],
        }

        commands_map = quick_commands if mode == "quick" else full_commands
        commands = commands_map.get(target, [])

        if not commands:
            result.add_check(
                "build_commands_available",
                False,
                f"No {mode} build commands defined for target: {target}"
            )
            result.passed = False
            return result

        result.add_check(
            "build_commands_available",
            True,
            f"{mode.capitalize()} validation for {target}"
        )

        for step_name, cmd, timeout in commands:
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=sdk_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                success = proc.returncode == 0
                details = f"exit code {proc.returncode}"
                if not success and proc.stderr:
                    error_preview = proc.stderr[:200].replace('\n', ' ')
                    details += f": {error_preview}..."

                result.add_check(f"build_{step_name}", success, details)
                if not success:
                    result.passed = False
                    break

            except subprocess.TimeoutExpired:
                result.add_check(f"build_{step_name}", False, f"timed out after {timeout}s")
                result.passed = False
                break
            except FileNotFoundError as e:
                # Command not found - skip this check gracefully in quick mode
                if mode == "quick":
                    result.add_check(f"build_{step_name}", True, f"skipped (command not found: {cmd[0]})")
                else:
                    result.add_check(f"build_{step_name}", False, f"command not found: {e}")
                    result.passed = False
                    break
            except Exception as e:
                result.add_check(f"build_{step_name}", False, f"error: {e}")
                result.passed = False
                break

        result.summary = f"{result.passed_count}/{len(result.checks)} {mode} checks passed"
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

    def assess_workflow_structure(self) -> AssessmentResult:
        """Assess whether .speakeasy/workflow.yaml has correct structure.

        This is essential for all SDK generation - the workflow file
        controls how speakeasy run operates.
        """
        result = AssessmentResult(passed=True)

        workflow_path = self.workspace_dir / ".speakeasy" / "workflow.yaml"
        if not workflow_path.exists():
            result.add_check("workflow_exists", False, ".speakeasy/workflow.yaml not found")
            result.passed = False
            return result

        result.add_check("workflow_exists", True, ".speakeasy/workflow.yaml found")

        try:
            content = yaml.safe_load(workflow_path.read_text())
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        result.add_check("valid_yaml", True, "Valid YAML")

        # Check required top-level keys
        required_keys = ["workflowVersion", "sources", "targets"]
        for key in required_keys:
            has_key = key in content
            result.add_check(
                f"has_{key}",
                has_key,
                f"'{key}' {'present' if has_key else 'missing'}"
            )
            if not has_key:
                result.passed = False

        # Check sources structure
        sources = content.get("sources", {})
        if sources:
            for source_name, source_config in sources.items():
                has_inputs = "inputs" in source_config
                result.add_check(
                    f"source_{source_name}_has_inputs",
                    has_inputs,
                    f"Source '{source_name}' has inputs" if has_inputs else f"Source '{source_name}' missing inputs"
                )
                if not has_inputs:
                    result.passed = False

        # Check targets structure
        targets = content.get("targets", {})
        if targets:
            for target_name, target_config in targets.items():
                has_target = "target" in target_config
                has_source = "source" in target_config
                result.add_check(
                    f"target_{target_name}_valid",
                    has_target and has_source,
                    f"Target '{target_name}' has target and source" if (has_target and has_source) else f"Target '{target_name}' missing target or source"
                )
                if not (has_target and has_source):
                    result.passed = False

        result.summary = f"{result.passed_count}/{len(result.checks)} workflow checks passed"
        return result

    def assess_gen_yaml(self, target: str) -> AssessmentResult:
        """Assess whether gen.yaml has correct language-specific configuration.

        Each language target requires specific configuration in gen.yaml.
        """
        result = AssessmentResult(passed=True)

        # gen.yaml can be at root or in .speakeasy/
        gen_paths = [
            self.workspace_dir / "gen.yaml",
            self.workspace_dir / ".speakeasy" / "gen.yaml",
        ]
        gen_path = None
        for p in gen_paths:
            if p.exists():
                gen_path = p
                break

        if not gen_path:
            result.add_check("gen_yaml_exists", False, "gen.yaml not found")
            result.passed = False
            return result

        result.add_check("gen_yaml_exists", True, f"gen.yaml found at {gen_path.relative_to(self.workspace_dir)}")

        try:
            content = yaml.safe_load(gen_path.read_text())
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        result.add_check("valid_yaml", True, "Valid YAML")

        # Check for language-specific section
        lang_key = target.lower()
        has_lang_section = lang_key in content
        result.add_check(
            f"has_{lang_key}_section",
            has_lang_section,
            f"'{lang_key}:' section {'present' if has_lang_section else 'missing'}"
        )
        if not has_lang_section:
            result.passed = False
            return result

        lang_config = content[lang_key]

        # Check for common required fields
        common_fields = {
            "typescript": ["packageName"],
            "python": ["packageName"],
            "go": ["packageName"],
            "java": ["groupID", "artifactID"],
            "csharp": ["packageName"],
            "ruby": ["packageName"],
            "php": ["packageName", "namespace"],
            "terraform": ["packageName"],
        }

        required = common_fields.get(lang_key, [])
        for field in required:
            has_field = field in lang_config
            result.add_check(
                f"has_{field}",
                has_field,
                f"'{field}' {'present' if has_field else 'missing'} in {lang_key} config"
            )
            if not has_field:
                result.passed = False

        result.summary = f"{result.passed_count}/{len(result.checks)} gen.yaml checks passed"
        return result

    def assess_hooks_preserved(self, target: str) -> AssessmentResult:
        """Assess whether SDK hooks are properly set up and would be preserved.

        Hook files should be created once and never overwritten on regeneration.
        """
        result = AssessmentResult(passed=True)

        # Language-specific hook locations
        hook_paths = {
            "typescript": [
                ("registration", "src/hooks/registration.ts"),
                ("types", "src/hooks/types.ts"),
            ],
            "python": [
                ("registration", "src/hooks/registration.py"),
            ],
            "go": [
                ("registration", "internal/hooks/registration.go"),
            ],
            "java": [
                ("registration", "src/main/java/hooks/HookRegistration.java"),
            ],
            "csharp": [
                ("registration", "Hooks/HookRegistration.cs"),
            ],
            "ruby": [
                ("registration", "sdk_hooks/registration.rb"),
            ],
            "php": [
                ("registration", "src/Hooks/HookRegistration.php"),
            ],
        }

        paths = hook_paths.get(target.lower(), [])
        if not paths:
            result.add_check(
                "hooks_defined",
                False,
                f"No hook paths defined for target: {target}"
            )
            # This isn't necessarily a failure - just no hooks to check
            result.summary = "No hooks to verify for this target"
            return result

        for hook_name, rel_path in paths:
            hook_path = self.workspace_dir / rel_path
            exists = hook_path.exists()
            result.add_check(
                f"hook_{hook_name}_exists",
                exists,
                f"{rel_path} {'found' if exists else 'not found'}"
            )
            # Missing hooks don't fail the test - they're created on first gen
            # But if they exist, they should have content

            if exists:
                content = hook_path.read_text()
                has_content = len(content.strip()) > 0
                result.add_check(
                    f"hook_{hook_name}_has_content",
                    has_content,
                    f"{rel_path} {'has content' if has_content else 'is empty'}"
                )

        result.summary = f"{result.passed_count}/{len(result.checks)} hook checks passed"
        return result

    def assess_retries_config(self, overlay_path: Path) -> AssessmentResult:
        """Assess whether x-speakeasy-retries is correctly configured.

        Validates retry configuration structure including backoff settings.
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

        # Find retry configurations in actions
        retry_configs = []
        actions = content.get("actions", [])

        for i, action in enumerate(actions):
            update = action.get("update", {})
            if "x-speakeasy-retries" in str(update):
                if isinstance(update, dict) and "x-speakeasy-retries" in update:
                    retry_configs.append((i, update["x-speakeasy-retries"]))

        if not retry_configs:
            result.add_check("has_retries", False, "No x-speakeasy-retries found in actions")
            result.passed = False
            return result

        result.add_check("has_retries", True, f"Found {len(retry_configs)} retry config(s)")

        # Validate each retry config
        for action_idx, config in retry_configs:
            prefix = f"action_{action_idx}_retries"

            # Check for strategy
            has_strategy = "strategy" in config
            result.add_check(
                f"{prefix}_has_strategy",
                has_strategy,
                f"strategy: {config.get('strategy', 'missing')}"
            )
            if not has_strategy:
                result.passed = False

            # Check for backoff config when strategy is backoff
            if config.get("strategy") == "backoff":
                has_backoff = "backoff" in config and isinstance(config["backoff"], dict)
                result.add_check(
                    f"{prefix}_has_backoff",
                    has_backoff,
                    "backoff config present" if has_backoff else "backoff config missing for backoff strategy"
                )
                if not has_backoff:
                    result.passed = False
                else:
                    backoff = config["backoff"]
                    # Check for common backoff fields
                    backoff_fields = ["initialInterval", "maxInterval", "exponent"]
                    for field in backoff_fields:
                        has_field = field in backoff
                        result.add_check(
                            f"{prefix}_backoff_{field}",
                            has_field,
                            f"{field}: {backoff.get(field, 'missing')}"
                        )

            # Check for statusCodes
            has_status_codes = "statusCodes" in config
            result.add_check(
                f"{prefix}_has_statusCodes",
                has_status_codes,
                f"statusCodes: {config.get('statusCodes', 'missing')}"
            )

        result.summary = f"{result.passed_count}/{len(result.checks)} retry checks passed"
        return result

    def assess_terraform_annotations(self, spec_path: Path) -> AssessmentResult:
        """Assess whether OpenAPI spec has correct Terraform entity annotations.

        Terraform providers require x-speakeasy-entity and x-speakeasy-entity-operation.
        """
        result = AssessmentResult(passed=True)

        if not spec_path.exists():
            result.add_check("spec_exists", False, f"{spec_path} not found")
            result.passed = False
            return result

        try:
            content = yaml.safe_load(spec_path.read_text())
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        result.add_check("valid_yaml", True, "Valid YAML")

        # Check for entity annotations in schemas
        schemas = content.get("components", {}).get("schemas", {})
        entities_found = []
        for schema_name, schema_def in schemas.items():
            if "x-speakeasy-entity" in schema_def:
                entities_found.append(schema_name)

        has_entities = len(entities_found) > 0
        result.add_check(
            "has_entity_annotations",
            has_entities,
            f"Found {len(entities_found)} schemas with x-speakeasy-entity: {entities_found}" if has_entities else "No x-speakeasy-entity annotations found"
        )
        if not has_entities:
            result.passed = False

        # Check for entity-operation annotations in paths
        paths = content.get("paths", {})
        operations_found = []
        crud_mapping = {"create": 0, "read": 0, "update": 0, "delete": 0}

        for path, path_item in paths.items():
            for method in ["get", "post", "put", "patch", "delete"]:
                if method in path_item:
                    operation = path_item[method]
                    if "x-speakeasy-entity-operation" in operation:
                        op_value = operation["x-speakeasy-entity-operation"]
                        operations_found.append(f"{method.upper()} {path}: {op_value}")
                        # Parse CRUD type
                        if "#" in str(op_value):
                            crud_type = str(op_value).split("#")[-1]
                            if crud_type in crud_mapping:
                                crud_mapping[crud_type] += 1

        has_operations = len(operations_found) > 0
        result.add_check(
            "has_entity_operation_annotations",
            has_operations,
            f"Found {len(operations_found)} operations with x-speakeasy-entity-operation" if has_operations else "No x-speakeasy-entity-operation annotations found"
        )
        if not has_operations:
            result.passed = False

        # Check CRUD coverage
        for crud_type, count in crud_mapping.items():
            has_crud = count > 0
            result.add_check(
                f"has_{crud_type}_operation",
                has_crud,
                f"{crud_type}: {count} operations" if has_crud else f"No {crud_type} operations found"
            )
            # Not all CRUD operations are required, so don't fail

        result.summary = f"{result.passed_count}/{len(result.checks)} Terraform annotation checks passed"
        return result

    def assess_mcp_config(self) -> AssessmentResult:
        """Assess whether MCP server generation is properly configured.

        Checks for enableMCPServer in gen.yaml and scopes overlay.
        """
        result = AssessmentResult(passed=True)

        # Check gen.yaml for enableMCPServer
        gen_paths = [
            self.workspace_dir / "gen.yaml",
            self.workspace_dir / ".speakeasy" / "gen.yaml",
        ]
        gen_path = None
        for p in gen_paths:
            if p.exists():
                gen_path = p
                break

        if not gen_path:
            result.add_check("gen_yaml_exists", False, "gen.yaml not found")
            result.passed = False
            return result

        try:
            content = yaml.safe_load(gen_path.read_text())
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        result.add_check("valid_yaml", True, "Valid YAML")

        # Check for MCP enabled in typescript config
        ts_config = content.get("typescript", {})
        mcp_enabled = ts_config.get("enableMCPServer", False)
        result.add_check(
            "mcp_enabled",
            mcp_enabled,
            "enableMCPServer: true" if mcp_enabled else "enableMCPServer not set or false"
        )
        if not mcp_enabled:
            result.passed = False

        # Check for MCP scopes overlay
        scopes_overlay = self.workspace_dir / "mcp-scopes-overlay.yaml"
        has_scopes = scopes_overlay.exists()
        result.add_check(
            "mcp_scopes_overlay_exists",
            has_scopes,
            "mcp-scopes-overlay.yaml found" if has_scopes else "mcp-scopes-overlay.yaml not found (optional)"
        )
        # Scopes overlay is optional, don't fail if missing

        # Check for MCP server directory
        mcp_dir = self.workspace_dir / "src" / "mcp-server"
        has_mcp_dir = mcp_dir.is_dir()
        result.add_check(
            "mcp_server_dir_exists",
            has_mcp_dir,
            "src/mcp-server/ directory found" if has_mcp_dir else "src/mcp-server/ directory not found"
        )

        result.summary = f"{result.passed_count}/{len(result.checks)} MCP config checks passed"
        return result

    def assess_test_generation(self) -> AssessmentResult:
        """Assess whether SDK test generation is properly configured.

        Checks for generateTests in gen.yaml and tests directory.
        """
        result = AssessmentResult(passed=True)

        # Check gen.yaml for generateTests
        gen_paths = [
            self.workspace_dir / "gen.yaml",
            self.workspace_dir / ".speakeasy" / "gen.yaml",
        ]
        gen_path = None
        for p in gen_paths:
            if p.exists():
                gen_path = p
                break

        if not gen_path:
            result.add_check("gen_yaml_exists", False, "gen.yaml not found")
            result.passed = False
            return result

        try:
            content = yaml.safe_load(gen_path.read_text())
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        result.add_check("valid_yaml", True, "Valid YAML")

        # Check for tests.generateTests
        tests_config = content.get("tests", {})
        generate_tests = tests_config.get("generateTests", False)
        result.add_check(
            "generate_tests_enabled",
            generate_tests,
            "tests.generateTests: true" if generate_tests else "tests.generateTests not enabled"
        )

        # Check for tests directory
        tests_dir = self.workspace_dir / "tests"
        has_tests_dir = tests_dir.is_dir()
        result.add_check(
            "tests_dir_exists",
            has_tests_dir,
            "tests/ directory found" if has_tests_dir else "tests/ directory not found"
        )

        # Check for custom Arazzo tests
        arazzo_path = self.workspace_dir / ".speakeasy" / "tests.arazzo.yaml"
        has_arazzo = arazzo_path.exists()
        result.add_check(
            "arazzo_tests_exist",
            has_arazzo,
            ".speakeasy/tests.arazzo.yaml found" if has_arazzo else ".speakeasy/tests.arazzo.yaml not found (optional)"
        )
        # Arazzo is optional

        result.summary = f"{result.passed_count}/{len(result.checks)} test generation checks passed"
        return result

    def assess_multi_target_workflow(self) -> AssessmentResult:
        """Assess whether workflow.yaml is configured for multi-target generation.

        Multi-target workflows have multiple sources and/or targets.
        """
        result = AssessmentResult(passed=True)

        workflow_path = self.workspace_dir / ".speakeasy" / "workflow.yaml"
        if not workflow_path.exists():
            result.add_check("workflow_exists", False, ".speakeasy/workflow.yaml not found")
            result.passed = False
            return result

        try:
            content = yaml.safe_load(workflow_path.read_text())
        except yaml.YAMLError as e:
            result.add_check("valid_yaml", False, f"Invalid YAML: {e}")
            result.passed = False
            return result

        result.add_check("valid_yaml", True, "Valid YAML")

        # Count sources
        sources = content.get("sources", {})
        source_count = len(sources)
        result.add_check(
            "sources_count",
            source_count >= 1,
            f"Found {source_count} source(s): {list(sources.keys())}"
        )

        # Count targets
        targets = content.get("targets", {})
        target_count = len(targets)
        is_multi_target = target_count > 1
        result.add_check(
            "is_multi_target",
            is_multi_target,
            f"Found {target_count} target(s): {list(targets.keys())}" + (" (multi-target)" if is_multi_target else " (single-target)")
        )

        # Check each target has unique output
        if is_multi_target:
            outputs = []
            for target_name, target_config in targets.items():
                output = target_config.get("output", "./")
                outputs.append(output)
                result.add_check(
                    f"target_{target_name}_output",
                    True,
                    f"Output: {output}"
                )

            # Check outputs are unique
            unique_outputs = len(set(outputs)) == len(outputs)
            result.add_check(
                "unique_outputs",
                unique_outputs,
                "All targets have unique output paths" if unique_outputs else f"Duplicate output paths found: {outputs}"
            )
            if not unique_outputs:
                result.passed = False

        result.summary = f"{result.passed_count}/{len(result.checks)} multi-target checks passed"
        return result

    def assess_naming_overlay(self, overlay_path: Path) -> AssessmentResult:
        """Assess whether a naming overlay has correct structure.

        Checks for x-speakeasy-name-override and x-speakeasy-group extensions.
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

        actions = content.get("actions", [])
        name_overrides = 0
        groups = 0

        for action in actions:
            update = action.get("update", {})
            if isinstance(update, dict):
                if "x-speakeasy-name-override" in update:
                    name_overrides += 1
                if "x-speakeasy-group" in update:
                    groups += 1

        has_naming = name_overrides > 0 or groups > 0
        result.add_check(
            "has_naming_extensions",
            has_naming,
            f"Found {name_overrides} name-override(s), {groups} group(s)" if has_naming else "No naming extensions found"
        )
        if not has_naming:
            result.passed = False

        if name_overrides > 0:
            result.add_check("has_name_overrides", True, f"{name_overrides} x-speakeasy-name-override(s)")

        if groups > 0:
            result.add_check("has_groups", True, f"{groups} x-speakeasy-group(s)")

        result.summary = f"{result.passed_count}/{len(result.checks)} naming overlay checks passed"
        return result
