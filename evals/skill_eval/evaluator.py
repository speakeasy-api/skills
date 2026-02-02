"""Claude Agent SDK integration for skill evaluation."""

import asyncio
import re
from typing import Any

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)

from .assertions import check_assertions


class SkillEvaluator:
    """Evaluates skills using the Claude Agent SDK."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model

    async def _query_agent(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """Query the Claude agent and return the response text."""
        options = ClaudeAgentOptions(
            model=self.model,
            system_prompt=system_prompt,
            max_turns=1,
            allowed_tools=[],  # No tools needed for eval queries
        )

        async with ClaudeSDKClient(options=options) as client:
            await client.query(user_prompt)

            response_text = ""
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text

            return response_text

    async def evaluate(self, test: dict[str, Any], skill_content: str | None) -> dict[str, Any]:
        """Evaluate a single test case."""
        suite = test.get("suite", "unknown")
        handlers = {
            "activation": self._eval_activation,
            "correctness": self._eval_correctness,
            "completeness": self._eval_completeness,
            "hallucination": self._eval_hallucination,
        }
        handler = handlers.get(suite)
        if handler:
            return await handler(test, skill_content)
        return {"passed": False, "error": f"Unknown suite: {suite}"}

    async def _eval_activation(self, test: dict, skill_content: str | None) -> dict:
        """Test if skill activates on correct trigger phrases."""
        skill_name = test["skill"]
        checks = []

        if skill_content:
            desc_match = re.search(r"description:\s*>?-?\s*\n?\s*(.*?)(?=\n[a-z]|\nlicense:)", skill_content, re.DOTALL | re.IGNORECASE)
            description = desc_match.group(1).lower() if desc_match else ""

            for phrase in test.get("should_activate", []):
                keywords = [w for w in phrase.lower().split() if len(w) > 3]
                matches = sum(1 for k in keywords if k in description) >= max(1, len(keywords) // 2)
                checks.append({"phrase": phrase, "expected": "activate", "passed": matches})

            for phrase in test.get("should_not_activate", []):
                matches = phrase.lower() in description
                checks.append({"phrase": phrase, "expected": "not_activate", "passed": not matches})

        return {"skill": skill_name, "suite": "activation", "checks": checks, "passed": all(c["passed"] for c in checks) if checks else False}

    async def _eval_correctness(self, test: dict, skill_content: str | None) -> dict:
        """Test if output uses correct Speakeasy syntax."""
        prompt = test.get("prompt", "")
        system = "You are an expert at Speakeasy SDK generation."
        if skill_content:
            system += f"\n\nSkill context:\n\n{skill_content}"

        try:
            output = await self._query_agent(system, prompt)
            checks = check_assertions(output, test.get("assertions", []))
            return {"skill": test["skill"], "suite": "correctness", "prompt": prompt[:100], "checks": checks, "passed": all(c["passed"] for c in checks)}
        except Exception as e:
            return {"skill": test["skill"], "suite": "correctness", "passed": False, "error": str(e)}

    async def _eval_completeness(self, test: dict, skill_content: str | None) -> dict:
        """Test if all required steps are performed."""
        prompt = test.get("prompt", "")
        required_steps = test.get("required_steps", [])
        system = "You are an expert at Speakeasy SDK generation. List the steps you would take."
        if skill_content:
            system += f"\n\nSkill context:\n\n{skill_content}"

        try:
            output = await self._query_agent(system, prompt)
            output_lower = output.lower()
            checks = []
            for step in required_steps:
                keywords = [w for w in step.lower().split() if len(w) > 3]
                found = sum(1 for k in keywords if k in output_lower) >= max(1, len(keywords) // 2)
                checks.append({"step": step, "passed": found})
            return {"skill": test["skill"], "suite": "completeness", "prompt": prompt[:100], "checks": checks, "passed": sum(c["passed"] for c in checks) >= len(checks) * 0.8}
        except Exception as e:
            return {"skill": test["skill"], "suite": "completeness", "passed": False, "error": str(e)}

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
                output = await self._query_agent(system, prompt, max_tokens=1000)
                found_ext = re.findall(r"x-speakeasy-[\w-]+", output)
                invalid_ext = [e for e in found_ext if e not in valid_extensions]
                found_cmd = re.findall(r"speakeasy\s+[\w-]+", output)
                invalid_cmd = [c for c in found_cmd if not any(v in c for v in valid_commands)]
                checks.append({"prompt": prompt[:50], "passed": not invalid_ext and not invalid_cmd, "invalid_extensions": invalid_ext, "invalid_commands": invalid_cmd})
            except Exception as e:
                checks.append({"prompt": prompt[:50], "passed": False, "error": str(e)})

        return {"skill": test["skill"], "suite": "hallucination", "checks": checks, "passed": all(c["passed"] for c in checks)}
