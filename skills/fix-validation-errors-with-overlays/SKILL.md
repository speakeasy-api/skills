---
name: fix-validation-errors-with-overlays
description: Use when you have lint errors but can't modify the source spec. Triggers on "fix with overlay", "can't edit spec", "add missing descriptions", "fix validation errors", "overlay fix"
---

# fix-validation-errors-with-overlays

Fix OpenAPI validation errors using overlays when you can't modify the source spec.

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

## NOT Overlay-Appropriate

| Issue | Why |
|-------|-----|
| Invalid JSON/YAML | Syntax error in source |
| Missing required fields | Schema incomplete |
| Broken $ref | Source needs fixing |
| Wrong data types | API design issue |

## Quick Fix Workflow

```bash
# 1. Generate suggestions
speakeasy suggest operation-ids -s openapi.yaml -o fixes.yaml

# 2. Add to workflow
# Edit .speakeasy/workflow.yaml to include overlay

# 3. Regenerate
speakeasy run
```

## Related Skills

- `validate-openapi-spec` - Identify errors to fix
- `create-openapi-overlay` - Create custom overlay fixes
- `get-ai-suggestions` - Auto-generate fix suggestions
- `diagnose-generation-failure` - Determine if overlay can fix issue
