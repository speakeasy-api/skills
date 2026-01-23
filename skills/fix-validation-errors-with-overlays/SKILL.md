---
name: fix-validation-errors-with-overlays
description: Use when you have lint errors but can't modify the source spec. Triggers on "fix with overlay", "can't edit spec", "add missing descriptions", "fix validation errors", "overlay fix"
license: Apache-2.0
---

# fix-validation-errors-with-overlays

Fix OpenAPI validation errors using overlays when you can't modify the source spec.

## When to Use

- Lint errors exist but source spec can't be edited
- Adding missing descriptions, tags, or operation names
- User says: "fix with overlay", "can't edit spec", "add missing descriptions"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| OpenAPI spec | Yes | Spec with validation errors |
| Lint output | Helpful | Errors to fix |

## Outputs

| Output | Description |
|--------|-------------|
| Overlay file | Fixes for validation issues |

## Overlay-Appropriate Fixes

| Issue | Overlay Solution |
|-------|------------------|
| Poor operation names | `x-speakeasy-name-override` |
| Missing descriptions | Add `summary` or `description` |
| Missing tags | Add `tags` array |
| Need operation grouping | `x-speakeasy-group` |
| Need retry config | `x-speakeasy-retries` |

## What NOT to Do

| Issue | Why Overlays Won't Help |
|-------|-------------------------|
| Invalid JSON/YAML | Syntax error in source - must fix source |
| Missing required fields | Schema incomplete - must fix source |
| Broken $ref | Source needs fixing directly |
| Wrong data types | API design issue - requires spec changes |

- **Do NOT** try to fix structural errors with overlays
- **Do NOT** ignore errors that need source spec fixes

## Quick Fix Workflow

```bash
# 1. Generate suggestions
speakeasy suggest operation-ids -s openapi.yaml -o fixes.yaml

# 2. Add to workflow
# Edit .speakeasy/workflow.yaml to include overlay

# 3. Regenerate
speakeasy run --output console
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Overlay not applied | Not in workflow.yaml | Add overlay to sources.overlays in workflow |
| Target not found | Wrong JSONPath | Verify path matches spec exactly |
| Errors persist | Issue not overlay-appropriate | Check if issue needs source spec fix |

## Related Skills

- `validate-openapi-spec` - Identify errors to fix
- `create-openapi-overlay` - Create custom overlay fixes
- `get-ai-suggestions` - Auto-generate fix suggestions
- `diagnose-generation-failure` - Determine if overlay can fix issue
