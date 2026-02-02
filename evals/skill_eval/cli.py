"""Speakeasy CLI execution for skill evaluation."""

import asyncio
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CLIResult:
    """Result from a CLI command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    success: bool = field(init=False)

    def __post_init__(self):
        self.success = self.exit_code == 0

    @property
    def output(self) -> str:
        """Combined stdout and stderr."""
        parts = []
        if self.stdout.strip():
            parts.append(self.stdout.strip())
        if self.stderr.strip():
            parts.append(self.stderr.strip())
        return "\n".join(parts)


class SpeakeasyCLI:
    """Interface to the Speakeasy CLI for evaluation."""

    def __init__(self, working_dir: Path, timeout: int = 120):
        self.working_dir = working_dir
        self.timeout = timeout
        self._speakeasy_path = self._find_speakeasy()

    def _find_speakeasy(self) -> str:
        """Find the speakeasy CLI executable."""
        # Check if speakeasy is in PATH
        speakeasy = shutil.which("speakeasy")
        if speakeasy:
            return speakeasy

        # Check common installation locations
        common_paths = [
            Path.home() / ".speakeasy" / "bin" / "speakeasy",
            Path("/usr/local/bin/speakeasy"),
            Path("/opt/homebrew/bin/speakeasy"),
        ]
        for path in common_paths:
            if path.exists():
                return str(path)

        raise RuntimeError(
            "speakeasy CLI not found. Install it with: "
            "curl -fsSL https://raw.githubusercontent.com/speakeasy-api/speakeasy/main/install.sh | sh"
        )

    async def run(self, *args: str, env: dict[str, str] | None = None) -> CLIResult:
        """Run a speakeasy CLI command."""
        cmd = [self._speakeasy_path, *args]
        cmd_str = " ".join(cmd)

        # Merge environment
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
                env=full_env,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout
            )
            return CLIResult(
                command=cmd_str,
                exit_code=proc.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
            )
        except asyncio.TimeoutError:
            return CLIResult(
                command=cmd_str,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {self.timeout}s",
            )
        except Exception as e:
            return CLIResult(
                command=cmd_str,
                exit_code=-1,
                stdout="",
                stderr=str(e),
            )

    async def quickstart(
        self,
        spec: str,
        target: str,
        sdk_name: str,
        package_name: str,
        output_dir: str | None = None,
    ) -> CLIResult:
        """Initialize a new SDK project."""
        args = [
            "quickstart",
            "--skip-interactive",
            "--output", "console",
            "-s", spec,
            "-t", target,
            "-n", sdk_name,
            "-p", package_name,
        ]
        if output_dir:
            args.extend(["-o", output_dir])
        return await self.run(*args)

    async def generate(self) -> CLIResult:
        """Regenerate SDK from existing workflow configuration."""
        return await self.run("run", "-y", "--output", "console")

    async def lint(self, spec: str) -> CLIResult:
        """Lint an OpenAPI spec."""
        return await self.run("lint", "openapi", "--non-interactive", "-s", spec)

    async def suggest_operation_ids(self, spec: str, output: str) -> CLIResult:
        """Generate AI-suggested operation IDs as an overlay."""
        return await self.run("suggest", "operation-ids", "-s", spec, "-o", output)

    async def overlay_apply(self, spec: str, overlay: str, output: str) -> CLIResult:
        """Apply an overlay to a spec."""
        return await self.run("overlay", "apply", "-s", spec, "-o", overlay, "--out", output)

    async def overlay_validate(self, overlay: str) -> CLIResult:
        """Validate an overlay file."""
        return await self.run("overlay", "validate", "-o", overlay)

    async def test(self, target: str | None = None) -> CLIResult:
        """Run contract tests."""
        args = ["test"]
        if target:
            args.extend(["--target", target])
        return await self.run(*args)

    async def version(self) -> CLIResult:
        """Get CLI version."""
        return await self.run("--version")

    async def is_available(self) -> bool:
        """Check if the CLI is available and working."""
        try:
            result = await self.version()
            return result.success
        except Exception:
            return False
