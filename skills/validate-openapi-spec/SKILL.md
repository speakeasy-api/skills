---
name: validate-openapi-spec
description: Use when checking if an OpenAPI spec is valid or has errors. Triggers on "validate spec", "lint spec", "check OpenAPI", "spec errors", "is my spec valid", "run speakeasy lint"
license: Apache-2.0
---

# validate-openapi-spec

Use `speakeasy lint` to check for errors and warnings in your OpenAPI spec.

## When to Use

- Checking if a spec is valid before generation
- Identifying errors blocking SDK generation
- User says: "validate spec", "lint spec", "is my spec valid"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| OpenAPI spec | Yes | Path to spec file (`-s`) |

## Outputs

| Output | Description |
|--------|-------------|
| Errors | Issues that block SDK generation |
| Warnings | Issues that may cause problems |
| Hints | Best practice suggestions |

## Command

```bash
speakeasy lint openapi --non-interactive -s <path-to-spec>
```

## Output Categories

| Severity | Meaning | Action |
|----------|---------|--------|
| Error | Blocks SDK generation | Must fix |
| Warning | May cause issues | Should fix |
| Hint | Best practice suggestion | Consider fixing |

## Common Validation Issues

| Issue | Solution |
|-------|----------|
| Missing operationId | Add operationId or use `speakeasy suggest operation-ids` |
| Invalid $ref | Fix the reference path |
| Missing response schema | Add response schema definitions |
| Duplicate operationId | Make operation IDs unique |

## AI-Friendly Output

For commands with large outputs, pipe to `grep` or `tail` to reduce context:
```bash
speakeasy lint openapi --non-interactive -s ./openapi.yaml 2>&1 | grep -E "(error|warning)"
```

## What NOT to Do

- **Do NOT** fix errors one-by-one without understanding root cause
- **Do NOT** ignore warnings - they often indicate real problems
- **Do NOT** modify the source spec without asking if it's externally managed

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "file not found" | Invalid spec path | Check the file path exists |
| Many duplicate errors | Shared schema issues | Fix the root schema, not each reference |
| "$ref not found" | Broken reference | Check the reference path matches actual location |

## Related Skills

- `diagnose-generation-failure` - When lint errors cause generation to fail
- `fix-validation-errors-with-overlays` - Fix issues without modifying source spec
- `get-ai-suggestions` - Get AI-powered suggestions for improvements
