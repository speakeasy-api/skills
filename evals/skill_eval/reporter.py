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

        # Summary table
        table = Table(title=f"Evaluation Results: {results['suite']}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Tests", str(results["total"]))
        table.add_row("Passed", str(results["passed"]))
        table.add_row("Failed", str(results["failed"]))
        table.add_row("Pass Rate", f"{results['pass_rate']:.1%}")

        self.console.print(table)

        # Failed tests details
        failed = [d for d in results["details"] if not d["passed"]]
        if failed:
            self.console.print("\n[bold red]Failed Tests:[/bold red]")
            for f in failed:
                self.console.print(f"  • {f['skill']} ({f['suite']})")
                if "error" in f:
                    self.console.print(f"    [dim]Error: {f['error']}[/dim]")
                if "checks" in f:
                    for check in f["checks"]:
                        if not check.get("passed", True):
                            self.console.print(f"    [dim]- {check}[/dim]")

    def print_comparison(
        self,
        without_skills: dict[str, Any],
        with_skills: dict[str, Any],
    ) -> None:
        """Print comparison of results with and without skills."""
        self.console.print()

        table = Table(title="Comparison: Without Skills vs With Skills")
        table.add_column("Metric", style="cyan")
        table.add_column("Without Skills", style="yellow")
        table.add_column("With Skills", style="green")
        table.add_column("Delta", style="bold")

        metrics = [
            ("Pass Rate", "pass_rate", True),
            ("Passed", "passed", True),
            ("Failed", "failed", False),
        ]

        for label, key, higher_is_better in metrics:
            val_without = without_skills[key]
            val_with = with_skills[key]

            if isinstance(val_without, float):
                delta = val_with - val_without
                delta_str = f"{delta:+.1%}"
                val_without_str = f"{val_without:.1%}"
                val_with_str = f"{val_with:.1%}"
            else:
                delta = val_with - val_without
                delta_str = f"{delta:+d}"
                val_without_str = str(val_without)
                val_with_str = str(val_with)

            # Color delta based on improvement
            if (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better):
                delta_str = f"[green]{delta_str}[/green]"
            elif delta != 0:
                delta_str = f"[red]{delta_str}[/red]"

            table.add_row(label, val_without_str, val_with_str, delta_str)

        self.console.print(table)
