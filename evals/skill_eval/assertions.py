"""Assertion checkers for skill evaluation."""

import json
import re
from typing import Any

import yaml


def check_assertions(output: str, assertions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check a list of assertions against output."""
    results = []

    for assertion in assertions:
        atype = assertion.get("type", "")
        value = assertion.get("value", "")

        if atype == "contains":
            results.append({"type": atype, "value": value, "passed": value in output})

        elif atype == "not_contains":
            results.append({"type": atype, "value": value, "passed": value not in output})

        elif atype == "matches":
            results.append({"type": atype, "pattern": value, "passed": bool(re.search(value, output))})

        elif atype == "valid_yaml":
            try:
                yaml_blocks = re.findall(r"```ya?ml\n(.*?)```", output, re.DOTALL)
                for block in yaml_blocks:
                    yaml.safe_load(block)
                results.append({"type": atype, "passed": len(yaml_blocks) > 0})
            except yaml.YAMLError:
                results.append({"type": atype, "passed": False})

        elif atype == "valid_json":
            try:
                json_blocks = re.findall(r"```json\n(.*?)```", output, re.DOTALL)
                for block in json_blocks:
                    json.loads(block)
                results.append({"type": atype, "passed": len(json_blocks) > 0})
            except json.JSONDecodeError:
                results.append({"type": atype, "passed": False})

        elif atype == "no_invalid_extensions":
            valid = assertion.get("valid_list", [])
            found = re.findall(r"x-speakeasy-[\w-]+", output)
            invalid = [e for e in found if e not in valid]
            results.append({"type": atype, "passed": not invalid, "invalid": invalid})

        elif atype == "no_invalid_commands":
            valid = assertion.get("valid_list", [])
            found = re.findall(r"speakeasy\s+[\w-]+", output)
            invalid = [c for c in found if not any(v in c for v in valid)]
            results.append({"type": atype, "passed": not invalid, "invalid": invalid})

    return results
