"""Fixture loading for skill evaluations.

Handles loading fixtures from:
- Local files (spec_file)
- Git repositories (source_ref with source.yaml)
"""

import json
import os
import shutil
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

import yaml


class FixtureLoader:
    """Loads test fixtures from various sources."""

    def __init__(self, fixtures_dir: Path, cache_dir: Path | None = None):
        self.fixtures_dir = fixtures_dir
        # Cache cloned repos to avoid re-cloning on every test run
        self.cache_dir = cache_dir or Path.home() / ".cache" / "skill-eval" / "repos"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load(self, test: dict[str, Any]) -> dict[str, Any]:
        """Load fixture data for a test.

        Handles:
        - spec_file: Direct path to an OpenAPI spec
        - source: Inline git repo reference (repository, commit, spec_path)

        Returns updated test dict with 'spec' and 'fixture_files' populated.
        """
        if "source" in test:
            return self._load_git_fixture_inline(test)
        elif "spec_file" in test:
            return self._load_file_fixture(test)
        return test

    def _load_file_fixture(self, test: dict[str, Any]) -> dict[str, Any]:
        """Load fixture from local file."""
        spec_path = self.fixtures_dir.parent / test["spec_file"]
        if spec_path.exists():
            test["spec"] = spec_path.read_text()
            # Also load additional fixture files from the same directory
            fixture_dir = spec_path.parent
            test["fixture_files"] = {}
            for fixture_file in fixture_dir.iterdir():
                if fixture_file.is_file() and fixture_file.name != spec_path.name:
                    rel_path = str(fixture_file.relative_to(self.fixtures_dir.parent))
                    test["fixture_files"][rel_path] = fixture_file.read_text()
        else:
            test["spec"] = None
            test["error"] = f"Spec file not found: {test['spec_file']}"
        return test

    def _load_git_fixture_inline(self, test: dict[str, Any]) -> dict[str, Any]:
        """Load fixture from inline git source config."""
        source_config = test["source"]

        repo_url = source_config.get("repository")
        commit = source_config.get("commit")
        spec_path = source_config.get("spec_path", "openapi.yaml")

        if not repo_url or not commit:
            test["spec"] = None
            test["error"] = "source missing repository or commit"
            return test

        # Clone or update the repo
        try:
            repo_dir = self._ensure_repo_cloned(repo_url, commit)
        except Exception as e:
            test["spec"] = None
            test["error"] = f"Failed to clone repo: {e}"
            return test

        # Load the spec
        full_spec_path = repo_dir / spec_path
        if not full_spec_path.exists():
            test["spec"] = None
            test["error"] = f"Spec not found in repo: {spec_path}"
            return test

        test["spec"] = full_spec_path.read_text()

        # Load local fixture files if fixture_dir specified
        test["fixture_files"] = {}
        fixture_dir_rel = test.get("fixture_dir")
        if fixture_dir_rel:
            fixture_dir = self.fixtures_dir.parent / fixture_dir_rel
            if fixture_dir.exists():
                for fixture_file in fixture_dir.iterdir():
                    if fixture_file.is_file():
                        rel_path = str(fixture_file.relative_to(self.fixtures_dir.parent))
                        test["fixture_files"][rel_path] = fixture_file.read_text()

        # Fetch GitHub issue if specified
        issue_config = source_config.get("issue")
        if issue_config:
            issue_content = self._fetch_github_issue(
                issue_config.get("repo"),
                issue_config.get("number")
            )
            if issue_content:
                # Add issue as a fixture file the agent can read
                issue_dir = fixture_dir_rel or "fixtures"
                issue_path = f"{issue_dir}/issue.md"
                test["fixture_files"][issue_path] = issue_content

        return test

    def _ensure_repo_cloned(self, repo_url: str, commit: str) -> Path:
        """Clone repo to cache or update existing clone to specified commit.

        Uses shallow clone with specific commit for efficiency.
        """
        # Create a unique directory name from repo URL
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        repo_owner = repo_url.rstrip("/").split("/")[-2]
        repo_dir = self.cache_dir / f"{repo_owner}-{repo_name}-{commit[:8]}"

        if repo_dir.exists():
            # Verify the commit is correct
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip().startswith(commit[:8]):
                    return repo_dir
            except Exception:
                pass
            # Wrong commit or corrupted, remove and re-clone
            shutil.rmtree(repo_dir)

        # Shallow clone with specific commit
        # First clone with depth 1
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )

        # Fetch the specific commit
        subprocess.run(
            ["git", "fetch", "--depth", "1", "origin", commit],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

        # Checkout the commit
        subprocess.run(
            ["git", "checkout", commit],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )

        return repo_dir

    def _fetch_github_issue(self, repo: str, issue_number: int) -> str | None:
        """Fetch a GitHub issue and format as markdown.

        Uses gh CLI if available, falls back to API.
        """
        if not repo or not issue_number:
            return None

        # Try gh CLI first (handles auth automatically)
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}/issues/{issue_number}"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                issue_data = json.loads(result.stdout)
                return self._format_issue_markdown(issue_data)
        except Exception:
            pass

        # Fallback to unauthenticated API (may hit rate limits)
        try:
            url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/vnd.github+json"},
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                issue_data = json.loads(response.read().decode("utf-8"))
                return self._format_issue_markdown(issue_data)
        except Exception:
            return None

    def _format_issue_markdown(self, issue_data: dict) -> str:
        """Format GitHub issue data as markdown."""
        title = issue_data.get("title", "Unknown")
        body = issue_data.get("body", "")
        author = issue_data.get("user", {}).get("login", "unknown")
        created = issue_data.get("created_at", "")[:10]
        url = issue_data.get("html_url", "")
        state = issue_data.get("state", "open")

        return f"""# GitHub Issue: {title}

**Repository:** {issue_data.get('repository_url', '').replace('https://api.github.com/repos/', '')}
**Author:** {author}
**Created:** {created}
**State:** {state}
**URL:** {url}

---

{body}
"""

    def clear_cache(self) -> None:
        """Clear the repo cache."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
