---
name: improve-operation-ids
description: Use when SDK methods have ugly auto-generated names. Triggers on "ugly method names", "GetApiV1Users", "improve operation IDs", "sdk.users.list() style", "better SDK naming", "x-speakeasy-group"
---

# improve-operation-ids

Improve SDK method naming from auto-generated to intuitive grouped methods.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| OpenAPI spec | Yes | Spec to improve (`-s`) |
| Authentication | Yes | Via `speakeasy auth login` or `SPEAKEASY_API_KEY` env var |

## Outputs

| Output | Description |
|--------|-------------|
| Suggestions | Better operation names |
| Overlay file | Optional: saves as overlay (`-o`) |

## Prerequisites

For non-interactive environments (CI/CD, AI agents), set:
```bash
export SPEAKEASY_API_KEY="<your-api-key>"
```
See `configure-authentication` skill for details.

## Check Current State

```bash
speakeasy suggest operation-ids -s openapi.yaml
```

## SDK Method Naming

Speakeasy generates grouped SDK methods using `x-speakeasy-group`:

| HTTP Method | SDK Usage | Operation ID |
|-------------|-----------|--------------|
| GET (list) | `sdk.users.list()` | `users_list` |
| GET (single) | `sdk.users.get()` | `users_get` |
| POST | `sdk.users.create()` | `users_create` |
| PUT | `sdk.users.update()` | `users_update` |
| PATCH | `sdk.users.patch()` | `users_patch` |
| DELETE | `sdk.users.delete()` | `users_delete` |

Use `x-speakeasy-group: users` and `x-speakeasy-name-override: list` to achieve this grouping.

## Apply Suggestions

```bash
# Generate overlay
speakeasy suggest operation-ids -s openapi.yaml -o operation-ids.yaml

# Add to workflow and regenerate
speakeasy run
```

## Manual Override

```yaml
overlay: 1.0.0
info:
  title: Custom operation names
  version: 1.0.0
actions:
  - target: "$.paths['/api/v1/users'].get"
    update:
      x-speakeasy-group: users
      x-speakeasy-name-override: listAll
```

This produces: `sdk.users.listAll()`

## Related Skills

- `get-ai-suggestions` - Auto-generate naming suggestions
- `create-openapi-overlay` - Create custom naming overlays
- `regenerate-sdk` - Regenerate with improved names
