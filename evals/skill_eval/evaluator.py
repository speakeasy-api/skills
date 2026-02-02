"""Anthropic SDK integration for skill evaluation."""

import os
from typing import Any

import anthropic

from .assertions import check_assertions


class SkillEvaluator:
    """Evaluates skills using the Anthropic API."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.client = anthropic.AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

    async def evaluate(self, test: dict[str, Any], skill_content: str | None) -> dict[str, Any]:
        """Evaluate a single test case."""
        suite = test.get("suite", "unknown")

        if suite == "activation":
            return await self._eval_activation(test, skill_content)
        elif suite == "correctness":
            return await self._eval_correctness(test, skill_content)
        elif suite == "completeness":
            return await self._eval_completeness(test, skill_content)
        elif suite == "hallucination":
            return await self._eval_hallucination(test, skill_content)
        else:
            return {"passed": False, "error": f"Unknown suite: {suite}"}

    async def _eval_activation(self, test: dict, skill_content: str | None) -> dict:
        """Test if skill activates on correct trigger phrases."""
        skill_name = test["skill"]
        should_activate = test.get("should_activate", [])
        should_not_activate = test.get("should_not_activate", [])

        results = {"skill": skill_name, "suite": "activation", "checks": []}

        # For activation tests, we check if the skill description matches
        if skill_content:
            # Extract description from frontmatter
            import re
            desc_match = re.search(r"description:\s*['\"]?(.*?)['\"]?\n", skill_content, re.DOTALL)
            description = desc_match.group(1) if desc_match else ""

            for phrase in should_activate:
                # Check if phrase or keywords appear in description
                matches = any(
                    word.lower() in description.lower()
                    for word in phrase.split()
                    if len(word) > 3
                )
                results["checks"].append({
                    "phrase": phrase,
                    "expected": "activate",
                    "passed": matches,
                })

            for phrase in should_not_activate:
                # Should NOT match generic phrases
                matches = phrase.lower() in description.lower()
                results["checks"].append({
                    "phrase": phrase,
                    "expected": "not_activate",
                    "passed": not matches,
                })

        results["passed"] = all(c["passed"] for c in results["checks"])
        return results

    async def _eval_correctness(self, test: dict, skill_content: str | None) -> dict:
        """Test if output uses correct Speakeasy syntax."""
        prompt = test.get("prompt", "")
        assertions = test.get("assertions", [])

        # Build system message with skill
        system = "You are an expert at Speakeasy SDK generation."
        if skill_content:
            system += f"\n\nHere is your skill context:\n\n{skill_content}"

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            output = response.content[0].text

            # Check assertions
            check_results = check_assertions(output, assertions)

            return {
                "skill": test["skill"],
                "suite": "correctness",
                "prompt": prompt[:100],
                "checks": check_results,
                "passed": all(c["passed"] for c in check_results),
            }
        except Exception as e:
            return {
                "skill": test["skill"],
                "suite": "correctness",
                "passed": False,
                "error": str(e),
            }

    async def _eval_completeness(self, test: dict, skill_content: str | None) -> dict:
        """Test if all required steps are performed."""
        prompt = test.get("prompt", "")
        required_steps = test.get("required_steps", [])

        system = "You are an expert at Speakeasy SDK generation. List the steps you would take."
        if skill_content:
            system += f"\n\nSkill context:\n\n{skill_content}"

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            output = response.content[0].text.lower()

            # Check if each required step is mentioned
            checks = []
            for step in required_steps:
                # Check for key terms from the step
                key_terms = [w for w in step.lower().split() if len(w) > 3]
                found = sum(1 for term in key_terms if term in output) >= len(key_terms) // 2
                checks.append({"step": step, "passed": found})

            return {
                "skill": test["skill"],
                "suite": "completeness",
                "prompt": prompt[:100],
                "checks": checks,
                "passed": sum(c["passed"] for c in checks) >= len(checks) * 0.8,
            }
        except Exception as e:
            return {
                "skill": test["skill"],
                "suite": "completeness",
                "passed": False,
                "error": str(e),
            }

    async def _eval_hallucination(self, test: dict, skill_content: str | None) -> dict:
        """Test if output contains invented APIs."""
        prompts = test.get("prompts", [])
        valid_extensions = test.get("valid_extensions", [])
        valid_commands = test.get("valid_commands", [])

        system = "You are an expert at Speakeasy SDK generation."
        if skill_content:
            system += f"\n\nSkill context:\n\n{skill_content}"

        checks = []
        for prompt in prompts:
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                output = response.content[0].text

                # Look for x-speakeasy-* extensions in output
                import re
                found_extensions = re.findall(r"x-speakeasy-[\w-]+", output)
                invalid = [ext for ext in found_extensions if ext not in valid_extensions]

                # Look for speakeasy commands
                found_commands = re.findall(r"speakeasy\s+[\w-]+(?:\s+[\w-]+)?", output)
                invalid_cmds = [cmd for cmd in found_commands if not any(v in cmd for v in valid_commands)]

                passed = len(invalid) == 0 and len(invalid_cmds) == 0
                checks.append({
                    "prompt": prompt[:50],
                    "passed": passed,
                    "invalid_extensions": invalid,
                    "invalid_commands": invalid_cmds,
                })
            except Exception as e:
                checks.append({"prompt": prompt[:50], "passed": False, "error": str(e)})

        return {
            "skill": test["skill"],
            "suite": "hallucination",
            "checks": checks,
            "passed": all(c["passed"] for c in checks),
        }
