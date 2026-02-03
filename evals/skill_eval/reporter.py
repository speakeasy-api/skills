"""Results reporting for skill evaluations."""

from typing import Any

from rich.console import Console
from rich.table import Table


class Reporter:
    """Formats and displays evaluation results."""

    def __init__(self, console: Console):
        self.console = console

    def print_results(self, results: dict[str, Any]) -> None:
        """Print evaluation results."""
        self.console.print()

        table = Table(title=f"Evaluation Results: {results['suite']}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Total Tests", str(results["total"]))
        table.add_row("Passed", str(results["passed"]))
        table.add_row("Failed", str(results["failed"]))
        table.add_row("Pass Rate", f"{results['pass_rate']:.1%}")
        self.console.print(table)

        failed = [d for d in results["details"] if not d.get("passed")]
        if failed:
            self.console.print("\n[bold red]Failed Tests:[/bold red]")
            for f in failed:
                self.console.print(f"  • {f['skill']} ({f.get('name', f.get('skill', 'unknown'))})")
                if "error" in f:
                    self.console.print(f"    [dim]Error: {f['error']}[/dim]")
                for check in f.get("checks", []):
                    if not check.get("passed", True):
                        self.console.print(f"    [dim]- {check}[/dim]")

    def print_comparison(self, without: dict[str, Any], with_skills: dict[str, Any]) -> None:
        """Print comparison of results with and without skills."""
        self.console.print()

        table = Table(title="Comparison: Without Skills vs With Skills")
        table.add_column("Metric", style="cyan")
        table.add_column("Without", style="yellow")
        table.add_column("With", style="green")
        table.add_column("Delta", style="bold")

        for label, key, higher_better in [("Pass Rate", "pass_rate", True), ("Passed", "passed", True), ("Failed", "failed", False)]:
            v1, v2 = without[key], with_skills[key]
            if isinstance(v1, float):
                delta, s1, s2 = v2 - v1, f"{v1:.1%}", f"{v2:.1%}"
                delta_s = f"{delta:+.1%}"
            else:
                delta, s1, s2 = v2 - v1, str(v1), str(v2)
                delta_s = f"{delta:+d}"

            color = "green" if (delta > 0) == higher_better else "red" if delta != 0 else ""
            table.add_row(label, s1, s2, f"[{color}]{delta_s}[/{color}]" if color else delta_s)

        self.console.print(table)
