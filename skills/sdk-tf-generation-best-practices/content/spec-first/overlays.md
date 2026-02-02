---
short_description: Modify OpenAPI documents without editing the source
long_description: OpenAPI Overlays are separate documents that apply modifications to existing OpenAPI specifications using JSONPath. Useful for multi-consumer scenarios, vendor-specific customizations, and maintaining clean separation of concerns.
source:
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/openapi/overlays.mdx"
    ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
    last_reconciled: "2025-12-11"
  - repo: "speakeasy-sdks/visa-payments-typescript-sdk"
    path: ".speakeasy/overlays/"
    ref: "main"
    last_reconciled: "2025-12-11"
    notes: "Custom security schemes and metadata tracking patterns"
---

# OpenAPI Overlays

Overlays modify existing OpenAPI documents without editing the original file. Use overlays to apply customizations for different consumers, environments, or tooling.

> **Note:** OpenAPI Overlay Specification is at version 1.0.0. Speakeasy uses https://github.com/speakeasy-api/openapi-overlay implementation.

## Use Cases

- Separate API definition from tool-specific modifications
- Apply different customizations for different SDK languages
- Add vendor extensions without touching source document
- Share common modifications across multiple OpenAPI documents
- Maintain clean base specification managed by separate team

## Overlay Document Structure

### Basic Example

```yaml
overlay: 1.0.0
info:
  title: Overlay to fix the Speakeasy bar
  version: 0.0.1
actions:
  - target: "$.tags"
    description: Add a Snacks tag to the global tags list
    update:
      - name: Snacks
        description: All methods related to serving snacks
  - target: "$.paths['/dinner']"
    description: Remove all paths related to serving dinner
    remove: true
```

### Required Fields

**overlay** (string, required):
Version of Overlay Specification. Use `1.0.0`.

**info** (object, required):
Metadata about the overlay:
- `title` (string, required): Human-readable description
- `version` (string, required): Overlay version identifier

**actions** (array, required):
Ordered list of modifications to apply. Must have at least one action.

### Optional Fields

**extends** (string):
URL to the original OpenAPI document this overlay applies to.

**x-*** (any):
Extension fields for tooling-specific metadata.

## Action Object

Each action describes one modification:

```yaml
- target: "$.info"
  description: "Update API description"
  update:
    description: "The Speakeasy Bar API is a secret underground bar."
```

**target** (string, required):
JSONPath expression specifying where to apply the change.

**description** (string):
Human-readable explanation of this action.

**update** (any):
Object to merge with targeted location. Ignored if `remove` is true.

**remove** (boolean):
If true, remove targeted objects. Takes precedence over `update`.

## JSONPath Targeting

Speakeasy uses VMware Labs YAML JSONPath: https://github.com/vmware-labs/yaml-jsonpath

### Common Patterns

| Expression | Target |
|------------|--------|
| `$.info.title` | The title field of info object |
| `$.servers[0].url` | URL of first server |
| `$.paths['/drinks'].get.parameters` | Parameters of GET /drinks |
| `$.paths..parameters[?(@.in=='query')]` | All query parameters |
| `$.paths.*[?(@..parameters.*[?(@.in=='query')])]` | All operations with query params |
| `$.components.schemas.Drink` | Drink schema in components |

### Target Selection Rules

| Modification Type | Target |
|-------------------|--------|
| Update primitive value | The containing object |
| Update object | The object itself |
| Update array | The array itself |
| Add property to object | The object itself |
| Add item to array | The array itself |
| Remove property | The object itself |
| Remove array item | The array itself |

## Common Operations

### Update Info and Servers

```yaml
overlay: 1.0.0
info:
  title: Update Speakeasy Bar Info and Servers
  version: 1.0.0
actions:
  - target: $.info
    update:
      description: The Speakeasy Bar API is a secret underground bar.
      contact:
        name: Speakeasy Bar Support
        email: support@speakeasy.bar
  - target: $.servers
    update:
      - url: https://staging.speakeasy.bar/v1
        description: Staging server
      - url: https://api.speakeasy.bar/v1
        description: Production server
```

### Add Tags

```yaml
overlay: 1.0.0
info:
  title: Add Tags and Update Responses
  version: 1.0.0
actions:
  - target: $.tags
    update:
      - name: Drinks
        description: Operations related to managing drinks
      - name: Orders
        description: Operations related to order processing
```

### Add Tags to Operations with Query Parameters

```yaml
overlay: 1.0.0
info:
  title: Add Query Parameter Tags
  version: 1.0.0
actions:
  - target: $.paths.*[?(@..parameters.*[?(@.in=='query')])]['post','get','put','path','delete'].tags
    update:
      - hasQueryParameters
```

### Update Response Schemas

```yaml
overlay: 1.0.0
info:
  title: Update Drink Responses
  version: 1.0.0
actions:
  - target: $.paths['/drinks'].get.responses[200].content['application/json'].schema
    update:
      $ref: "#/components/schemas/DrinkList"
  - target: $.paths['/drinks/{drinkId}'].get.responses[200].content['application/json'].schema
    update:
      $ref: "#/components/schemas/Drink"
```

### Remove Deprecated Operations

```yaml
overlay: 1.0.0
info:
  title: Remove Deprecated Drink Operations
  version: 1.0.0
actions:
  - target: $.paths['/drinks'].*.deprecated
    remove: true
  - target: $.paths['/drinks/{drinkId}'].*.deprecated
    remove: true
```

### Add Speakeasy Extensions

```yaml
overlay: 1.0.0
info:
  title: Add Retry Configuration
  version: 1.0.0
actions:
  - target: $.paths['/drinks'].get
    update:
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 500
          maxInterval: 60000
          maxElapsedTime: 3600000
          exponent: 1.5
        statusCodes: ["5XX"]
        retryConnectionErrors: true
```

## Application Order

Overlays are applied in this sequence:

1. Locate the original OpenAPI document (via `extends` field or tool parameter)
2. Process each action in order from `actions` array:
   - Evaluate JSONPath `target` expression
   - If `remove: true`, delete targeted objects
   - Otherwise, merge `update` object with targeted objects
3. Return modified OpenAPI document

## Merge Behavior

When `update` is applied:
- Properties in `update` replace properties in target
- New properties from `update` are added to target
- Arrays are replaced entirely (not merged item-by-item)

## Speakeasy CLI Commands

**Apply overlay:**

```bash
speakeasy overlay apply -s spec.yaml -o overlay.yaml --out modified.yaml
```

**Validate overlay:**

```bash
speakeasy overlay validate -o overlay.yaml
```

## Visual Overlay Creator

Use the web tool to create and edit overlays visually:
https://overlay.speakeasy.com/

## Best Practices

1. Use descriptive `description` fields for each action
2. Test overlays against your base OpenAPI document
3. Version your overlays alongside your OpenAPI specs
4. Consider splitting complex modifications into multiple focused overlays
5. Document which overlays apply to which use cases
6. Validate the final merged document after applying overlays

## Example Workflow

```bash
# Start with base OpenAPI spec
speakeasy validate openapi -s base-spec.yaml

# Apply SDK-specific customizations
speakeasy overlay apply -s base-spec.yaml -o typescript-overlay.yaml --out ts-spec.yaml

# Generate SDK from customized spec
speakeasy quickstart --schema ts-spec.yaml --target typescript --out-dir ./sdk

# Apply different overlay for Python
speakeasy overlay apply -s base-spec.yaml -o python-overlay.yaml --out py-spec.yaml
speakeasy quickstart --schema py-spec.yaml --target python --out-dir ./sdk-python
```

## Common Patterns

### Hide Internal APIs

```yaml
actions:
  - target: $.paths['/internal/*']
    remove: true
```

### Add Examples

```yaml
actions:
  - target: $.paths['/drinks'].get.responses[200].content['application/json'].schema
    update:
      examples:
        - id: 1
          name: "Martini"
          price: 12.00
```

### Change Server URLs by Environment

```yaml
# production-overlay.yaml
actions:
  - target: $.servers
    update:
      - url: https://api.production.com
        description: Production server
```

```yaml
# staging-overlay.yaml
actions:
  - target: $.servers
    update:
      - url: https://api.staging.com
        description: Staging server
```

---

## Overlay Recipes

Production-tested overlay patterns extracted from real-world SDKs.

### Recipe: Open All Enums (Anti-Fragility)

For APIs with frequently changing enum values (AI models, payment methods, cloud regions),
automatically apply open enums to prevent SDK breakage when the API returns new values:

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: Open all enums
  version: 0.0.0
actions:
  - target: $..[?length(@.enum) > 1]
    description: Apply x-speakeasy-unknown-values to all enums with multiple values
    update:
      x-speakeasy-unknown-values: allow
```

**When to use:**
- AI/LLM APIs (model lists change weekly)
- Payment APIs (new payment methods added)
- Cloud APIs (new regions, instance types)
- Any API aggregating third-party services

**Why this matters:** Without open enums, the SDK throws validation errors when the API returns
an enum value not defined in the spec. This overlay makes all enums "open" so unknown values
pass through as strings instead of failing.

> **Pattern Source:** [OpenRouterTeam/python-sdk](https://github.com/OpenRouterTeam/python-sdk)

---

### Recipe: Add Global Headers via Overlay

Add SDK-wide headers without modifying the upstream spec. These become constructor options:

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: Add global headers
  version: 0.0.0
actions:
  # Add x-speakeasy-globals at root level
  - target: $
    description: Add global parameters for SDK-wide headers
    update:
      x-speakeasy-globals:
        parameters:
          - $ref: "#/components/parameters/AppIdentifier"
          - $ref: "#/components/parameters/TenantId"

  # Define the parameters in components
  - target: $.components
    description: Add parameter definitions
    update:
      parameters:
        AppIdentifier:
          name: X-App-Id
          in: header
          schema:
            type: string
          description: Application identifier for tracking
        TenantId:
          name: X-Tenant-Id
          in: header
          schema:
            type: string
          description: Multi-tenant identifier
```

**Result in SDK:**

```python
# Python SDK constructor now accepts these as options
client = MyAPI(
    api_key="...",
    app_identifier="my-app",  # Becomes X-App-Id header
    tenant_id="tenant-123",   # Becomes X-Tenant-Id header
)
```

**When to use:**
- Multi-tenant APIs requiring tenant identification
- APIs that track usage per application
- Adding correlation IDs or tracing headers
- Custom headers for API gateways

> **Pattern Source:** [OpenRouterTeam/python-sdk](https://github.com/OpenRouterTeam/python-sdk)

---

### Recipe: Remove Unsupported Content Types

Clean up specs by removing content types the SDK doesn't need to support:

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: Remove unsupported content types
  version: 0.0.0
actions:
  # Remove XML responses
  - target: $..responses.*.content["application/xml"]
    description: Remove application/xml responses
    remove: true

  # Remove RSS responses
  - target: $..responses.*.content["application/rss+xml"]
    description: Remove RSS responses
    remove: true

  # Remove related parameters
  - target: $..parameters[?@.name == "format"]
    description: Remove format parameter used for content negotiation
    remove: true
```

**When to use:**
- Upstream spec includes content types not needed for SDK
- Simplifying SDK by supporting only JSON
- Removing legacy formats (XML, SOAP)

> **Pattern Source:** [OpenRouterTeam/python-sdk](https://github.com/OpenRouterTeam/python-sdk)

---

### Recipe: Add Retry Configuration to All Operations

Apply consistent retry behavior across all API operations:

```yaml
overlay: 1.0.0
info:
  title: Add global retry configuration
  version: 0.0.0
actions:
  # Add retries to all GET operations
  - target: $.paths.*.get
    description: Add retry configuration to all GET operations
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

  # Add retries to idempotent POST operations (use with caution)
  - target: $.paths.*[?(@.post.x-speakeasy-idempotent == true)].post
    description: Add retry to idempotent POST operations
    update:
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 1000
          maxInterval: 30000
          maxElapsedTime: 120000
          exponent: 2
        statusCodes: ["5XX"]
```

---

### Recipe: Rename Operations for Better SDK Methods

Improve SDK method names without changing the underlying API:

```yaml
overlay: 1.0.0
info:
  title: Improve operation names
  version: 0.0.0
actions:
  # Rename verbose operation IDs
  - target: $.paths['/users/{userId}/permissions'].get
    update:
      x-speakeasy-name-override: getUserPermissions

  - target: $.paths['/users/{userId}/permissions'].put
    update:
      x-speakeasy-name-override: setUserPermissions

  # Group operations under a namespace
  - target: $.paths['/admin/*'].*.tags
    update:
      - Admin
```

---

### Recipe: Add Pagination to List Operations

Add Speakeasy pagination support to list endpoints:

```yaml
overlay: 1.0.0
info:
  title: Add pagination configuration
  version: 0.0.0
actions:
  - target: $.paths['/users'].get
    update:
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

  - target: $.paths['/events'].get
    update:
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

---

### Using Multiple Overlays

Chain overlays in `workflow.yaml` for modular customization:

```yaml
# .speakeasy/workflow.yaml
sources:
  my-api:
    inputs:
      - location: ./openapi.yaml
    overlays:
      # Apply in order
      - location: .speakeasy/overlays/open-enums.overlay.yaml
      - location: .speakeasy/overlays/add-headers.overlay.yaml
      - location: .speakeasy/overlays/retries.overlay.yaml
    output: .speakeasy/out.openapi.yaml
```

**Best Practice:** Keep overlays focused on single concerns:
- `open-enums.overlay.yaml` - Enum handling
- `global-headers.overlay.yaml` - SDK-wide parameters
- `retries.overlay.yaml` - Retry configuration
- `cleanup.overlay.yaml` - Remove unsupported features

---

## Multi-Overlay Workflow Patterns

For complex SDKs, use multiple overlays applied in sequence for separation of concerns.

### Production Example: 4-Overlay Architecture

This pattern from production SDKs separates concerns across dedicated overlays:

```yaml
# .speakeasy/workflow.yaml
sources:
    my-api:
        inputs:
            - location: https://api.example.com/openapi.yaml
        overlays:
            - location: overlay.yaml           # Main fixes (lint, TS, endpoints)
            - location: sdk-only-errors.yaml   # Error response fixes
            - location: docs-overlay.yaml      # Documentation tweaks
            - location: tests-overlay.yaml     # Test configuration
        output: processed-spec.json
        ruleset: myAPIRuleset
```

### Overlay Categories

| Category | Purpose | Typical Contents |
|----------|---------|------------------|
| **Main Fixes** | Lint errors, validation fixes | Required fields, parameter types, missing schemas |
| **Error Responses** | SDK-specific error handling | Error schemas, status code mappings |
| **Documentation** | Doc generation tweaks | x-speakeasy-usage-example, descriptions |
| **Test Configuration** | Control test generation | x-speakeasy-test: false for problematic endpoints |

### Category 1: Main Fixes Overlay

Fix lint errors and add missing configuration:

```yaml
# overlay.yaml
overlay: 1.0.0
info:
  title: Main SDK Fixes
  version: 1.0.0
actions:
  # Fix missing required field
  - target: $.paths['/resources'].post.requestBody.content['application/json'].schema
    update:
      required:
        - name
        - type

  # Add missing parameter description
  - target: $.paths['/resources/{id}'].get.parameters[0]
    update:
      description: Unique resource identifier

  # Fix operation ID for better method names
  - target: $.paths['/resources'].get
    update:
      operationId: listResources
```

### Category 2: Error Response Overlay

Define SDK-specific error handling:

```yaml
# sdk-only-errors.yaml
overlay: 1.0.0
info:
  title: Error Response Fixes
  version: 1.0.0
actions:
  # Add error response schema
  - target: $.paths['/resources'].post.responses
    update:
      "400":
        description: Bad Request
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
      "500":
        description: Internal Server Error
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"

  # Define error schema in components
  - target: $.components.schemas
    update:
      ErrorResponse:
        type: object
        properties:
          error:
            type: string
          message:
            type: string
          code:
            type: integer
```

### Category 3: Documentation Overlay

Enhance SDK documentation:

```yaml
# docs-overlay.yaml
overlay: 1.0.0
info:
  title: Documentation Enhancements
  version: 1.0.0
actions:
  # Add usage example
  - target: $.paths['/resources'].post
    update:
      x-speakeasy-usage-example: true

  # Improve description
  - target: $.paths['/resources'].get
    update:
      summary: List all resources with optional filtering
      description: |
        Returns a paginated list of resources. Use query parameters
        to filter results by status, type, or creation date.
```

### Category 4: Test Configuration Overlay

Control test generation for problematic endpoints:

```yaml
# tests-overlay.yaml
overlay: 1.0.0
info:
  title: Test Configuration
  version: 1.0.0
actions:
  # Disable tests for endpoints that require special setup
  - target: $.paths['/admin/dangerous-operation'].post
    update:
      x-speakeasy-test: false

  # Disable tests for endpoints with external dependencies
  - target: $.paths['/webhooks/callback'].post
    update:
      x-speakeasy-test: false

  # Disable tests for rate-limited endpoints
  - target: $.paths['/bulk-import'].post
    update:
      x-speakeasy-test: false
```

### Benefits of Multi-Overlay Architecture

1. **Separation of Concerns**: Each overlay has a single responsibility
2. **Easier Maintenance**: Update one category without touching others
3. **Team Collaboration**: Different teams can own different overlays
4. **Debugging**: Easier to identify which overlay causes issues
5. **Reusability**: Share common overlays across multiple SDKs

---

## Overlay Metadata Tracking

For large-scale method renaming or SDK modifications, use `x-speakeasy-metadata` to track changes with timestamps and before/after documentation.

### Metadata Structure

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: Speakeasy Modifications
  version: 0.0.1
  x-speakeasy-metadata:
    type: speakeasy-modifications
    before: ""
    after: ""
actions:
  - target: $["paths"]["/payments"]["post"]
    update:
      x-speakeasy-group: payments
      x-speakeasy-name-override: create
    x-speakeasy-metadata:
      after: sdk.payments.create()
      before: sdk.payments.createPayment()
      created_at: 1751909023486
      type: method-name
```

### Metadata Fields

| Field | Description |
|-------|-------------|
| `before` | Original SDK method signature |
| `after` | New SDK method signature |
| `created_at` | Unix timestamp of when modification was made |
| `type` | Classification of change (e.g., `method-name`, `group-change`) |

### Benefits

- **Audit Trail**: Track when and why methods were renamed
- **Documentation**: Auto-generate migration guides from before/after
- **Review**: Easier code review with clear intent
- **Rollback**: Identify specific changes to revert

### Example: Extensive Method Renaming

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: SDK Method Improvements
  version: 1.0.0
actions:
  - target: $["paths"]["/pts/v2/payments/{id}/voids"]["post"]
    update:
      x-speakeasy-group: voids
      x-speakeasy-name-override: post
    x-speakeasy-metadata:
      after: sdk.voids.post()
      before: sdk.void.voidPayment()
      created_at: 1751909023485
      type: method-name

  - target: $["paths"]["/pts/v2/payments"]["post"]
    update:
      x-speakeasy-name-override: create
    x-speakeasy-metadata:
      after: sdk.payments.create()
      before: sdk.payments.createPayment()
      created_at: 1751909023486
      type: method-name

  - target: $["paths"]["/pts/v2/payments/{id}/refunds"]["post"]
    update:
      x-speakeasy-group: refunds
      x-speakeasy-name-override: create
    x-speakeasy-metadata:
      after: sdk.refunds.create()
      before: sdk.refund.refundPayment()
      created_at: 1751909023487
      type: method-name
```

> **Pattern Source:** [speakeasy-sdks/visa-payments-typescript-sdk](https://github.com/speakeasy-sdks/visa-payments-typescript-sdk)

---

## Custom Security Schemes via Overlay

For APIs requiring complex authentication (HMAC signatures, multi-part credentials), define custom security schemes via overlay.

### Define Custom Security Scheme

```yaml
overlay: 1.0.0
x-speakeasy-jsonpath: rfc9535
info:
  title: Custom Security Scheme
  version: 0.0.0
actions:
  # Add the custom security scheme to components
  - target: $["components"]
    update:
      "securitySchemes":
        "myCustomScheme":
          "type": "http"
          "scheme": "custom"
          "x-speakeasy-custom-security-scheme":
            "schema":
              "type": "object"
              "properties":
                "keyId":
                  "type": "string"
                  "description": "API Key ID (otherwise known as 'key')"
                  "example": "bbccd1f1-58e9-440b-96af-77d2c7576aec"
                "keySecret":
                  "type": "string"
                  "description": "API Secret for HMAC signing"
                  "example": "app-speakeasy-123"
                "merchantId":
                  "type": "string"
                  "description": "Merchant/Organization identifier"
                  "example": "merchant_12345"
              "required": []

  # Apply the security scheme globally
  - target: $
    update:
      "security": [{"myCustomScheme": []}]
```

### How It Works

1. **Schema Definition**: The `x-speakeasy-custom-security-scheme.schema` defines credential properties
2. **Type Generation**: Speakeasy generates a `Security` type with these properties
3. **Environment Variables**: With `envVarPrefix: MYAPI`, generates support for:
   - `MYAPI_KEY_ID`
   - `MYAPI_KEY_SECRET`
   - `MYAPI_MERCHANT_ID`
4. **Hook Integration**: Credentials flow to hooks via `hookCtx.securitySource`

### gen.yaml Configuration

```yaml
typescript:
  envVarPrefix: MYAPI
  flattenGlobalSecurity: true
```

### Generated Security Type

```typescript
// src/models/security.ts (generated)
export type Security = {
  /** API Key ID (otherwise known as 'key') */
  keyId?: string | undefined;
  /** API Secret for HMAC signing */
  keySecret?: string | undefined;
  /** Merchant/Organization identifier */
  merchantId?: string | undefined;
};
```

### Hook Implementation

See `sdk-customization/hooks.md` for the complete `BeforeRequestHook` implementation that:
- Extracts credentials from security context
- Computes HMAC-SHA256 signatures
- Adds HTTP signature headers to requests

### Usage in SDK

```typescript
import { SDK } from "my-sdk";

// Via environment variables
const sdk = new SDK();

// Or via constructor
const sdk = new SDK({
  security: {
    keyId: "your-key-id",
    keySecret: "base64-encoded-secret",
    merchantId: "your-merchant-id",
  },
});
```

### Ignoring Unsupported Operations

Often paired with `x-speakeasy-ignore` to hide operations not ready for SDK:

```yaml
actions:
  # Hide operations that require different auth or aren't ready
  - target: $["paths"]["/admin/internal-only"]
    update:
      "x-speakeasy-ignore": true

  - target: $["paths"]["/legacy/deprecated-endpoint"]
    update:
      "x-speakeasy-ignore": true
```

> **Pattern Source:** [speakeasy-sdks/visa-payments-typescript-sdk](https://github.com/speakeasy-sdks/visa-payments-typescript-sdk)

### Validating Multi-Overlay Workflows

```bash
# Validate each overlay individually
speakeasy overlay validate -o overlay.yaml
speakeasy overlay validate -o sdk-only-errors.yaml
speakeasy overlay validate -o docs-overlay.yaml
speakeasy overlay validate -o tests-overlay.yaml

# Run full workflow to test combined output
speakeasy run

# Inspect the processed spec
speakeasy validate openapi -s processed-spec.json
```

## Reference

- Overlay Spec: https://github.com/OAI/Overlay-Specification
- Speakeasy Implementation: https://github.com/speakeasy-api/openapi-overlay
- JSONPath Spec: https://datatracker.ietf.org/wg/jsonpath/documents/

---

## Pre-defined TODO List

When working with OpenAPI overlays, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Identify modifications needed to base spec | Identifying needed modifications |
| 2 | Create overlay document with required structure | Creating overlay document |
| 3 | Write JSONPath target expressions | Writing JSONPath expressions |
| 4 | Define update or remove actions | Defining actions |
| 5 | Validate overlay with speakeasy overlay validate | Validating overlay |
| 6 | Apply overlay with speakeasy overlay apply | Applying overlay |
| 7 | Validate merged document | Validating merged document |
| 8 | Submit feedback if documentation was unclear or incomplete | Submitting feedback |

**Usage:**
```
TodoWrite([
  {content: "Identify modifications needed to base spec", status: "pending", activeForm: "Identifying needed modifications"},
  {content: "Create overlay document with required structure", status: "pending", activeForm: "Creating overlay document"},
  {content: "Write JSONPath target expressions", status: "pending", activeForm: "Writing JSONPath expressions"},
  {content: "Define update or remove actions", status: "pending", activeForm: "Defining actions"},
  {content: "Validate overlay with speakeasy overlay validate", status: "pending", activeForm: "Validating overlay"},
  {content: "Apply overlay with speakeasy overlay apply", status: "pending", activeForm: "Applying overlay"},
  {content: "Validate merged document", status: "pending", activeForm: "Validating merged document"},
  {content: "Submit feedback if documentation was unclear or incomplete", status: "pending", activeForm: "Submitting feedback"}
])
```

> **Feedback:** If a JSONPath expression did not match as expected, a recipe did not apply correctly, or overlay behavior was undocumented, run:
> ```bash
> speakeasy agent feedback -m "Description of the issue" --context-path "spec-first/overlays.md"
> ```

