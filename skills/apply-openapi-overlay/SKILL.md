---
name: apply-openapi-overlay
description: Use when applying an overlay file to a spec. Triggers on "apply overlay", "overlay apply", "merge overlay", "speakeasy overlay apply"
---

# apply-openapi-overlay

Apply an overlay file to transform an OpenAPI spec.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| OpenAPI spec | Yes | Source spec (`-s`) |
| Overlay file | Yes | Overlay to apply (`-o`) |

## Outputs

| Output | Description |
|--------|-------------|
| Modified spec | Transformed OpenAPI spec (`--out`) |

## Command

```bash
speakeasy overlay apply -s <spec-path> -o <overlay-path> --out <output-path>
```

## Example

```bash
# Apply overlay and output merged spec
speakeasy overlay apply -s openapi.yaml -o my-overlay.yaml --out openapi-modified.yaml
```

## Using in Workflow (Recommended)

Better approach - add overlay to workflow.yaml:

```yaml
sources:
  my-api:
    inputs:
      - location: ./openapi.yaml
    overlays:
      - location: ./naming-overlay.yaml
      - location: ./grouping-overlay.yaml
```

Overlays are applied in order, so later overlays can override earlier ones.

## Related Skills

- `create-openapi-overlay` - Create overlay files
- `regenerate-sdk` - Run workflow with overlays applied
- `fix-validation-errors-with-overlays` - Use overlays to fix lint issues
