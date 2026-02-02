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
def run(
    suite: str,
    skill: str | None,
    test_filter: str | None,
    output: str | None,
    verbose: bool,
    model: str,
    max_concurrent: int,
):
    """Run skill evaluations.

    Examples:

        skill-eval run --suite generation
        skill-eval run --skill start-new-sdk-project
        skill-eval run --test typescript -v
    """
    runner = EvalRunner(model=model, verbose=verbose)
    reporter = Reporter(console)

    console.print(Panel.fit(
        f"[bold]Running {suite} evaluations[/bold]\n"
        f"Model: {model}\n"
        f"Concurrent: {max_concurrent}",
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

    if output:
        Path(output).write_text(json.dumps(results, indent=2, default=str))
        console.print(f"\n[dim]Results written to {output}[/dim]")


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

    if result.get("checks"):
        console.print("\n[bold]Checks:[/bold]")
        for check in result["checks"]:
            status = "[green]✓[/green]" if check.get("passed") else "[red]✗[/red]"
            console.print(f"  {status} {check.get('name', check.get('details', ''))}")

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


@cli.command()
@click.option("--suite", type=click.Choice(["generation", "overlay", "diagnosis", "workflow"]), required=True)
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
        # Would need to modify evaluator to support this properly
        results_without = asyncio.run(runner.run(suite=suite, with_skills=False))

    console.print("\n[bold]Running WITH skills...[/bold]")
    with console.status("[green]Testing with skills..."):
        results_with = asyncio.run(runner.run(suite=suite, with_skills=True))

    reporter.print_comparison(results_without, results_with)


if __name__ == "__main__":
    cli()
