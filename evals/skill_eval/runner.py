"""Test runner for workspace-based skill evaluations."""

import asyncio
from pathlib import Path
from typing import Any

import yaml

from .evaluator import ExecutionObserver, SkillEvaluator
from .fixtures import FixtureLoader


class EvalRunner:
    """Runs skill evaluation test suites."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", verbose: bool = False):
        self.model = model
        self.verbose = verbose
        self.tests_dir = Path(__file__).parent.parent / "tests"
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"
        self.skills_dir = Path(__file__).parent.parent.parent / "skills"
        self.fixture_loader = FixtureLoader(self.fixtures_dir)

    def load_tests(self, suite: str) -> list[dict[str, Any]]:
        """Load test cases from YAML files."""
        suites = ["generation", "overlay", "diagnosis", "workflow"] if suite == "all" else [suite]
        tests = []

        for s in suites:
            path = self.tests_dir / f"{s}.yaml"
            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f)
                    for test in data.get("tests", []):
                        test["suite"] = s
                        # Use fixture loader for all fixture types
                        test = self.fixture_loader.load(test)
                        tests.append(test)
        return tests

    def list_tests(self) -> dict[str, list[dict]]:
        """List all tests grouped by suite."""
        return {s: self.load_tests(s) for s in ["generation", "overlay", "diagnosis", "workflow"]}

    def load_skill(self, skill_name: str) -> str | None:
        """Load skill content from SKILL.md file."""
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        return skill_path.read_text() if skill_path.exists() else None

    def clear_fixture_cache(self) -> None:
        """Clear the fixture loader's repo cache."""
        self.fixture_loader.clear_cache()
        if self.verbose:
            print("Fixture cache cleared")

    async def run(
        self,
        suite: str = "all",
        skill_filter: str | None = None,
        test_filter: str | None = None,
        with_skills: bool = True,
        skill_names: list[str] | None = None,
        max_concurrent: int = 3,
        observer: ExecutionObserver | None = None,
    ) -> dict[str, Any]:
        """Run evaluation suite.

        Args:
            suite: Test suite to run ("all", "generation", "overlay", "diagnosis", "workflow")
            skill_filter: Only run tests for this skill
            test_filter: Only run tests matching this name pattern
            with_skills: If True, install skills in workspace
            skill_names: Optional list of specific skill names to install. If None and with_skills=True, installs all.
            max_concurrent: Maximum concurrent test runs
            observer: Optional observer for real-time event streaming (forces max_concurrent=1)
        """
        tests = self.load_tests(suite)

        if skill_filter:
            tests = [t for t in tests if t.get("skill") == skill_filter]

        if test_filter:
            tests = [t for t in tests if test_filter in t.get("name", "")]

        # Skip tests with missing specs
        valid_tests = [t for t in tests if "error" not in t]
        skipped_tests = [t for t in tests if "error" in t]

        evaluator = SkillEvaluator(model=self.model)
        results = {
            "suite": suite,
            "total": len(tests),
            "passed": 0,
            "failed": 0,
            "skipped": len(skipped_tests),
            "details": [],
            "skill_names": skill_names,
        }

        # Add skipped tests to results
        for test in skipped_tests:
            results["details"].append({
                "name": test.get("name", "unknown"),
                "skill": test.get("skill", "unknown"),
                "type": test.get("type", "unknown"),
                "passed": False,
                "skipped": True,
                "error": test.get("error"),
            })

        # Run valid tests with concurrency limit
        # Force sequential execution when observer is provided to avoid interleaved output
        effective_max_concurrent = 1 if observer else max_concurrent
        sem = asyncio.Semaphore(effective_max_concurrent)

        async def run_test(test: dict) -> dict:
            async with sem:
                if self.verbose:
                    print(f"Running: {test.get('name', 'unnamed')}...")
                result = await evaluator.evaluate(test, with_skills=with_skills, skill_names=skill_names, observer=observer)
                result["name"] = test.get("name", "unnamed")
                return result

        if valid_tests:
            test_results = await asyncio.gather(*[run_test(t) for t in valid_tests])

            for result in test_results:
                results["details"].append(result)
                if result.get("passed"):
                    results["passed"] += 1
                else:
                    results["failed"] += 1

        results["pass_rate"] = results["passed"] / results["total"] if results["total"] > 0 else 0
        return results

    async def run_single(
        self,
        test_name: str,
        with_skills: bool = True,
        skill_names: list[str] | None = None,
        observer: ExecutionObserver | None = None,
    ) -> dict[str, Any]:
        """Run a single test by name.

        Args:
            test_name: Name of the test to run
            with_skills: If True, install skills in workspace
            skill_names: Optional list of specific skill names to install
            observer: Optional observer for real-time event streaming
        """
        all_tests = []
        for suite in ["generation", "overlay", "diagnosis", "workflow"]:
            all_tests.extend(self.load_tests(suite))

        test = next((t for t in all_tests if t.get("name") == test_name), None)
        if not test:
            return {"passed": False, "error": f"Test not found: {test_name}"}

        if "error" in test:
            return {"passed": False, "error": test["error"]}

        evaluator = SkillEvaluator(model=self.model)
        result = await evaluator.evaluate(test, with_skills=with_skills, skill_names=skill_names, observer=observer)
        result["name"] = test_name
        return result

    async def compare_with_without_skills(
        self,
        suite: str,
        skill_filter: str | None = None,
        skill_names: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare results with and without skill context.

        Args:
            suite: Test suite to run
            skill_filter: Only run tests for this skill
            skill_names: Optional list of specific skill names to install for the "with" run.
                         If None, installs all skills.
        """
        without_results = await self.run(suite=suite, skill_filter=skill_filter, with_skills=False)
        with_results = await self.run(suite=suite, skill_filter=skill_filter, with_skills=True, skill_names=skill_names)

        return {
            "without_skills": without_results,
            "with_skills": with_results,
        }
