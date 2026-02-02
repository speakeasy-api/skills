"""Assertion checkers for skill evaluation."""

import re
from typing import Any


def check_assertions(output: str, assertions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check a list of assertions against output."""
    results = []

    for assertion in assertions:
        atype = assertion.get("type", "")
        target = assertion.get("target", "output")
        value = assertion.get("value", "")

        if target == "output":
            text = output
        else:
            text = output  # Could extend to parse specific sections

        if atype == "contains":
            passed = value in text
            results.append({
                "type": atype,
                "value": value,
                "passed": passed,
            })

        elif atype == "not_contains":
            passed = value not in text
            results.append({
                "type": atype,
                "value": value,
                "passed": passed,
            })

        elif atype == "matches":
            passed = bool(re.search(value, text))
            results.append({
                "type": atype,
                "pattern": value,
                "passed": passed,
            })

        elif atype == "valid_yaml":
            import yaml
            try:
                # Extract YAML blocks from markdown
                yaml_blocks = re.findall(r"```ya?ml\n(.*?)```", text, re.DOTALL)
                for block in yaml_blocks:
                    yaml.safe_load(block)
                passed = len(yaml_blocks) > 0
            except yaml.YAMLError:
                passed = False
            results.append({
                "type": atype,
                "passed": passed,
            })

        elif atype == "valid_json":
            import json
            try:
                # Extract JSON blocks from markdown
                json_blocks = re.findall(r"```json\n(.*?)```", text, re.DOTALL)
                for block in json_blocks:
                    json.loads(block)
                passed = len(json_blocks) > 0
            except json.JSONDecodeError:
                passed = False
            results.append({
                "type": atype,
                "passed": passed,
            })

        elif atype == "no_invalid_extensions":
            valid_list = assertion.get("valid_list", [])
            found = re.findall(r"x-speakeasy-[\w-]+", text)
            invalid = [ext for ext in found if ext not in valid_list]
            results.append({
                "type": atype,
                "passed": len(invalid) == 0,
                "invalid": invalid,
            })

        elif atype == "no_invalid_commands":
            valid_list = assertion.get("valid_list", [])
            found = re.findall(r"speakeasy\s+[\w-]+", text)
            invalid = [cmd for cmd in found if not any(v in cmd for v in valid_list)]
            results.append({
                "type": atype,
                "passed": len(invalid) == 0,
                "invalid": invalid,
            })

    return results
