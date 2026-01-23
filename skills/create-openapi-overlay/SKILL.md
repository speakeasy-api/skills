---
name: create-openapi-overlay
description: Use when customizing SDK generation without editing the source spec. Triggers on "create overlay", "overlay file", "customize SDK", "can't modify spec", "x-speakeasy extensions", "SDK customization"
license: Apache-2.0
---

# create-openapi-overlay

Overlays let you customize an OpenAPI spec for SDK generation without modifying the source.

## When to Use

- You need to customize SDK output but can't modify the source spec
- Adding x-speakeasy extensions for grouping, naming, or retries
- Fixing lint issues without editing the original file
- User says: "create overlay", "customize SDK", "can't modify spec"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Target spec | Yes | Spec to customize |
| Customizations | Yes | Changes to apply (groups, names, etc.) |

## Outputs

| Output | Description |
|--------|-------------|
| Overlay file | YAML file with JSONPath-targeted changes |

## Create Overlay Manually

Create an overlay file with this template structure:

```yaml
overlay: 1.0.0
info:
  title: My Overlay
  version: 1.0.0
actions:
  - target: "$.paths['/example'].get"
    update:
      x-speakeasy-group: example
```

Or generate an overlay by comparing two specs:

```bash
speakeasy overlay compare -b <before-spec> -a <after-spec> -o <output-overlay>
```

## Overlay Capabilities

**Overlays are great for:**
- Renaming operations (x-speakeasy-name-override)
- Adding descriptions/summaries
- Grouping operations (x-speakeasy-group)
- Adding retry configuration
- Marking endpoints as deprecated
- Adding SDK-specific extensions
- Fixing spec issues without modifying the source
- Adding new endpoints or schemas
- Making portable patches that work across spec versions

## Example Overlay

```yaml
overlay: 1.0.0
info:
  title: SDK Customizations
  version: 1.0.0
actions:
  - target: "$.paths['/users'].get"
    update:
      x-speakeasy-group: users
      x-speakeasy-name-override: list
  - target: "$.paths['/users'].post"
    update:
      x-speakeasy-group: users
      x-speakeasy-name-override: create
  - target: "$.paths['/users/{id}'].get"
    update:
      x-speakeasy-group: users
      x-speakeasy-name-override: get
  - target: "$.paths['/users/{id}'].delete"
    update:
      x-speakeasy-group: users
      x-speakeasy-name-override: delete
      deprecated: true
```

This produces: `sdk.users.list()`, `sdk.users.create()`, `sdk.users.get()`, `sdk.users.delete()`

## JSONPath Targeting

| Target | Selects |
|--------|---------|
| `$.paths['/users'].get` | GET /users operation |
| `$.paths['/users/{id}'].*` | All operations on /users/{id} |
| `$.components.schemas.User` | User schema |
| `$.info` | API info object |

## What NOT to Do

- **Do NOT** use overlays for invalid YAML/JSON syntax errors
- **Do NOT** try to deduplicate schemas with overlays (requires structural analysis)
- **Do NOT** fix broken $ref paths with overlays - fix the source spec instead

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "target not found" | JSONPath doesn't match spec structure | Verify exact path with spec inspection |
| Changes not applied | Overlay not in workflow | Add overlay to `workflow.yaml` sources |
| YAML parse error | Invalid overlay syntax | Check YAML indentation and structure |

## Related Skills

- `apply-openapi-overlay` - Apply overlay to spec
- `fix-validation-errors-with-overlays` - Fix lint errors via overlay
- `improve-operation-ids` - Improve SDK method naming
- `get-ai-suggestions` - Generate overlay suggestions automatically
