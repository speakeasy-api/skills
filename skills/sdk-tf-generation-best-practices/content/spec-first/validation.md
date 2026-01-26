---
short_description: Validate and improve OpenAPI specifications
long_description: Use Speakeasy CLI to validate OpenAPI documents for correctness, SDK readiness, and best practices. Includes linting rules, common issues, and quality improvements.
source:
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/openapi/index.mdx,schemas.mdx,requests.mdx,responses.mdx"
    ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
    last_reconciled: "2025-12-11"
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/docs/sdks/prep-openapi/linting.mdx"
    ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
    last_reconciled: "2025-12-11"
    notes: "Added comprehensive linting rules, custom functions, and ruleset documentation"
---

# OpenAPI Validation

Validate OpenAPI specifications for correctness, SDK generation readiness, and best practices.

## Validation Command

```bash
speakeasy validate openapi -s spec.yaml
```

Output lists errors, warnings, and hints with line references when available.

## Linting Command

More detailed analysis with configurable rules:

```bash
speakeasy lint openapi --schema spec.yaml
```

## Common Validation Issues

### Missing Required Fields

**Error:**
```text
info object missing required 'version' field
```

**Fix:**

```yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0  # Required
```

### Invalid Server URLs

**Error:**
```text
servers array is empty or missing
```

**Fix:**

```yaml
servers:
  - url: https://api.example.com
    description: Production server
```

### Missing Operation IDs

**Warning:**
```text
operation missing operationId
```

**Fix:**

```yaml
paths:
  /users:
    get:
      operationId: listUsers  # Required for SDK generation
      summary: List users
```

### Poor Operation IDs

**Warning:**
```text
operationId 'get_users_users__user_id__get' is not descriptive
```

**Fix:**

```yaml
paths:
  /users/{userId}:
    get:
      operationId: getUser  # Clear and concise
```

### Missing Response Schemas

**Warning:**
```text
response missing schema definition
```

**Fix:**

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
```

### Missing Examples

**Hint:**
```text
schema missing examples
```

**Fix:**

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        name:
          type: string
          examples:
            - "John Doe"
        email:
          type: string
          format: email
          examples:
            - "john@example.com"
```

### Inconsistent Parameter Names

**Warning:**
```text
parameter naming inconsistent: 'userId' vs 'user_id'
```

**Fix:** Choose one naming convention (camelCase or snake_case) and use consistently.

### Missing Descriptions

**Hint:**
```text
operation missing description
```

**Fix:**

```yaml
paths:
  /users:
    get:
      summary: List users
      description: Returns a paginated list of all users in the system. Results can be filtered by status and role.
      operationId: listUsers
```

## Request Validation

### Missing Content-Type

**Error:**
```text
POST operation missing requestBody
```

**Fix:**

```yaml
paths:
  /users:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
```

### Parameter Validation

**Good parameter definition:**

```yaml
parameters:
  - name: userId
    in: path
    required: true
    description: The unique identifier of the user
    schema:
      type: string
      format: uuid
    example: "123e4567-e89b-12d3-a456-426614174000"
```

**Issues to avoid:**
- Missing `required` for path parameters
- No `description`
- No `example`
- Vague names like `id` without context

## Response Validation

### Complete Response Definition

```yaml
responses:
  '200':
    description: Successful operation
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
  '400':
    description: Bad request - Invalid input
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
  '404':
    description: User not found
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
  '500':
    description: Internal server error
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
```

### Missing Error Responses

**Warning:**
```text
operation missing error response definitions
```

Always document at least:
- `400` - Bad Request
- `401` - Unauthorized (if auth required)
- `404` - Not Found (for single resource endpoints)
- `500` - Internal Server Error

## Schema Validation

### Required vs Optional

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
          format: email
        phone:
          type: string
      required:
        - id      # Always required
        - name    # Always required
        - email   # Always required
        # phone is optional
```

### Type Constraints

```yaml
properties:
  age:
    type: integer
    minimum: 0
    maximum: 150
  username:
    type: string
    minLength: 3
    maxLength: 50
    pattern: "^[a-zA-Z0-9_]+$"
  tags:
    type: array
    minItems: 1
    maxItems: 10
    items:
      type: string
```

### Format Validation

Use appropriate formats:

```yaml
properties:
  email:
    type: string
    format: email      # Not just 'string'
  website:
    type: string
    format: uri
  birthdate:
    type: string
    format: date       # YYYY-MM-DD
  createdAt:
    type: string
    format: date-time  # RFC 3339
  id:
    type: string
    format: uuid
```

## Tag Validation

### Well-Organized Tags

```yaml
tags:
  - name: Users
    description: User management operations
  - name: Orders
    description: Order processing operations

paths:
  /users:
    get:
      tags: [Users]
  /orders:
    get:
      tags: [Orders]
```

**Issues to avoid:**
- Missing tag definitions in root
- Inconsistent tag names (Users vs users)
- Too many tags per operation
- Meaningless tags (API, Endpoints)

## Best Practices Validation

### OpenAPI Version

```yaml
openapi: 3.1.0  # Use latest stable version
```

### Info Object

```yaml
info:
  title: My API
  version: 1.0.0
  description: |
    Complete description of API purpose and functionality.

    ## Authentication
    API uses Bearer token authentication.

    ## Rate Limiting
    100 requests per minute per user.
  contact:
    name: API Support
    email: api@example.com
    url: https://example.com/support
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html
```

### Component Reusability

**Bad:**

```yaml
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  id: ...
                  name: ...
```

**Good:**

```yaml
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id: ...
        name: ...
```

## Linting Configuration

### Default Rulesets

Speakeasy provides five built-in rulesets:

1. **speakeasy-recommended** (default) - Ensures quality for SDK generation
2. **speakeasy-generation** - Required rules for successful SDK generation
3. **speakeasy-openapi** - General OpenAPI validity
4. **vacuum** - Extended validation rules
5. **owasp** - Security-focused rules

### Custom Configuration

Configure in `.speakeasy/lint.yaml`:

```yaml
lintVersion: 1.0.0
defaultRuleset: myRuleset
rulesets:
  myRuleset:
    rulesets:
      - speakeasy-recommended  # Base ruleset
    rules:
      # Override specific rule severity
      validate-enums:
        severity: warn
      # Add custom rule
      paths-kebab-case:
        description: Paths should be kebab-case
        message: "{{property}} should be kebab-case"
        severity: warn
        given: $.paths[*]~
        then:
          functionOptions:
            match: "^(\\/|[a-z0-9-.]+|{[a-zA-Z0-9_]+})+$"
```

### Key Linting Rules

**Critical (error):**
- `operation-operationId` - Every operation must have operationId
- `operation-operationId-unique` - operationIds must be unique
- `validate-parameters` - Parameters must be unique with non-empty names
- `validate-security` - Security schemes must be correctly defined
- `duplicate-operation-name` - Prevent SDK method name collisions
- `validate-types` - Data types must be valid for generation
- `path-params` - Path parameters must be defined and valid

**Important (warn):**
- `operation-tags` - Operations should have tags
- `operation-tag-defined` - Tags must be defined globally
- `operation-description` - Operations should have descriptions
- `oas3-parameter-description` - Parameters should have descriptions
- `oas3-missing-example` - Add examples where possible
- `operation-4xx-response` - Include error responses

**Security (owasp ruleset):**
- `owasp-protection-global-unsafe` - API should require authentication
- `owasp-no-http-basic` - Avoid HTTP Basic auth
- `owasp-security-hosts-https-oas3` - Use HTTPS for all servers
- `owasp-no-api-keys-in-url` - API keys should not be in URLs
- `owasp-define-error-responses-401` - Document 401 responses
- `owasp-rate-limit` - Define rate limiting

### Using Custom Rules

**Run with specific ruleset:**

```bash
speakeasy lint openapi -r myRuleset -s openapi.yaml
```

**Configure in workflow.yaml:**

```yaml
sources:
  my-api:
    inputs:
      - location: ./openapi.yaml
    ruleset: myRuleset
```

### Custom Functions

For complex validation beyond pattern matching, write custom functions in JavaScript or Go.

Place in `.speakeasy/functions/`:

```javascript
// .speakeasy/functions/validate-version.js
module.exports = (input, options, context) => {
  if (!input.match(/^\d+\.\d+\.\d+$/)) {
    return [
      {
        message: "Version must follow semver format (x.y.z)",
      },
    ];
  }
};
```

Use in lint.yaml:

```yaml
rules:
  version-format:
    description: Ensure version follows semver
    given: $.info.version
    then:
      function: validate-version
```

## Validation Workflow

1. **Generate or write OpenAPI spec**
2. **Basic validation:**
   ```bash
   speakeasy validate openapi -s spec.yaml
   ```
3. **Fix errors** (must be resolved)
4. **Detailed linting:**
   ```bash
   speakeasy lint openapi --schema spec.yaml
   ```
5. **Fix warnings** (should be resolved)
6. **Address hints** (nice to have)
7. **Generate SDK:**
   ```bash
   speakeasy quickstart --schema spec.yaml --target typescript --out-dir ./sdk
   ```

## CI/CD Validation

```yaml
# .github/workflows/validate-openapi.yml
name: Validate OpenAPI

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Speakeasy
        uses: speakeasy-api/speakeasy-action/setup@v1

      - name: Validate OpenAPI
        run: speakeasy validate openapi -s openapi.yaml

      - name: Lint OpenAPI
        run: speakeasy lint openapi --schema openapi.yaml
```

## Common Transformations

### Swagger 2.0 to OpenAPI 3.x

```bash
speakeasy openapi transform convert-swagger -s swagger2.json -o openapi.yaml
```

### Apply Overlays

```bash
speakeasy overlay apply -s spec.yaml -o overlay.yaml --out modified.yaml
```

## Quality Metrics

Good OpenAPI specs have:

- All operations have `operationId`
- All operations have `summary` and `description`
- All parameters have `description` and `example`
- All schemas have `examples`
- All responses have schemas
- Error responses documented (400, 401, 404, 500)
- Tags defined and consistently applied
- Security schemes defined
- Server URLs provided
- No validation errors
- Minimal warnings

## Editor Integration

Use the Speakeasy VS Code extension for real-time validation. Search "Speakeasy" in the VS Code extension marketplace.

## Reference

- SDK contract testing: `../sdk-testing/contract-testing.md`

---

## Pre-defined TODO List

When validating OpenAPI specifications, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Run speakeasy validate openapi -s spec.yaml | Running speakeasy validate |
| 2 | Fix all validation errors | Fixing validation errors |
| 3 | Add missing operationId to all operations | Adding missing operationId |
| 4 | Add descriptions to operations and parameters | Adding descriptions |
| 5 | Add examples to all schemas | Adding examples to schemas |
| 6 | Define error responses (400, 401, 404, 500) | Defining error responses |
| 7 | Run speakeasy lint for detailed analysis | Running speakeasy lint |
| 8 | Address warnings and hints | Addressing warnings and hints |

**Usage:**
```javascript
TodoWrite([
  {content: "Run speakeasy validate openapi -s spec.yaml", status: "pending", activeForm: "Running speakeasy validate"},
  {content: "Fix all validation errors", status: "pending", activeForm: "Fixing validation errors"},
  {content: "Add missing operationId to all operations", status: "pending", activeForm: "Adding missing operationId"},
  {content: "Add descriptions to operations and parameters", status: "pending", activeForm: "Adding descriptions"},
  {content: "Add examples to all schemas", status: "pending", activeForm: "Adding examples to schemas"},
  {content: "Define error responses (400, 401, 404, 500)", status: "pending", activeForm: "Defining error responses"},
  {content: "Run speakeasy lint for detailed analysis", status: "pending", activeForm: "Running speakeasy lint"},
  {content: "Address warnings and hints", status: "pending", activeForm: "Addressing warnings and hints"}
])
```

