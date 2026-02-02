---
name: configure-speakeasy-extensions
description: >-
  Use when adding x-speakeasy extensions to an OpenAPI spec for SDK customization.
  Covers retries, pagination, naming, grouping, open enums, global headers, and
  custom security schemes. Triggers on "x-speakeasy", "add retries", "SDK pagination",
  "open enums", "global headers", "custom security", "SDK naming", "SDK grouping",
  "anti-fragile enums", "speakeasy extension".
license: Apache-2.0
---

# configure-speakeasy-extensions

Configure Speakeasy-specific OpenAPI extensions (`x-speakeasy-*`) to customize SDK generation. These extensions control retry behavior, pagination, method naming, operation grouping, enum handling, and custom authentication.

## When to Use

- Adding retry configuration to SDK operations
- Configuring cursor or offset pagination
- Customizing SDK method names and groupings
- Making enums "open" to handle unknown values gracefully
- Adding global headers as SDK constructor options
- Implementing custom security schemes (HMAC, signatures)
- User says: "x-speakeasy", "add retries", "SDK pagination", "open enums", "global headers", "custom security"

## Extension Reference

| Extension | Applies To | Purpose |
|-----------|-----------|---------|
| `x-speakeasy-retries` | Operation or root | Configure retry behavior |
| `x-speakeasy-pagination` | Operation | Enable automatic pagination |
| `x-speakeasy-name-override` | Operation | Override SDK method name |
| `x-speakeasy-group` | Operation | Group methods under namespace |
| `x-speakeasy-unknown-values` | Schema with enum | Allow unknown enum values |
| `x-speakeasy-globals` | Root | Define SDK-wide parameters |
| `x-speakeasy-custom-security-scheme` | Security scheme | Multi-part custom auth |

## Retries Configuration

Add retry behavior for transient failures:

### Per-Operation Retries

```yaml
paths:
  /resources:
    get:
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 500      # ms
          maxInterval: 60000        # ms
          maxElapsedTime: 3600000   # ms
          exponent: 1.5
        statusCodes: ["5XX", "429"]
        retryConnectionErrors: true
```

### Global Retries (via overlay)

```yaml
overlay: 1.0.0
info:
  title: Add global retries
  version: 1.0.0
actions:
  - target: $
    update:
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 500
          maxInterval: 60000
          maxElapsedTime: 3600000
          exponent: 1.5
        statusCodes: ["5XX", "429"]
        retryConnectionErrors: true
```

## Pagination Configuration

### Offset/Limit Pagination

```yaml
paths:
  /users:
    get:
      x-speakeasy-pagination:
        type: offsetLimit
        inputs:
          - name: offset
            in: parameters
            type: offset
          - name: limit
            in: parameters
            type: limit
        outputs:
          results: $.data
          numPages: $.meta.total_pages
```

### Cursor Pagination

```yaml
paths:
  /events:
    get:
      x-speakeasy-pagination:
        type: cursor
        inputs:
          - name: cursor
            in: parameters
            type: cursor
        outputs:
          results: $.events
          nextCursor: $.next_cursor
```

## Method Naming and Grouping

### Override Method Names

```yaml
paths:
  /users/{userId}/permissions:
    get:
      x-speakeasy-name-override: getUserPermissions
    put:
      x-speakeasy-name-override: setUserPermissions
```

### Group Operations

```yaml
paths:
  /users:
    get:
      x-speakeasy-group: users
      x-speakeasy-name-override: list
    post:
      x-speakeasy-group: users
      x-speakeasy-name-override: create
```

**Result:** `sdk.users.list()`, `sdk.users.create()`

## Open Enums (Anti-Fragility)

Prevent SDK breakage when APIs return new enum values:

### Single Enum

```yaml
components:
  schemas:
    Status:
      type: string
      enum: [pending, active, completed]
      x-speakeasy-unknown-values: allow
```

### All Enums (via overlay)

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: Open all enums
  version: 1.0.0
actions:
  - target: $..[?length(@.enum) > 1]
    update:
      x-speakeasy-unknown-values: allow
```

**Use for:** AI/LLM APIs (models change weekly), payment APIs (new methods), cloud APIs (new regions).

## Global Headers

Add SDK-wide headers that become constructor options:

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: Add global headers
  version: 1.0.0
actions:
  - target: $
    update:
      x-speakeasy-globals:
        parameters:
          - $ref: "#/components/parameters/TenantId"
          - $ref: "#/components/parameters/AppId"
  - target: $.components
    update:
      parameters:
        TenantId:
          name: X-Tenant-Id
          in: header
          schema:
            type: string
        AppId:
          name: X-App-Id
          in: header
          schema:
            type: string
```

**Result:**

```python
client = SDK(
    api_key="...",
    tenant_id="tenant-123",  # X-Tenant-Id header
    app_id="my-app"          # X-App-Id header
)
```

## Custom Security Schemes

For APIs requiring complex authentication (HMAC, multi-part credentials):

```yaml
overlay: 1.0.0
info:
  title: Custom HMAC Security
  version: 1.0.0
actions:
  - target: $.components
    update:
      securitySchemes:
        hmacAuth:
          type: http
          scheme: custom
          x-speakeasy-custom-security-scheme:
            schema:
              type: object
              properties:
                keyId:
                  type: string
                  description: API Key ID
                keySecret:
                  type: string
                  description: Secret for HMAC signing
                merchantId:
                  type: string
                  description: Merchant identifier
  - target: $
    update:
      security:
        - hmacAuth: []
```

With `envVarPrefix: MYAPI` in gen.yaml, this generates env var support for `MYAPI_KEY_ID`, `MYAPI_KEY_SECRET`, `MYAPI_MERCHANT_ID`.

## Applying Extensions

### Via Overlay (recommended)

```yaml
# .speakeasy/workflow.yaml
sources:
  my-api:
    inputs:
      - location: ./openapi.yaml
    overlays:
      - location: ./extensions.overlay.yaml
```

### Directly in Spec

Add extensions directly to your OpenAPI spec if you control it.

## What NOT to Do

- **Do NOT** use `x-speakeasy-retries` with non-idempotent POST operations without `x-speakeasy-idempotent: true`
- **Do NOT** mix pagination types on the same endpoint
- **Do NOT** use `x-speakeasy-unknown-values` on enums with only one value
- **Do NOT** add global headers that conflict with per-operation parameters

## Related Skills

- `manage-openapi-overlays` - Apply extensions via overlay files
- `customize-sdk-hooks` - Implement custom security in hooks
- `generate-sdk-for-typescript` - TypeScript-specific configuration
- `generate-sdk-for-python` - Python-specific configuration
