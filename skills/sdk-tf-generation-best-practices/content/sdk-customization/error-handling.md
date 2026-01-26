---
short_description: "Configure typed SDK errors and error behavior"
long_description: |
  Guide for configuring SDK error handling using OpenAPI response schemas and
  the x-speakeasy-errors extension. Covers default error behavior, custom error
  classes, error message configuration, and advanced error handling patterns.
source:
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/docs/sdks/customize/errors"
    ref: "main"
    last_reconciled: "2025-12-11"
related:
  - "../plans/sdk-generation.md"
  - "./hooks.md"
  - "../sdk-languages/typescript.md"
  - "../sdk-languages/python.md"
  - "../sdk-languages/go.md"
---

# SDK Error Handling Configuration

Configure SDK error handling using OpenAPI response schemas and the `x-speakeasy-errors` extension.

## Default Error Handling

Without configuration, Speakeasy SDKs handle errors as follows:

1. **Non-2xx responses**: throws either a typed error (when a response schema is defined) or a default SDK error (raw response)
2. **SDKValidationError**: thrown when an error body cannot be parsed or does not match the expected schema
3. **HTTPClientError (network/IO)**: connection failures, timeouts, DNS, and TLS errors are surfaced from the underlying client

### Default Error Example (TypeScript)

```typescript
import { Drinks } from "drinks";
import {
  SDKValidationError,
  SDKError,
  HTTPClientError,
} from "drinks/models/errors/index.js";

const drinks = new Drinks();

async function run() {
  let result;
  try {
    result = await drinks.listDrinks();
    console.log(result);
  } catch (err) {
    // 1. Default SDK Errors: Non-2xx responses without custom error schemas
    if (err instanceof SDKError) {
      console.error(err.statusCode);
      console.error(err.message);
      console.error(err.body); // Raw response body as string
      return;
    }

    // 2. Validation Errors: Error response parsing failed
    if (err instanceof SDKValidationError) {
      console.error(err.rawValue);
      console.error(err.pretty()); // Pretty-printed validation errors
      return;
    }

    // 3. Network/IO Errors: Connection failures (escalated verbatim)
    if (err instanceof HTTPClientError) {
      console.error(err.name);
      console.error(err.message);
      return;
    }

    throw err;
  }
}
```

---

## Recommended Configuration

Define named error classes with structured schemas for specific error types.

### OpenAPI Error Schema Configuration

```yaml
openapi: 3.1.0
info:
  title: The Speakeasy Bar
  version: 1.0.0
servers:
  - url: https://speakeasy.bar
paths:
  /drinks:
    get:
      operationId: listDrinks
      summary: Get a list of drinks
      responses:
        "200":
          description: A list of drinks
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Drink"
        "400":
          description: Bad Request
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/BadRequestError"
        "401":
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UnauthorizedError"
        "404":
          description: Not Found
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/NotFoundError"
components:
  schemas:
    Drink:
      type: object
      title: Drink
      properties:
        name:
          type: string
    BadRequestError:
      type: object
      title: BadRequestError
      properties:
        statusCode:
          type: integer
        error:
          type: string
        typeName:
          type: string
        message:
          type: string
          x-speakeasy-error-message: true
        detail:
          oneOf:
            - type: string
            - type: object
        ref:
          type: string
    UnauthorizedError:
      type: object
      title: UnauthorizedError
      properties:
        message:
          type: string
          x-speakeasy-error-message: true
        code:
          type: string
    NotFoundError:
      type: object
      title: NotFoundError
      properties:
        message:
          type: string
          x-speakeasy-error-message: true
        resource:
          type: string
        resourceId:
          type: string
```

> **Note:** Defining 5XX responses is generally not recommended as the server is not always in control of the response. If a JSON schema is specified for a 5XX response and the response doesn't match the schema, the SDK will raise a `SDKValidationError`.

### Error Message Configuration

Use `x-speakeasy-error-message: true` to configure the error message propagated to `err.message` in the SDK:

```yaml
properties:
  message:
    type: string
    x-speakeasy-error-message: true
```

### Custom Error Handling Example (TypeScript)

```typescript
import { Drinks } from "drinks";
import {
  SDKValidationError,
  SDKError,
  HTTPClientError,
  BadRequestError,
  UnauthorizedError,
  NotFoundError,
} from "drinks/models/errors/index.js";

const drinks = new Drinks();

async function run() {
  let result;
  try {
    result = await drinks.listDrinks();
    console.log(result);
  } catch (err) {
    // Custom typed errors with structured schemas and hoisted properties
    if (err instanceof BadRequestError) {
      // Access hoisted properties directly
      console.error(err.message);
      console.error(err.typeName);
      console.error(err.detail);
      console.error(err.ref);

      // Or access the full error data object
      console.error(err.data$);
      return;
    }

    if (err instanceof UnauthorizedError) {
      // Access structured error fields
      console.error(err.message);
      console.error(err.code);
      return;
    }

    if (err instanceof NotFoundError) {
      // Access resource-specific error details
      console.error(err.message);
      console.error(err.resource);
      console.error(err.resourceId);
      return;
    }

    // Default SDK Errors: Non-2xx responses without custom error schemas
    if (err instanceof SDKError) {
      console.error(err.statusCode);
      console.error(err.message);
      console.error(err.body);
      return;
    }

    // Validation Errors: Error response parsing failed
    if (err instanceof SDKValidationError) {
      console.error(err.rawValue);
      console.error(err.pretty());
      return;
    }

    // Network/IO Errors: Connection failures (escalated verbatim)
    if (err instanceof HTTPClientError) {
      console.error(err.name);
      console.error(err.message);
      return;
    }

    throw err;
  }
}
```

---

## Advanced Configuration

### Renaming Default Error Class

Change the name of the default error class in `gen.yaml`:

```yaml
typescript:
  defaultErrorName: MySDKError
```

```yaml
python:
  defaultErrorName: MySDKException
```

```yaml
go:
  defaultErrorName: MySDKError
```

### Handling Default Response Code

The `default` response code is a catch-all for any status code not explicitly defined. By default, Speakeasy SDKs treat default responses as non-error responses. To treat it as a specific error type, define it in `x-speakeasy-errors`:

```yaml
x-speakeasy-errors:
  statusCodes:
    - "default"
```

### The x-speakeasy-errors Extension

Override default error-handling behavior at the `paths`, `path item`, or `operation` level. Deeper levels merge or override parent behavior.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `override` | `boolean` | If `true`, the statusCodes list overrides any parent `x-speakeasy-errors` extension. Defaults to `false`. |
| `statusCodes` | `[string]` | Array of status codes to handle as errors. Merges with parent unless override is `true`. Each code must be in quotes. Wildcards supported (e.g., `5XX`). |

### x-speakeasy-errors Example

```yaml
paths:
  x-speakeasy-errors:
    statusCodes:
      - 4XX  # Handle all 400-499 as errors
      - 5XX
  /drinks:
    x-speakeasy-errors:
      override: true  # Only handle 404 and 500 as errors for this path
      statusCodes:
        - 404
        - 500
    get:
      x-speakeasy-errors:
        statusCodes:  # Merges with parent: 404, 401, 500, 503
          - 401
          - 503
      operationId: getDrinks
      responses:
        200:
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Drink"
        401:
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AuthError"
        404:
          description: Not Found  # No schema = standard SDK error
        500:
          description: Internal Server Error
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
        503:
          description: Service Unavailable
```

### Disabling Default Error Handling

Disable automatic error handling for 4XX and 5XX status codes:

```yaml
go:
  clientServerStatusCodesAsErrors: false
```

```yaml
typescript:
  clientServerStatusCodesAsErrors: false
```

---

## Error Schema Patterns

### Basic Error Schema

```yaml
components:
  schemas:
    Error:
      type: object
      title: Error
      properties:
        message:
          type: string
          x-speakeasy-error-message: true
        code:
          type: string
```

### Detailed Error Schema

```yaml
components:
  schemas:
    DetailedError:
      type: object
      title: DetailedError
      properties:
        message:
          type: string
          x-speakeasy-error-message: true
        statusCode:
          type: integer
        errorCode:
          type: string
        timestamp:
          type: string
          format: date-time
        path:
          type: string
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              issue:
                type: string
```

### Validation Error Schema

```yaml
components:
  schemas:
    ValidationError:
      type: object
      title: ValidationError
      properties:
        message:
          type: string
          x-speakeasy-error-message: true
        errors:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
              code:
                type: string
```

### Rate Limit Error Schema

```yaml
components:
  schemas:
    RateLimitError:
      type: object
      title: RateLimitError
      properties:
        message:
          type: string
          x-speakeasy-error-message: true
        retryAfter:
          type: integer
          description: Seconds until retry is allowed
        limit:
          type: integer
        remaining:
          type: integer
```

---

## Error Handling by Language

### TypeScript Error Hierarchy

```text
Error
├── HTTPClientError (network/IO errors)
├── SDKValidationError (parsing failures)
├── SDKError (default error)
└── Custom Errors
    ├── BadRequestError
    ├── UnauthorizedError
    ├── NotFoundError
    └── ...
```

### Python Error Hierarchy

```text
Exception
├── HTTPClientError (network/IO errors)
├── SDKValidationError (parsing failures)
├── APIError (default error)
└── Custom Errors
    ├── BadRequestError
    ├── UnauthorizedError
    ├── NotFoundError
    └── ...
```

### Go Error Handling

```go
res, err := sdk.Drinks.ListDrinks(ctx)
if err != nil {
    // Type assertion for custom errors
    var badRequestErr *sdkerrors.BadRequestError
    if errors.As(err, &badRequestErr) {
        fmt.Printf("Bad Request: %s\n", badRequestErr.Message)
        fmt.Printf("Detail: %v\n", badRequestErr.Detail)
        return
    }

    // Default SDK error
    var sdkErr *sdkerrors.SDKError
    if errors.As(err, &sdkErr) {
        fmt.Printf("SDK Error: %d - %s\n", sdkErr.StatusCode, sdkErr.Message)
        return
    }

    // Other errors
    fmt.Printf("Error: %v\n", err)
    return
}
```

---

## Best Practices

1. **Define 4XX errors**: Always define schemas for client errors (400-499)
2. **Avoid 5XX schemas**: Don't define strict schemas for server errors; they may not match during failures
3. **Use error messages**: Always use `x-speakeasy-error-message` to identify the primary error message field
4. **Descriptive error names**: Use meaningful error class names (e.g., `ValidationError`, not `Error400`)
5. **Include context**: Add fields like `requestId`, `timestamp`, `path` for debugging
6. **Hoisted properties**: Design error schemas with flat structures for easy property access
7. **Validation errors**: Use array-based `errors` field for validation error details
8. **Rate limiting**: Include `retryAfter` field in rate limit error schemas
9. **Documentation**: Document error types and their properties in OpenAPI descriptions
10. **Testing**: Test error handling for all defined error types

---

## Pre-defined TODO List

When configuring SDK error handling, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Define error schemas for 4XX responses | Defining error schemas |
| 2 | Add x-speakeasy-error-message to error schemas | Configuring error messages |
| 3 | Configure x-speakeasy-errors extension if needed | Configuring error handling behavior |
| 4 | Set defaultErrorName in gen.yaml | Setting default error name |
| 5 | Test error handling for each error type | Testing error handling |
| 6 | Test validation error scenarios | Testing validation errors |
| 7 | Test network error handling | Testing network errors |
| 8 | Document error types in README | Documenting error types |

**Usage:**
```javascript
TodoWrite([
  {content: "Define error schemas for 4XX responses", status: "pending", activeForm: "Defining error schemas"},
  {content: "Add x-speakeasy-error-message to error schemas", status: "pending", activeForm: "Configuring error messages"},
  {content: "Configure x-speakeasy-errors extension if needed", status: "pending", activeForm: "Configuring error handling behavior"},
  {content: "Set defaultErrorName in gen.yaml", status: "pending", activeForm: "Setting default error name"},
  {content: "Test error handling for each error type", status: "pending", activeForm: "Testing error handling"},
  {content: "Test validation error scenarios", status: "pending", activeForm: "Testing validation errors"},
  {content: "Test network error handling", status: "pending", activeForm: "Testing network errors"},
  {content: "Document error types in README", status: "pending", activeForm: "Documenting error types"}
])
```
