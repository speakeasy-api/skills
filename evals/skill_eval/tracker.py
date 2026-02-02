"""Evaluation results tracking for VCS."""

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EvalTracker:
    """Tracks evaluation results over time for trend analysis."""

    def __init__(self, results_dir: Path | None = None):
        self.results_dir = results_dir or Path(__file__).parent.parent / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.results_dir / "HISTORY.md"

    def get_git_info(self) -> dict[str, str]:
        """Get current git commit info."""
        try:
            commit = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()

            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()

            # Check for uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()
            dirty = bool(status)

            return {
                "commit": commit,
                "branch": branch,
                "dirty": dirty,
            }
        except Exception:
            return {"commit": "unknown", "branch": "unknown", "dirty": False}

    def save_results(self, results: dict[str, Any], model: str) -> Path:
        """Save evaluation results to a timestamped JSON file."""
        timestamp = datetime.now(timezone.utc)
        git_info = self.get_git_info()

        # Create filename with timestamp
        filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename

        # Enrich results with metadata
        full_results = {
            "metadata": {
                "timestamp": timestamp.isoformat(),
                "model": model,
                "git_commit": git_info["commit"],
                "git_branch": git_info["branch"],
                "git_dirty": git_info["dirty"],
            },
            "results": results,
        }

        filepath.write_text(json.dumps(full_results, indent=2, default=str))
        return filepath

    def update_history(self, results: dict[str, Any], model: str, results_file: Path) -> None:
        """Append a summary entry to HISTORY.md."""
        timestamp = datetime.now(timezone.utc)
        git_info = self.get_git_info()

        # Calculate summary stats
        total = results.get("total", 0)
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        skipped = results.get("skipped", 0)
        pass_rate = results.get("pass_rate", 0)
        total_cost = sum(
            d.get("cost_usd", 0) or 0
            for d in results.get("details", [])
        )

        # Count skill invocations
        details = results.get("details", [])
        skill_invoked_count = sum(
            1 for d in details
            if d.get("expected_skill_invoked", False)
        )

        # Calculate turn usage stats
        turns_data = [d.get("turns_used", 0) for d in details if d.get("turns_used")]
        avg_turns = sum(turns_data) / len(turns_data) if turns_data else 0
        total_turns = sum(turns_data)

        # Create markdown entry
        dirty_marker = " (dirty)" if git_info["dirty"] else ""
        entry = f"""
## {timestamp.strftime('%Y-%m-%d %H:%M')} UTC

| Metric | Value |
|--------|-------|
| Commit | `{git_info['commit']}`{dirty_marker} |
| Branch | `{git_info['branch']}` |
| Model | `{model}` |
| **Pass Rate** | **{pass_rate:.1%}** |
| Passed | {passed} |
| Failed | {failed} |
| Skipped | {skipped} |
| Total | {total} |
| Skills Invoked | {skill_invoked_count}/{len(details)} |
| Avg Turns | {avg_turns:.1f} |
| Total Turns | {total_turns} |
| Cost | ${total_cost:.4f} |
| Results File | `{results_file.name}` |

"""
        # Append failed tests if any
        failed_tests = [d for d in details if not d.get("passed", True)]
        if failed_tests:
            entry += "**Failed Tests:**\n"
            for ft in failed_tests[:5]:  # Limit to 5
                name = ft.get("name", ft.get("skill", "unknown"))
                error = ft.get("error", "")
                if error:
                    entry += f"- `{name}`: {error[:100]}\n"
                else:
                    entry += f"- `{name}`\n"
            if len(failed_tests) > 5:
                entry += f"- ... and {len(failed_tests) - 5} more\n"
            entry += "\n"

        entry += "---\n"

        # Read existing history and prepend new entry
        if self.history_file.exists():
            content = self.history_file.read_text()
            # Find the marker line and insert after it
            marker = "<!-- New entries will be prepended below this line -->"
            if marker in content:
                parts = content.split(marker, 1)
                new_content = parts[0] + marker + "\n" + entry + parts[1].lstrip("\n")
            else:
                # Fallback: append at end
                new_content = content + entry
        else:
            new_content = "# Evaluation History\n\n" + entry

        self.history_file.write_text(new_content)

    def get_recent_results(self, n: int = 10) -> list[dict[str, Any]]:
        """Load the N most recent timestamped result files.

        Only loads files matching the YYYYMMDD_HHMMSS.json pattern to avoid
        picking up ad-hoc result files.
        """
        # Only match timestamped files (YYYYMMDD_HHMMSS.json)
        timestamp_pattern = re.compile(r"^\d{8}_\d{6}\.json$")
        result_files = sorted(
            [f for f in self.results_dir.glob("*.json") if timestamp_pattern.match(f.name)],
            key=lambda p: p.name,
            reverse=True
        )[:n]

        results = []
        for f in result_files:
            try:
                data = json.loads(f.read_text())
                results.append(data)
            except Exception:
                pass

        return results

    def get_trend_summary(self, n: int = 10) -> dict[str, Any]:
        """Get trend summary from recent results."""
        recent = self.get_recent_results(n)
        if not recent:
            return {"error": "No results found"}

        pass_rates = []
        costs = []
        skill_invocation_rates = []
        avg_turns_list = []

        for r in recent:
            # Handle both wrapped (metadata/results) and unwrapped formats
            results = r.get("results", r)
            pass_rates.append(results.get("pass_rate", 0))

            details = results.get("details", [])
            total_cost = sum(d.get("cost_usd", 0) or 0 for d in details)
            costs.append(total_cost)

            if details:
                invoked = sum(1 for d in details if d.get("expected_skill_invoked", False))
                skill_invocation_rates.append(invoked / len(details))

                # Track turn usage
                turns_data = [d.get("turns_used", 0) for d in details if d.get("turns_used")]
                if turns_data:
                    avg_turns_list.append(sum(turns_data) / len(turns_data))
            else:
                skill_invocation_rates.append(0)

        return {
            "count": len(recent),
            "pass_rate": {
                "latest": pass_rates[0] if pass_rates else 0,
                "avg": sum(pass_rates) / len(pass_rates) if pass_rates else 0,
                "trend": pass_rates,
            },
            "cost_usd": {
                "latest": costs[0] if costs else 0,
                "avg": sum(costs) / len(costs) if costs else 0,
                "trend": costs,
            },
            "skill_invocation_rate": {
                "latest": skill_invocation_rates[0] if skill_invocation_rates else 0,
                "avg": sum(skill_invocation_rates) / len(skill_invocation_rates) if skill_invocation_rates else 0,
                "trend": skill_invocation_rates,
            },
            "avg_turns": {
                "latest": avg_turns_list[0] if avg_turns_list else 0,
                "avg": sum(avg_turns_list) / len(avg_turns_list) if avg_turns_list else 0,
                "trend": avg_turns_list,
            },
        }
