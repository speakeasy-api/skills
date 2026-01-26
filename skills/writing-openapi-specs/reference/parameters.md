# Parameters

Best practices for defining parameters in OpenAPI specifications.

## Parameter Locations

Parameters can appear in four locations:

| Location | Use For | Example |
|----------|---------|---------|
| `path` | Resource identifiers in URL | `/users/{id}` |
| `query` | Filtering, pagination, sorting | `/users?limit=20&role=admin` |
| `header` | Metadata, authentication | `Authorization`, `X-Request-ID` |
| `cookie` | Session data, preferences | `session_id` |

## Path Parameters

Path parameters are part of the URL path and identify specific resources.

### Basic Path Parameter

```yaml
paths:
  /users/{id}:
    get:
      operationId: users_get
      parameters:
        - name: id
          in: path
          required: true
          description: User ID
          schema:
            type: integer
```

### Multiple Path Parameters

```yaml
paths:
  /organizations/{org_id}/projects/{project_id}:
    get:
      operationId: projects_get
      parameters:
        - name: org_id
          in: path
          required: true
          description: Organization ID
          schema:
            type: string
            format: uuid

        - name: project_id
          in: path
          required: true
          description: Project ID
          schema:
            type: integer
```

### Path Parameter Best Practices

**Do**:
- Always set `required: true` (path parameters are always required)
- Use lowercase with underscores: `user_id`, `project_id`
- Use appropriate types (integer for numeric IDs, string for UUIDs)
- Provide clear descriptions

**Avoid**:
```yaml
# ❌ camelCase in path
/users/{userId}

# ✓ Use snake_case
/users/{user_id}

# ❌ Optional path parameter
- name: id
  in: path
  required: false  # Path params must be required

# ❌ Missing description
- name: id
  in: path
  required: true
  schema: {type: integer}
```

## Query Parameters

Query parameters filter, sort, paginate, or modify responses.

### Pagination Parameters

```yaml
parameters:
  - name: limit
    in: query
    description: Maximum number of items to return
    schema:
      type: integer
      minimum: 1
      maximum: 100
      default: 20

  - name: offset
    in: query
    description: Number of items to skip
    schema:
      type: integer
      minimum: 0
      default: 0
```

### Filtering Parameters

```yaml
parameters:
  - name: status
    in: query
    description: Filter by status
    schema:
      type: string
      enum: [pending, approved, rejected]

  - name: role
    in: query
    description: Filter by user role
    schema:
      type: string
      enum: [admin, user, guest]

  - name: created_after
    in: query
    description: Filter items created after this date
    schema:
      type: string
      format: date
      example: "2024-01-01"

  - name: email
    in: query
    description: Filter by email (partial match)
    schema:
      type: string
      format: email
```

### Sorting Parameters

```yaml
parameters:
  - name: sort_by
    in: query
    description: Field to sort by
    schema:
      type: string
      enum: [created_at, updated_at, name, email]
      default: created_at

  - name: order
    in: query
    description: Sort order
    schema:
      type: string
      enum: [asc, desc]
      default: desc
```

### Boolean Parameters

```yaml
parameters:
  - name: include_deleted
    in: query
    description: Include deleted items in results
    schema:
      type: boolean
      default: false

  - name: active_only
    in: query
    description: Return only active items
    schema:
      type: boolean
      default: true
```

### Array Parameters

```yaml
parameters:
  - name: tags
    in: query
    description: Filter by tags (can specify multiple)
    schema:
      type: array
      items:
        type: string
    style: form
    explode: true
    example: ["api", "documentation", "sdk"]
    # Results in: ?tags=api&tags=documentation&tags=sdk

  - name: ids
    in: query
    description: List of IDs to retrieve
    schema:
      type: array
      items:
        type: integer
    style: form
    explode: false
    example: [1, 2, 3]
    # Results in: ?ids=1,2,3
```

### Query Parameter Serialization

Control how arrays and objects are serialized:

| Style | Explode | Array Example | Result |
|-------|---------|---------------|--------|
| `form` | `true` | `[1, 2, 3]` | `?id=1&id=2&id=3` |
| `form` | `false` | `[1, 2, 3]` | `?id=1,2,3` |
| `spaceDelimited` | `false` | `[1, 2, 3]` | `?id=1%202%203` |
| `pipeDelimited` | `false` | `[1, 2, 3]` | `?id=1\|2\|3` |

```yaml
parameters:
  # Form style, exploded (most common for arrays)
  - name: tags
    in: query
    schema:
      type: array
      items: {type: string}
    style: form
    explode: true
    # ?tags=api&tags=sdk

  # Form style, not exploded (comma-separated)
  - name: ids
    in: query
    schema:
      type: array
      items: {type: integer}
    style: form
    explode: false
    # ?ids=1,2,3
```

### Required vs Optional

```yaml
# Required parameter
- name: api_key
  in: query
  required: true
  description: API key for authentication
  schema:
    type: string

# Optional parameter with default
- name: format
  in: query
  required: false
  description: Response format
  schema:
    type: string
    enum: [json, xml]
    default: json
```

**Most query parameters should be optional** with sensible defaults.

## Header Parameters

Header parameters pass metadata, authentication, or special instructions.

### Authentication Header

```yaml
parameters:
  - name: Authorization
    in: header
    required: true
    description: Bearer token for authentication
    schema:
      type: string
      example: "Bearer eyJhbGc..."
```

**Note**: For standard authentication schemes, prefer using `security` instead of manual header parameters. See [reference/security.md](reference/security.md).

### Custom Headers

```yaml
parameters:
  - name: X-Request-ID
    in: header
    description: Unique request identifier for tracing
    schema:
      type: string
      format: uuid

  - name: X-Idempotency-Key
    in: header
    required: true
    description: Idempotency key to prevent duplicate requests
    schema:
      type: string
      example: "a7b8c9d0-e1f2-4567-8901-234567890abc"

  - name: X-API-Version
    in: header
    description: API version override
    schema:
      type: string
      enum: ["2023-01-01", "2024-01-01"]
      example: "2024-01-01"
```

### Content Negotiation Headers

```yaml
parameters:
  - name: Accept
    in: header
    description: Preferred response format
    schema:
      type: string
      enum:
        - application/json
        - application/xml
        - text/csv
      default: application/json

  - name: Accept-Language
    in: header
    description: Preferred language for response
    schema:
      type: string
      example: "en-US"
```

### Header Naming Convention

**Standard headers**: Use standard case (e.g., `Authorization`, `Content-Type`)

**Custom headers**: Prefix with `X-` and use kebab-case:
- `X-Request-ID`
- `X-API-Version`
- `X-Idempotency-Key`

## Cookie Parameters

Cookie parameters are less common in REST APIs but useful for session management.

```yaml
parameters:
  - name: session_id
    in: cookie
    description: Session identifier
    schema:
      type: string

  - name: preferences
    in: cookie
    description: User preferences
    schema:
      type: string
```

**Prefer header or query parameters** for API authentication. Cookies are more common in browser-based applications.

## Reusable Parameters

Define common parameters in components:

```yaml
components:
  parameters:
    Limit:
      name: limit
      in: query
      description: Maximum number of items to return
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

    Offset:
      name: offset
      in: query
      description: Number of items to skip
      schema:
        type: integer
        minimum: 0
        default: 0

    UserId:
      name: user_id
      in: path
      required: true
      description: User identifier
      schema:
        type: integer

    SortBy:
      name: sort_by
      in: query
      description: Field to sort results by
      schema:
        type: string
        enum: [created_at, updated_at, name]
        default: created_at

# Use in operations
paths:
  /users:
    get:
      parameters:
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/Offset'
        - $ref: '#/components/parameters/SortBy'

  /users/{user_id}:
    get:
      parameters:
        - $ref: '#/components/parameters/UserId'
```

## Path-Level Parameters

Define parameters at the path level to share across operations:

```yaml
paths:
  /users/{id}:
    parameters:
      # Shared across all operations on this path
      - name: id
        in: path
        required: true
        description: User ID
        schema:
          type: integer

    get:
      operationId: users_get
      # Inherits 'id' parameter

    put:
      operationId: users_update
      # Inherits 'id' parameter
      parameters:
        # Operation-specific parameter
        - name: X-Idempotency-Key
          in: header
          required: true
          schema:
            type: string

    delete:
      operationId: users_delete
      # Inherits 'id' parameter
```

## Validation

Apply validation constraints:

```yaml
parameters:
  - name: age
    in: query
    description: Minimum age filter
    schema:
      type: integer
      minimum: 0
      maximum: 150

  - name: username
    in: query
    description: Username to search
    schema:
      type: string
      minLength: 3
      maxLength: 32
      pattern: '^[a-zA-Z0-9_]+$'

  - name: email
    in: query
    description: Email address
    schema:
      type: string
      format: email
      maxLength: 255

  - name: page_size
    in: query
    description: Items per page
    schema:
      type: integer
      minimum: 1
      maximum: 100
      multipleOf: 10
      default: 20
```

## Deprecated Parameters

Mark parameters as deprecated when they should no longer be used:

```yaml
parameters:
  - name: page
    in: query
    deprecated: true
    description: |
      **DEPRECATED**: Use `offset` instead.

      Page number for pagination. This parameter is deprecated and will be
      removed in version 3.0. Use `offset` parameter for pagination.
    schema:
      type: integer
      default: 1

  - name: offset
    in: query
    description: Number of items to skip (replaces deprecated `page` parameter)
    schema:
      type: integer
      minimum: 0
      default: 0
```

## Common Patterns

### Search Parameters

```yaml
paths:
  /users/search:
    get:
      operationId: users_search
      parameters:
        - name: q
          in: query
          description: Search query (searches name, email, username)
          schema:
            type: string
            minLength: 2

        - name: fields
          in: query
          description: Fields to search in
          schema:
            type: array
            items:
              type: string
              enum: [name, email, username]
            default: [name, email, username]

        - name: fuzzy
          in: query
          description: Enable fuzzy matching
          schema:
            type: boolean
            default: false
```

### Date Range Parameters

```yaml
parameters:
  - name: start_date
    in: query
    description: Start of date range (inclusive)
    schema:
      type: string
      format: date
      example: "2024-01-01"

  - name: end_date
    in: query
    description: End of date range (inclusive)
    schema:
      type: string
      format: date
      example: "2024-12-31"
```

### Field Selection (Sparse Fieldsets)

```yaml
parameters:
  - name: fields
    in: query
    description: |
      Comma-separated list of fields to include in response.
      If not specified, all fields are returned.
    schema:
      type: array
      items:
        type: string
    style: form
    explode: false
    example: "id,name,email"
    # Results in: ?fields=id,name,email
```

### Expansion Parameters

```yaml
parameters:
  - name: expand
    in: query
    description: |
      Comma-separated list of relationships to expand (include in response).
      For example, `expand=orders,profile` includes related orders and profile.
    schema:
      type: array
      items:
        type: string
        enum: [orders, profile, subscriptions, preferences]
    style: form
    explode: false
```

## Common Pitfalls

### Avoid

**Optional path parameters**:
```yaml
- name: id
  in: path
  required: false  # ❌ Path params must be required
```

**Inconsistent naming**:
```yaml
# ❌ Mixed conventions
- name: user_id     # snake_case
- name: sortBy      # camelCase
- name: page-limit  # kebab-case
```

**Missing validation**:
```yaml
- name: limit
  in: query
  schema:
    type: integer
  # ❌ No minimum/maximum, could receive negative or huge values
```

**Vague descriptions**:
```yaml
- name: id
  description: ID
  # ❌ Not helpful

# ✓ Better
- name: id
  description: Unique user identifier
```

**Required query parameters without defaults**:
```yaml
- name: format
  in: query
  required: true
  # ❌ Forces clients to specify, no default
```

**Not specifying array serialization**:
```yaml
- name: ids
  schema:
    type: array
    items: {type: integer}
  # ❌ Missing style and explode - behavior unclear
```

### Do

- Always set `required: true` for path parameters
- Use consistent naming (snake_case for query/path, standard case for headers)
- Apply appropriate validation (min, max, pattern, enum)
- Provide clear, specific descriptions
- Set sensible defaults for optional parameters
- Specify `style` and `explode` for array parameters
- Use reusable components for common parameters
- Document deprecated parameters with replacement info
- Keep query parameters optional when possible

## Summary Checklist

For each parameter:

- [ ] `name` is clear and follows naming conventions
- [ ] `in` location specified (path/query/header/cookie)
- [ ] `required` explicitly set (true for path, usually false for query)
- [ ] `description` explains what the parameter does
- [ ] `schema` with appropriate type and validation
- [ ] Defaults specified for optional parameters
- [ ] Array parameters have `style` and `explode` defined
- [ ] Enums used for restricted values
- [ ] Deprecated parameters marked with migration info
- [ ] Examples provided for complex parameters

## Advanced Patterns

### Complex Query Objects

OpenAPI 3.0 supports object parameters:

```yaml
parameters:
  - name: filter
    in: query
    description: Complex filter criteria
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [active, inactive]
            created_after:
              type: string
              format: date
            tags:
              type: array
              items: {type: string}
    # Usage: ?filter={"status":"active","created_after":"2024-01-01"}
```

**Note**: Most clients don't handle JSON query params well. Prefer individual parameters or POST with request body for complex filtering.

### Matrix Parameters

For path parameters with multiple values:

```yaml
paths:
  /files/{file_id;version;format}:
    parameters:
      - name: file_id
        in: path
        required: true
        schema: {type: integer}
      - name: version
        in: path
        required: true
        schema: {type: integer}
      - name: format
        in: path
        required: true
        schema:
          type: string
          enum: [pdf, docx, txt]
    # Example: /files/123;version=2;format=pdf
```

**Note**: Matrix parameters are less common. Prefer standard path parameters or query parameters.
