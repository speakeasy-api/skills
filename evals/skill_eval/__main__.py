"""CLI entry point for skill evaluation."""

import asyncio
import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .runner import EvalRunner
from .reporter import Reporter
from .tracker import EvalTracker

console = Console()


@click.group()
def cli():
    """Skill evaluation harness for Speakeasy agent skills.

    This harness evaluates skills by running real SDK generation workflows
    using the Speakeasy CLI in isolated workspaces.
    """
    pass


@cli.command()
@click.option(
    "--suite",
    type=click.Choice(["all", "generation", "overlay", "diagnosis", "workflow"]),
    default="all",
    help="Test suite to run"
)
@click.option("--skill", help="Run tests for specific skill only")
@click.option("--test", "test_filter", help="Run tests matching this name pattern")
@click.option("--output", "-o", type=click.Path(), help="Output results to JSON file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--model", default="claude-sonnet-4-20250514", help="Model to use for agent")
@click.option("--max-concurrent", default=3, help="Max concurrent test runs")
@click.option("--track/--no-track", default=True, help="Track results in VCS history")
@click.option("--keep-workspaces", is_flag=True, help="Keep workspace directories for debugging")
def run(
    suite: str,
    skill: str | None,
    test_filter: str | None,
    output: str | None,
    verbose: bool,
    model: str,
    max_concurrent: int,
    track: bool,
    keep_workspaces: bool,
):
    """Run skill evaluations.

    Examples:

        skill-eval run --suite generation
        skill-eval run --skill start-new-sdk-project
        skill-eval run --test typescript -v
        skill-eval run --no-track  # Skip history tracking
        skill-eval run --keep-workspaces  # Keep workspaces for debugging
    """
    runner = EvalRunner(model=model, verbose=verbose)
    # TODO: Add keep_workspaces support to EvalRunner
    reporter = Reporter(console)
    tracker = EvalTracker() if track else None

    console.print(Panel.fit(
        f"[bold]Running {suite} evaluations[/bold]\n"
        f"Model: {model}\n"
        f"Concurrent: {max_concurrent}\n"
        f"Tracking: {'enabled' if track else 'disabled'}",
        title="Skill Eval"
    ))

    with console.status("[bold green]Running evaluations..."):
        results = asyncio.run(runner.run(
            suite=suite,
            skill_filter=skill,
            test_filter=test_filter,
            max_concurrent=max_concurrent,
        ))

    reporter.print_results(results)

    # Track results
    if tracker:
        results_file = tracker.save_results(results, model)
        tracker.update_history(results, model, results_file)
        console.print(f"\n[dim]Results tracked in {results_file.name}[/dim]")
        console.print(f"[dim]History updated in results/HISTORY.md[/dim]")

    if output:
        Path(output).write_text(json.dumps(results, indent=2, default=str))
        console.print(f"\n[dim]Results also written to {output}[/dim]")


@cli.command()
@click.argument("test_name")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--model", default="claude-sonnet-4-20250514", help="Model to use for agent")
@click.option("--output", "-o", type=click.Path(), help="Output results to JSON file")
def single(test_name: str, verbose: bool, model: str, output: str | None):
    """Run a single test by name.

    Examples:

        skill-eval single typescript-sdk-from-clean-spec
        skill-eval single fix-poor-naming-with-overlay -v
    """
    runner = EvalRunner(model=model, verbose=verbose)

    console.print(f"[bold]Running test: {test_name}[/bold]\n")

    with console.status("[bold green]Running evaluation..."):
        result = asyncio.run(runner.run_single(test_name))

    # Print result details
    if result.get("passed"):
        console.print("[bold green]PASSED[/bold green]")
    else:
        console.print("[bold red]FAILED[/bold red]")

    if result.get("error"):
        console.print(f"[red]Error: {result['error']}[/red]")

    # Show skills info
    if result.get("skills_installed"):
        console.print(f"\n[dim]Skills installed: {result['skills_installed']}[/dim]")
    if result.get("skills_invoked"):
        console.print(f"[cyan]Skills invoked: {', '.join(result['skills_invoked'])}[/cyan]")
    if "expected_skill_invoked" in result:
        if result["expected_skill_invoked"]:
            console.print(f"[green]✓ Expected skill was invoked[/green]")
        else:
            console.print(f"[yellow]! Expected skill was NOT invoked[/yellow]")

    if result.get("checks"):
        console.print("\n[bold]Checks:[/bold]")
        for check in result["checks"]:
            status = "[green]✓[/green]" if check.get("passed") else "[red]✗[/red]"
            console.print(f"  {status} {check.get('name', check.get('details', ''))}")

    if result.get("speakeasy_commands"):
        console.print(f"\n[bold]Speakeasy commands used:[/bold]")
        for cmd in result["speakeasy_commands"]:
            console.print(f"  $ {cmd[:80]}{'...' if len(cmd) > 80 else ''}")

    if result.get("tool_calls"):
        console.print(f"\n[dim]Tool calls: {len(result['tool_calls'])}[/dim]")
        if verbose:
            for tc in result["tool_calls"]:
                console.print(f"  - {tc['name']}")

    if result.get("changes"):
        changes = result["changes"]
        if changes.get("added"):
            console.print(f"\n[green]Files created: {len(changes['added'])}[/green]")
            if verbose:
                for f in changes["added"][:10]:
                    console.print(f"  + {f}")

    if result.get("cost_usd"):
        console.print(f"\n[dim]Cost: ${result['cost_usd']:.4f}[/dim]")

    if output:
        Path(output).write_text(json.dumps(result, indent=2, default=str))
        console.print(f"\n[dim]Results written to {output}[/dim]")


@cli.command("list")
@click.option("--suite", type=click.Choice(["all", "generation", "overlay", "diagnosis", "workflow"]), default="all")
def list_tests(suite: str):
    """List all available test cases."""
    runner = EvalRunner()

    if suite == "all":
        tests = runner.list_tests()
    else:
        tests = {suite: runner.load_tests(suite)}

    for suite_name, cases in tests.items():
        if not cases:
            continue

        console.print(f"\n[bold]{suite_name}[/bold] ({len(cases)} tests)")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Name")
        table.add_column("Skill")
        table.add_column("Type")
        table.add_column("Target")

        for case in cases:
            table.add_row(
                case.get("name", "unnamed"),
                case.get("skill", "-"),
                case.get("type", "-"),
                case.get("target", "-"),
            )

        console.print(table)


@cli.command()
def check():
    """Check if the evaluation environment is ready."""
    import shutil

    console.print("[bold]Environment Check[/bold]\n")

    # Check speakeasy CLI
    speakeasy = shutil.which("speakeasy")
    if speakeasy:
        console.print(f"[green]✓[/green] speakeasy CLI found: {speakeasy}")
        # Try to get version
        import subprocess
        try:
            result = subprocess.run([speakeasy, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                console.print(f"  Version: {result.stdout.strip()}")
        except Exception:
            pass
    else:
        console.print("[red]✗[/red] speakeasy CLI not found")
        console.print("  Install with: curl -fsSL https://raw.githubusercontent.com/speakeasy-api/speakeasy/main/install.sh | sh")

    # Check ANTHROPIC_API_KEY
    import os
    if os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[green]✓[/green] ANTHROPIC_API_KEY is set")
    else:
        console.print("[yellow]![/yellow] ANTHROPIC_API_KEY not set (required for running evaluations)")

    # Check fixture files
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    fixture_files = list(fixtures_dir.glob("*.yaml"))
    console.print(f"[green]✓[/green] {len(fixture_files)} fixture files found")

    # Check test files
    tests_dir = Path(__file__).parent.parent / "tests"
    test_files = list(tests_dir.glob("*.yaml"))
    console.print(f"[green]✓[/green] {len(test_files)} test files found")

    # Check skills directory
    skills_dir = Path(__file__).parent.parent.parent / "skills"
    if skills_dir.exists():
        skill_count = len([d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
        console.print(f"[green]✓[/green] {skill_count} skills available")
    else:
        console.print("[red]✗[/red] Skills directory not found")

    # Check results directory
    results_dir = Path(__file__).parent.parent / "results"
    if results_dir.exists():
        result_files = list(results_dir.glob("*.json"))
        console.print(f"[green]✓[/green] {len(result_files)} previous eval results")
    else:
        console.print("[dim]No previous eval results[/dim]")


@cli.command()
@click.option("-n", "--count", default=10, help="Number of recent results to analyze")
def trend(count: int):
    """Show evaluation trends from recent runs."""
    tracker = EvalTracker()
    summary = tracker.get_trend_summary(count)

    if "error" in summary:
        console.print(f"[yellow]{summary['error']}[/yellow]")
        return

    console.print(Panel.fit(
        f"[bold]Evaluation Trends[/bold]\n"
        f"Based on {summary['count']} recent runs",
        title="Trend Analysis"
    ))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric")
    table.add_column("Latest")
    table.add_column("Average")
    table.add_column("Trend (recent→old)")

    # Pass rate
    pr = summary["pass_rate"]
    trend_str = " → ".join(f"{r:.0%}" for r in pr["trend"][:5])
    table.add_row(
        "Pass Rate",
        f"{pr['latest']:.1%}",
        f"{pr['avg']:.1%}",
        trend_str
    )

    # Skill invocation rate
    si = summary["skill_invocation_rate"]
    trend_str = " → ".join(f"{r:.0%}" for r in si["trend"][:5])
    table.add_row(
        "Skill Invocation",
        f"{si['latest']:.1%}",
        f"{si['avg']:.1%}",
        trend_str
    )

    # Cost
    cost = summary["cost_usd"]
    trend_str = " → ".join(f"${c:.2f}" for c in cost["trend"][:5])
    table.add_row(
        "Cost per Run",
        f"${cost['latest']:.4f}",
        f"${cost['avg']:.4f}",
        trend_str
    )

    console.print(table)
    console.print("\n[dim]See results/HISTORY.md for full history[/dim]")


@cli.command()
@click.option("--suite", type=click.Choice(["all", "generation", "overlay", "diagnosis", "workflow"]), required=True)
@click.option("--model", default="claude-sonnet-4-20250514", help="Model to use")
def compare(suite: str, model: str):
    """Compare results with and without skills loaded.

    This helps measure the effectiveness of skills by comparing
    agent performance with skill context vs without.
    """
    runner = EvalRunner(model=model)
    reporter = Reporter(console)

    console.print(f"\n[bold]Comparing {suite} results with/without skills[/bold]\n")

    console.print("[bold]Running WITHOUT skills...[/bold]")
    with console.status("[yellow]Testing base model..."):
        results_without = asyncio.run(runner.run(suite=suite, with_skills=False))

    console.print("\n[bold]Running WITH skills...[/bold]")
    with console.status("[green]Testing with skills..."):
        results_with = asyncio.run(runner.run(suite=suite, with_skills=True))

    reporter.print_comparison(results_without, results_with)


if __name__ == "__main__":
    cli()

@cli.command()
@click.option("--all", is_flag=True, help="Remove all temporary workspaces")
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without deleting")
def clean(all: bool, dry_run: bool):
    """Clean up leftover workspace directories from failed tests.
    
    Examples:
    
        skill-eval clean  # Clean recent workspaces
        skill-eval clean --all  # Clean all workspaces
        skill-eval clean --dry-run  # Show what would be deleted
    """
    import shutil
    from pathlib import Path
    
    workspace_dirs = list(Path("/tmp").glob("skill-eval-*"))
    
    if not workspace_dirs:
        console.print("[green]No workspace directories found to clean[/green]")
        return
    
    console.print(f"[bold]Found {len(workspace_dirs)} workspace director{'y' if len(workspace_dirs) == 1 else 'ies'}:[/bold]\n")
    
    for workspace_dir in workspace_dirs:
        size = sum(f.stat().st_size for f in workspace_dir.rglob('*') if f.is_file())
        size_mb = size / (1024 * 1024)
        console.print(f"  {workspace_dir.name} ({size_mb:.1f} MB)")
    
    if dry_run:
        console.print("\n[yellow]Dry run - no files deleted[/yellow]")
        return
    
    if not all and len(workspace_dirs) > 5:
        # Keep the 5 most recent
        workspace_dirs_sorted = sorted(workspace_dirs, key=lambda d: d.stat().st_mtime, reverse=True)
        to_delete = workspace_dirs_sorted[5:]
        to_keep = workspace_dirs_sorted[:5]
        
        console.print(f"\n[dim]Keeping {len(to_keep)} most recent workspaces[/dim]")
        workspace_dirs = to_delete
    
    if workspace_dirs:
        console.print(f"\n[yellow]Deleting {len(workspace_dirs)} workspace director{'y' if len(workspace_dirs) == 1 else 'ies'}...[/yellow]")
        for workspace_dir in workspace_dirs:
            shutil.rmtree(workspace_dir)
            console.print(f"  [red]✗[/red] Deleted {workspace_dir.name}")
        console.print("\n[green]Cleanup complete![/green]")
