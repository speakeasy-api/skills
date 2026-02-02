"""Workspace management for isolated skill evaluation environments."""

import shutil
import tempfile
from pathlib import Path
from typing import Any
import hashlib
import json


class Workspace:
    """Isolated workspace for evaluating skills against the Speakeasy CLI."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path(tempfile.mkdtemp(prefix="skill-eval-"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._initial_state: dict[str, str] | None = None

    @property
    def spec_path(self) -> Path:
        return self.base_dir / "openapi.yaml"

    @property
    def workflow_path(self) -> Path:
        return self.base_dir / ".speakeasy" / "workflow.yaml"

    @property
    def gen_yaml_path(self) -> Path:
        return self.base_dir / "gen.yaml"

    @property
    def overlay_dir(self) -> Path:
        return self.base_dir / "overlays"

    @property
    def sdk_output_dir(self) -> Path:
        return self.base_dir / "sdk"

    def setup(self, spec_content: str, gen_yaml: str | None = None, overlays: dict[str, str] | None = None) -> None:
        """Initialize workspace with OpenAPI spec and optional configuration."""
        # Write OpenAPI spec
        self.spec_path.write_text(spec_content)

        # Write gen.yaml if provided
        if gen_yaml:
            self.gen_yaml_path.write_text(gen_yaml)

        # Write overlays if provided
        if overlays:
            self.overlay_dir.mkdir(parents=True, exist_ok=True)
            for name, content in overlays.items():
                (self.overlay_dir / name).write_text(content)

        # Capture initial state
        self._initial_state = self._snapshot_state()

    def _snapshot_state(self) -> dict[str, str]:
        """Capture current state of all files in workspace."""
        state = {}
        for path in self.base_dir.rglob("*"):
            if path.is_file():
                rel_path = str(path.relative_to(self.base_dir))
                content = path.read_bytes()
                state[rel_path] = hashlib.sha256(content).hexdigest()
        return state

    def get_changes(self) -> dict[str, Any]:
        """Compare current state to initial state."""
        if self._initial_state is None:
            return {"error": "No initial state captured"}

        current_state = self._snapshot_state()

        added = set(current_state.keys()) - set(self._initial_state.keys())
        removed = set(self._initial_state.keys()) - set(current_state.keys())
        modified = {
            k for k in set(current_state.keys()) & set(self._initial_state.keys())
            if current_state[k] != self._initial_state[k]
        }

        return {
            "added": sorted(added),
            "removed": sorted(removed),
            "modified": sorted(modified),
            "unchanged": sorted(set(current_state.keys()) - added - modified),
        }

    def file_exists(self, rel_path: str) -> bool:
        """Check if a file exists in the workspace."""
        return (self.base_dir / rel_path).exists()

    def read_file(self, rel_path: str) -> str | None:
        """Read a file from the workspace."""
        path = self.base_dir / rel_path
        return path.read_text() if path.exists() else None

    def write_file(self, rel_path: str, content: str) -> None:
        """Write a file to the workspace."""
        path = self.base_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def list_files(self, pattern: str = "**/*") -> list[str]:
        """List files matching a glob pattern."""
        return sorted(
            str(p.relative_to(self.base_dir))
            for p in self.base_dir.glob(pattern)
            if p.is_file()
        )

    def cleanup(self) -> None:
        """Remove the workspace directory."""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def __enter__(self) -> "Workspace":
        return self

    def __exit__(self, *args) -> None:
        self.cleanup()


class WorkspaceManager:
    """Manages multiple workspaces for parallel evaluation."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path(tempfile.mkdtemp(prefix="skill-eval-workspaces-"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._workspaces: dict[str, Workspace] = {}

    def create(self, name: str) -> Workspace:
        """Create a new named workspace."""
        workspace_dir = self.base_dir / name
        workspace = Workspace(workspace_dir)
        self._workspaces[name] = workspace
        return workspace

    def get(self, name: str) -> Workspace | None:
        """Get an existing workspace by name."""
        return self._workspaces.get(name)

    def cleanup_all(self) -> None:
        """Clean up all workspaces."""
        for workspace in self._workspaces.values():
            workspace.cleanup()
        self._workspaces.clear()
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def __enter__(self) -> "WorkspaceManager":
        return self

    def __exit__(self, *args) -> None:
        self.cleanup_all()
