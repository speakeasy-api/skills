---
name: create-openapi-overlay
description: Use when customizing SDK generation without editing the source spec. Triggers on "create overlay", "overlay file", "customize SDK", "can't modify spec", "x-speakeasy extensions", "SDK customization"
---

# create-openapi-overlay

Overlays let you customize an OpenAPI spec for SDK generation without modifying the source.

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

## When to Use Overlays

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

**Overlays cannot easily handle:**
- Deduplication of schemas (requires structural analysis)

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

## Related Skills

- `apply-openapi-overlay` - Apply overlay to spec
- `fix-validation-errors-with-overlays` - Fix lint errors via overlay
- `improve-operation-ids` - Improve SDK method naming
- `get-ai-suggestions` - Generate overlay suggestions automatically
