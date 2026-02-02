"""CLI entry point for skill evaluation."""

import asyncio
import json
from pathlib import Path

import click
from rich.console import Console

from .runner import EvalRunner
from .reporter import Reporter

console = Console()


@click.group()
def cli():
    """Skill evaluation harness for Speakeasy agent skills."""
    pass


@cli.command()
@click.option("--suite", type=click.Choice(["all", "activation", "correctness", "completeness", "hallucination"]), default="all")
@click.option("--skill", help="Run tests for specific skill only")
@click.option("--output", "-o", type=click.Path(), help="Output results to JSON file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--model", default="claude-sonnet-4-20250514", help="Model to use")
def run(suite: str, skill: str | None, output: str | None, verbose: bool, model: str):
    """Run skill evaluations."""
    runner = EvalRunner(model=model, verbose=verbose)
    reporter = Reporter(console)

    with console.status("[bold green]Running evaluations..."):
        results = asyncio.run(runner.run(suite=suite, skill_filter=skill))

    reporter.print_results(results)

    if output:
        Path(output).write_text(json.dumps(results, indent=2))
        console.print(f"\n[dim]Results written to {output}[/dim]")


@cli.command()
@click.option("--suite", type=click.Choice(["correctness", "completeness", "hallucination"]), required=True)
@click.option("--model", default="claude-sonnet-4-20250514", help="Model to use")
def compare(suite: str, model: str):
    """Compare results with and without skills loaded."""
    runner = EvalRunner(model=model)
    reporter = Reporter(console)

    console.print("\n[bold]Running WITHOUT skills...[/bold]")
    with console.status("[yellow]Testing base model..."):
        results_without = asyncio.run(runner.run(suite=suite, with_skills=False))

    console.print("\n[bold]Running WITH skills...[/bold]")
    with console.status("[green]Testing with skills..."):
        results_with = asyncio.run(runner.run(suite=suite, with_skills=True))

    reporter.print_comparison(results_without, results_with)


@cli.command("list")
def list_tests():
    """List all available test cases."""
    runner = EvalRunner()
    tests = runner.list_tests()

    for suite, cases in tests.items():
        console.print(f"\n[bold]{suite}[/bold] ({len(cases)} tests)")
        for case in cases[:5]:
            prompt = case.get('prompt', case.get('should_activate', ['...'])[0] if case.get('should_activate') else '...')
            console.print(f"  - {case['skill']}: {str(prompt)[:50]}...")
        if len(cases) > 5:
            console.print(f"  ... and {len(cases) - 5} more")


if __name__ == "__main__":
    cli()
