# OpenAPI Validation Guide

Validate and fix OpenAPI specifications for SDK generation.

## Validation Commands

```bash
# Basic validation
speakeasy validate openapi -s spec.yaml

# Detailed linting with rules
speakeasy lint openapi -s spec.yaml
```

## Inspecting Large Specs

Never load full specs into context. Use `yq`/`jq` to extract sections:

```bash
# List all paths
yq '.paths | keys' spec.yaml

# Inspect specific endpoint
yq '.paths["/users/{id}"]' spec.yaml

# List all schemas
yq '.components.schemas | keys' spec.yaml

# Find operations without operationId
yq '[.paths[][] | select(.operationId == null)]' spec.yaml

# For JSON specs
jq '.paths | keys' spec.json
```

## Common Issues and Fixes

### Missing Operation IDs

**Error:** `operation missing operationId`

```yaml
# Bad
paths:
  /users:
    get:
      summary: List users

# Good
paths:
  /users:
    get:
      operationId: listUsers
      summary: List users
```

### Poor Operation IDs

**Warning:** `operationId 'get_users_users__user_id__get' is not descriptive`

```yaml
# Bad - auto-generated
operationId: get_users_users__user_id__get

# Good - clear and concise
operationId: getUser
```

Use `speakeasy suggest operation-ids -s spec.yaml` for AI-powered suggestions.

### Missing Response Schemas

**Warning:** `response missing schema definition`

```yaml
# Bad
responses:
  '200':
    description: Success

# Good
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
```

### Missing Error Responses

Always document error responses:

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
  '400':
    description: Bad request
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
  '401':
    description: Unauthorized
  '404':
    description: Not found
  '500':
    description: Internal server error
```

### Missing Descriptions

**Hint:** `operation missing description`

```yaml
# Bad
paths:
  /users:
    get:
      operationId: listUsers

# Good
paths:
  /users:
    get:
      operationId: listUsers
      summary: List users
      description: Returns a paginated list of all users. Supports filtering by status.
```

### Missing Examples

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

Choose one convention and use consistently:

```yaml
# Consistent - camelCase
parameters:
  - name: userId
  - name: projectId
  - name: pageSize

# Or consistent - snake_case
parameters:
  - name: user_id
  - name: project_id
  - name: page_size
```

### Missing Request Body

```yaml
# Bad
paths:
  /users:
    post:
      operationId: createUser

# Good
paths:
  /users:
    post:
      operationId: createUser
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
```

### Required vs Optional Properties

```yaml
components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
      properties:
        id:
          type: string
        email:
          type: string
        name:
          type: string  # Optional - not in required
```

## Schema Best Practices

### Use Refs for Reusability

```yaml
# Bad - inline schema
responses:
  '200':
    content:
      application/json:
        schema:
          type: object
          properties:
            id:
              type: string
            name:
              type: string

# Good - use ref
responses:
  '200':
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
```

### Nullable Fields

```yaml
properties:
  middle_name:
    type: string
    nullable: true
```

### Enums with Descriptions

```yaml
properties:
  status:
    type: string
    enum: [pending, active, suspended, deleted]
    description: |
      User account status:
      - pending: Awaiting email verification
      - active: Normal account state
      - suspended: Temporarily disabled
      - deleted: Soft-deleted, can be restored
```

### Format Specifiers

```yaml
properties:
  id:
    type: string
    format: uuid
  created_at:
    type: string
    format: date-time
  email:
    type: string
    format: email
  website:
    type: string
    format: uri
  price:
    type: number
    format: double
  count:
    type: integer
    format: int64
```

## Fixing Issues via Overlay

When you can't modify the source spec, use overlays:

```yaml
overlay: 1.0.0
info:
  title: Validation Fixes
  version: 1.0.0
actions:
  # Add missing operationId
  - target: "$.paths['/users'].get"
    update:
      operationId: listUsers

  # Add missing description
  - target: "$.paths['/users'].get"
    update:
      description: Returns a paginated list of users

  # Add missing response schema
  - target: "$.paths['/users'].get.responses['200']"
    update:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserList'
```

## Validation Workflow

```bash
# 1. Validate spec
speakeasy lint openapi -s spec.yaml 2>&1 | head -50

# 2. Create overlay for fixes
# (create fixes.yaml targeting each issue)

# 3. Add overlay to workflow.yaml
# sources:
#   my-api:
#     inputs:
#       - location: ./spec.yaml
#     overlays:
#       - location: ./fixes.yaml

# 4. Regenerate SDK
speakeasy run --output console
```
