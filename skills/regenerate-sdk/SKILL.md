---
name: regenerate-sdk
description: Use when spec changed and SDK needs regenerating. Triggers on "regenerate SDK", "run speakeasy", "speakeasy run", "rebuild SDK", "update SDK", "spec changed"
license: Apache-2.0
---

# regenerate-sdk

Use `speakeasy run` to execute the workflow and regenerate SDKs.

## When to Use

- OpenAPI spec has been updated
- Workflow or overlay configuration changed
- Regenerating with latest Speakeasy version
- User says: "regenerate SDK", "run speakeasy", "spec changed"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| workflow.yaml | Yes | Must exist at `.speakeasy/workflow.yaml` |
| OpenAPI spec | Yes | As configured in workflow |
| Authentication | Yes | Via `speakeasy auth login` or `SPEAKEASY_API_KEY` env var |

## Outputs

| Output | Description |
|--------|-------------|
| Generated SDK | Updated SDK code in output directory |
| Generation logs | Success/failure details |

## Prerequisites

For non-interactive environments (CI/CD, AI agents), set:
```bash
export SPEAKEASY_API_KEY="<your-api-key>"
```
See `configure-authentication` skill for details.

## Command

```bash
# Run all configured targets
speakeasy run

# Run specific target only
speakeasy run -t <target-name>

# Run with specific source
speakeasy run -s <source-name>

# AI-friendly output mode
speakeasy run --output console
```

## When to Use

- After updating the OpenAPI spec
- After modifying workflow.yaml
- After changing overlays
- To regenerate with latest Speakeasy version

## Example Workflow

```yaml
# .speakeasy/workflow.yaml
workflowVersion: 1.0.0
speakeasyVersion: latest
sources:
  my-api:
    inputs:
      - location: ./openapi.yaml
targets:
  typescript-sdk:
    target: typescript
    source: my-api
    output: ./sdk/typescript
```

## AI-Friendly Output

For commands with large outputs, pipe to `grep` or `tail` to reduce context:
```bash
speakeasy run --output console 2>&1 | tail -50
```

## What NOT to Do

- **Do NOT** run without checking spec validity first if there were recent changes
- **Do NOT** ignore generation warnings - they may indicate SDK quality issues
- **Do NOT** delete `.speakeasy/` directory without understanding its purpose

## Troubleshooting

If `speakeasy run` fails, check:
1. Is the OpenAPI spec valid? Run `speakeasy lint openapi --non-interactive -s <spec>`
2. Does the source path exist? Check `inputs.location` in workflow.yaml
3. Are there blocking validation errors? See `diagnose-generation-failure` skill

## Related Skills

- `start-new-sdk-project` - Initial setup if no workflow.yaml exists
- `validate-openapi-spec` - Check spec before regenerating
- `diagnose-generation-failure` - When generation fails
- `check-workspace-status` - See configured targets and sources
