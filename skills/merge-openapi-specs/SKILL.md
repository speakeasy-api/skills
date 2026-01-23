---
name: merge-openapi-specs
description: Use when combining multiple OpenAPI specs into one. Triggers on "merge specs", "combine specs", "multiple OpenAPI files", "microservices specs", "speakeasy merge"
license: Apache-2.0
---

# merge-openapi-specs

Use `speakeasy merge` to combine multiple specs into one.

## When to Use

- Combining microservice specs into a unified API
- Merging versioned spec files
- Combining public and internal API specs
- User says: "merge specs", "combine specs", "multiple OpenAPI files"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| OpenAPI specs | Yes (2+) | Specs to merge (`-s` for each) |

## Outputs

| Output | Description |
|--------|-------------|
| Merged spec | Combined OpenAPI spec (`-o`) |

## Command

```bash
speakeasy merge -s <spec1> -s <spec2> -o <output-path>
```

## Example

```bash
# Merge two specs
speakeasy merge -s ./api/users.yaml -s ./api/orders.yaml -o combined.yaml

# Merge multiple specs (specify each with -s)
speakeasy merge -s ./specs/auth.yaml -s ./specs/users.yaml -s ./specs/orders.yaml -o combined.yaml
```

## Use Cases

- Microservices with separate specs per service
- API versioning with multiple spec files
- Combining public and internal API specs

## Conflict Resolution

When specs have conflicts:
- Later specs override earlier ones for duplicate paths
- Schema conflicts may require manual resolution
- Review merged output for correctness

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Schema conflicts | Duplicate schema names | Rename schemas before merging |
| Missing references | Cross-spec $ref | Ensure all referenced schemas are included |
| Duplicate paths | Same endpoint in multiple specs | Remove duplicates or use different base paths |

## Related Skills

- `validate-openapi-spec` - Validate merged output
- `start-new-sdk-project` - Generate SDK from merged spec
- `create-openapi-overlay` - Customize merged spec without editing
