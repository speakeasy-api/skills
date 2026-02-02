"""Test runner for skill evaluations."""

import asyncio
from pathlib import Path
from typing import Any

import yaml

from .evaluator import SkillEvaluator


class EvalRunner:
    """Runs skill evaluation test suites."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", verbose: bool = False):
        self.model = model
        self.verbose = verbose
        self.tests_dir = Path(__file__).parent.parent / "tests"
        self.skills_dir = Path(__file__).parent.parent.parent / "skills"

    def load_tests(self, suite: str) -> list[dict[str, Any]]:
        """Load test cases from YAML files."""
        if suite == "all":
            suites = ["activation", "correctness", "completeness", "hallucination"]
        else:
            suites = [suite]

        tests = []
        for s in suites:
            path = self.tests_dir / f"{s}.yaml"
            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f)
                    for test in data.get("tests", []):
                        test["suite"] = s
                        tests.append(test)
        return tests

    def list_tests(self) -> dict[str, list[dict]]:
        """List all tests grouped by suite."""
        result = {}
        for suite in ["activation", "correctness", "completeness", "hallucination"]:
            result[suite] = self.load_tests(suite)
        return result

    def load_skill(self, skill_name: str) -> str | None:
        """Load skill content from SKILL.md file."""
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        if skill_path.exists():
            return skill_path.read_text()
        return None

    async def run(
        self,
        suite: str = "all",
        skill_filter: str | None = None,
        with_skills: bool = True,
    ) -> dict[str, Any]:
        """Run evaluation suite."""
        tests = self.load_tests(suite)

        if skill_filter:
            tests = [t for t in tests if t["skill"] == skill_filter]

        evaluator = SkillEvaluator(model=self.model)
        results = {
            "suite": suite,
            "total": len(tests),
            "passed": 0,
            "failed": 0,
            "details": [],
        }

        # Run tests concurrently with semaphore to limit parallelism
        sem = asyncio.Semaphore(5)

        async def run_test(test: dict) -> dict:
            async with sem:
                skill_content = self.load_skill(test["skill"]) if with_skills else None
                return await evaluator.evaluate(test, skill_content)

        test_results = await asyncio.gather(*[run_test(t) for t in tests])

        for result in test_results:
            results["details"].append(result)
            if result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1

        results["pass_rate"] = results["passed"] / results["total"] if results["total"] > 0 else 0
        return results
