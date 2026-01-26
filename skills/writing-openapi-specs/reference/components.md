# Components

Best practices for organizing reusable components in OpenAPI specifications.

## Overview

The `components` section stores reusable definitions that can be referenced throughout your spec:

```yaml
components:
  schemas:        # Data models
  parameters:     # Reusable parameters
  responses:      # Reusable responses
  requestBodies:  # Reusable request bodies
  examples:       # Reusable examples
  headers:        # Reusable headers
  securitySchemes:  # Authentication schemes
  links:          # Reusable links
  callbacks:      # Reusable callbacks
```

## When to Create Components

### Create components for:

- **Schemas** used in multiple operations
- **Domain models** (User, Order, Product)
- **Common parameters** (pagination, filtering, sorting)
- **Standard responses** (errors, validation failures)
- **Repeated examples**
- **Security schemes**

### Keep inline for:

- **Operation-specific** request/response shapes
- **Simple, one-off** structures
- **Parameters unique** to one operation
- **Trivial schemas** unlikely to be reused

## Schemas

### Basic Schema Components

```yaml
components:
  schemas:
    User:
      type: object
      required: [id, email, name]
      properties:
        id:
          type: integer
          readOnly: true
        email:
          type: string
          format: email
        name:
          type: string
        created_at:
          type: string
          format: date-time
          readOnly: true

    Error:
      type: object
      required: [error, code]
      properties:
        error:
          type: string
          description: Human-readable error message
        code:
          type: string
          description: Machine-readable error code
        details:
          type: object
          description: Additional error context

    PaginationInfo:
      type: object
      required: [total, limit, offset]
      properties:
        total:
          type: integer
          description: Total number of items
        limit:
          type: integer
          description: Items per page
        offset:
          type: integer
          description: Items skipped
        next_offset:
          type: integer
          nullable: true
          description: Offset for next page, null if last page
```

### Naming Conventions

Use **PascalCase** for component names:

```yaml
components:
  schemas:
    User:              # ✓ PascalCase
    UserProfile:       # ✓ PascalCase
    OrderHistory:      # ✓ PascalCase
    PaymentMethod:     # ✓ PascalCase

    # Avoid
    user:              # ❌ lowercase
    user_profile:      # ❌ snake_case
    order-history:     # ❌ kebab-case
```

### Organizing Large Schema Collections

Group related schemas with prefixes:

```yaml
components:
  schemas:
    # User-related
    User:
    UserProfile:
    UserPreferences:
    UserCreateRequest:
    UserUpdateRequest:

    # Order-related
    Order:
    OrderItem:
    OrderHistory:
    OrderCreateRequest:

    # Common/Shared
    Error:
    ValidationError:
    PaginationInfo:
    Timestamp:
```

### Request/Response Schemas

Create specific schemas for requests and responses:

```yaml
components:
  schemas:
    # Domain model (complete representation)
    User:
      type: object
      required: [id, email, name, created_at]
      properties:
        id: {type: integer, readOnly: true}
        email: {type: string, format: email}
        name: {type: string}
        password_hash: {type: string, readOnly: true}
        created_at: {type: string, format: date-time, readOnly: true}
        updated_at: {type: string, format: date-time, readOnly: true}

    # Create request (no auto-generated fields)
    UserCreateRequest:
      type: object
      required: [email, name, password]
      properties:
        email: {type: string, format: email}
        name: {type: string}
        password: {type: string, format: password, minLength: 8}

    # Update request (all fields optional)
    UserUpdateRequest:
      type: object
      properties:
        email: {type: string, format: email}
        name: {type: string}
        password: {type: string, format: password, minLength: 8}

    # Public response (no sensitive fields)
    UserResponse:
      type: object
      required: [id, email, name, created_at]
      properties:
        id: {type: integer}
        email: {type: string, format: email}
        name: {type: string}
        created_at: {type: string, format: date-time}
```

**Alternative approach**: Use single schema with `readOnly`/`writeOnly`:

```yaml
User:
  type: object
  required: [email, name]
  properties:
    id:
      type: integer
      readOnly: true
    email:
      type: string
      format: email
    name:
      type: string
    password:
      type: string
      format: password
      writeOnly: true
    password_hash:
      type: string
      readOnly: true
```

## Parameters

### Reusable Parameters

```yaml
components:
  parameters:
    # Pagination
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

    # Filtering
    Status:
      name: status
      in: query
      description: Filter by status
      schema:
        type: string
        enum: [active, inactive, pending]

    # Sorting
    SortBy:
      name: sort_by
      in: query
      description: Field to sort by
      schema:
        type: string
        enum: [created_at, updated_at, name]
        default: created_at

    SortOrder:
      name: order
      in: query
      description: Sort order
      schema:
        type: string
        enum: [asc, desc]
        default: desc

    # Path parameters
    UserId:
      name: user_id
      in: path
      required: true
      description: User identifier
      schema:
        type: integer

    OrderId:
      name: order_id
      in: path
      required: true
      description: Order identifier
      schema:
        type: string
        format: uuid

# Usage
paths:
  /users:
    get:
      parameters:
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/Offset'
        - $ref: '#/components/parameters/SortBy'
        - $ref: '#/components/parameters/SortOrder'

  /users/{user_id}:
    parameters:
      - $ref: '#/components/parameters/UserId'
    get:
      operationId: users_get
```

## Responses

### Reusable Responses

```yaml
components:
  responses:
    # Success responses
    Success:
      description: Operation successful
      content:
        application/json:
          schema:
            type: object
            properties:
              message: {type: string}
              success: {type: boolean, enum: [true]}

    # Client errors
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Invalid request parameters"
            code: "BAD_REQUEST"

    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Missing or invalid authentication"
            code: "UNAUTHORIZED"

    Forbidden:
      description: Insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "You don't have permission to access this resource"
            code: "FORBIDDEN"

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Resource not found"
            code: "NOT_FOUND"

    ValidationError:
      description: Validation failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidationError'

    RateLimitExceeded:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema: {type: integer}
          description: Seconds to wait before retrying
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    # Server errors
    InternalServerError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "An unexpected error occurred"
            code: "INTERNAL_ERROR"

# Usage
paths:
  /users/{id}:
    get:
      responses:
        '200':
          description: User retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '500':
          $ref: '#/components/responses/InternalServerError'
```

## Request Bodies

### Reusable Request Bodies

```yaml
components:
  requestBodies:
    UserCreate:
      required: true
      description: User creation payload
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserCreateRequest'
          examples:
            basic:
              summary: Basic user
              value:
                email: "user@example.com"
                name: "John Doe"
                password: "securePassword123"

    UserUpdate:
      required: true
      description: User update payload
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserUpdateRequest'
          examples:
            name_only:
              summary: Update name only
              value:
                name: "Jane Doe"

    FileUpload:
      required: true
      description: File upload
      content:
        multipart/form-data:
          schema:
            type: object
            required: [file]
            properties:
              file:
                type: string
                format: binary
              description:
                type: string

# Usage
paths:
  /users:
    post:
      requestBody:
        $ref: '#/components/requestBodies/UserCreate'

  /users/{id}:
    patch:
      requestBody:
        $ref: '#/components/requestBodies/UserUpdate'
```

## Examples

### Reusable Examples

```yaml
components:
  examples:
    BasicUser:
      summary: Basic user example
      value:
        id: 1
        email: "john@example.com"
        name: "John Doe"
        created_at: "2024-01-01T00:00:00Z"

    AdminUser:
      summary: Admin user example
      value:
        id: 2
        email: "admin@example.com"
        name: "Admin User"
        role: "admin"
        permissions: ["read", "write", "delete"]
        created_at: "2024-01-01T00:00:00Z"

    ValidationErrorExample:
      summary: Validation error
      value:
        error: "Validation failed"
        code: "VALIDATION_ERROR"
        details:
          - field: "email"
            message: "Invalid email format"
          - field: "password"
            message: "Password must be at least 8 characters"

# Usage
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
              examples:
                basic_users:
                  $ref: '#/components/examples/BasicUser'
                admin_users:
                  $ref: '#/components/examples/AdminUser'
```

## Headers

### Reusable Headers

```yaml
components:
  headers:
    X-RateLimit-Limit:
      description: Total requests allowed per window
      schema:
        type: integer
      example: 1000

    X-RateLimit-Remaining:
      description: Requests remaining in current window
      schema:
        type: integer
      example: 950

    X-RateLimit-Reset:
      description: Unix timestamp when window resets
      schema:
        type: integer
      example: 1609459200

    ETag:
      description: Entity tag for caching
      schema:
        type: string
      example: '"abc123def456"'

    Location:
      description: URI of created resource
      schema:
        type: string
        format: uri
      example: "https://api.example.com/users/123"

# Usage
paths:
  /users:
    get:
      responses:
        '200':
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/X-RateLimit-Reset'
```

## Security Schemes

### Common Security Schemes

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key authentication

    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT bearer token authentication

    OAuth2:
      type: oauth2
      description: OAuth 2.0 authentication
      flows:
        authorizationCode:
          authorizationUrl: https://api.example.com/oauth/authorize
          tokenUrl: https://api.example.com/oauth/token
          scopes:
            read: Read access
            write: Write access
            admin: Administrative access

    BasicAuth:
      type: http
      scheme: basic
      description: HTTP Basic authentication

# Apply globally
security:
  - BearerAuth: []

# Or per-operation
paths:
  /admin:
    get:
      security:
        - OAuth2: [admin]
```

See [reference/security.md](reference/security.md) for detailed security guidance.

## Organization Strategies

### Flat Structure (Small Specs)

```yaml
components:
  schemas:
    User:
    Order:
    Product:
    Error:
  parameters:
    Limit:
    Offset:
  responses:
    NotFound:
    Unauthorized:
```

**Use when**: Spec has < 20 components total.

### Grouped Structure (Medium Specs)

```yaml
components:
  schemas:
    # Users
    User:
    UserProfile:
    UserPreferences:

    # Orders
    Order:
    OrderItem:
    OrderHistory:

    # Common
    Error:
    ValidationError:
    PaginationInfo:
```

**Use when**: Spec has 20-100 components.

### File Splitting (Large Specs)

For very large specs, split into multiple files:

```
openapi.yaml                  # Main file
components/
  schemas/
    User.yaml
    Order.yaml
    Product.yaml
  parameters/
    pagination.yaml
    filtering.yaml
  responses/
    errors.yaml
    success.yaml
```

Reference external files:

```yaml
# openapi.yaml
components:
  schemas:
    User:
      $ref: './components/schemas/User.yaml'
    Order:
      $ref: './components/schemas/Order.yaml'
  parameters:
    Limit:
      $ref: './components/parameters/pagination.yaml#/Limit'
```

**Use when**: Spec has 100+ components or multiple teams collaborate.

## Reusability Best Practices

### Do

**Balance reusability with clarity**:
```yaml
# Good - Common error response
components:
  responses:
    NotFound:
      # Reused across many endpoints

# Also good - Operation-specific response
paths:
  /special-endpoint:
    get:
      responses:
        '200':
          # Inline - only used here
          description: Special response
          content:
            application/json:
              schema:
                type: object
                properties:
                  unique_field: {type: string}
```

**Use descriptive names**:
```yaml
# Good
UserCreateRequest:
UserResponse:
PaginationInfo:

# Avoid
Request1:
Response2:
Data:
```

**Group related components**:
```yaml
# Good - Clear grouping
User:
UserProfile:
UserPreferences:
UserCreateRequest:
UserUpdateRequest:

# Avoid - No clear relationship
User:
CreateUser:
UserData:
UpdateUserDTO:
```

### Avoid

**Over-abstracting**:
```yaml
# ❌ Too abstract
GenericResource:
  type: object
  properties:
    id: {type: integer}
    data: {type: object}

# ✓ Specific schemas
User:
  type: object
  properties:
    id: {type: integer}
    email: {type: string}
    name: {type: string}
```

**Creating components for one-off use**:
```yaml
# ❌ Unnecessary component
components:
  schemas:
    SpecialEndpointResponse:
      # Only used once

# ✓ Keep inline if used once
paths:
  /special:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  # Define inline
```

**Deeply nested references**:
```yaml
# ❌ Hard to follow
$ref: '#/components/schemas/Wrapper'
  $ref: '#/components/schemas/Container'
    $ref: '#/components/schemas/ActualData'

# ✓ Flatten structure
$ref: '#/components/schemas/ActualData'
```

## Summary Checklist

When organizing components:

- [ ] Use PascalCase for component names
- [ ] Create components for multi-use definitions
- [ ] Keep one-off schemas inline
- [ ] Group related components with naming prefixes
- [ ] Balance reusability with clarity
- [ ] Provide clear, descriptive names
- [ ] Document complex components
- [ ] Consider file splitting for large specs
- [ ] Avoid over-abstraction
- [ ] Avoid deeply nested references
- [ ] Use specific request/response schemas or readOnly/writeOnly
- [ ] Include examples for complex schemas

## Advanced Patterns

### Schema Composition in Components

```yaml
components:
  schemas:
    # Base schema
    Resource:
      type: object
      required: [id, created_at, updated_at]
      properties:
        id:
          type: integer
          readOnly: true
        created_at:
          type: string
          format: date-time
          readOnly: true
        updated_at:
          type: string
          format: date-time
          readOnly: true

    # Extend base
    User:
      allOf:
        - $ref: '#/components/schemas/Resource'
        - type: object
          required: [email, name]
          properties:
            email: {type: string, format: email}
            name: {type: string}

    Order:
      allOf:
        - $ref: '#/components/schemas/Resource'
        - type: object
          required: [user_id, total]
          properties:
            user_id: {type: integer}
            total: {type: number}
```

### Parameterized Components

Use examples to show variations:

```yaml
components:
  schemas:
    PagedResponse:
      type: object
      required: [data, pagination]
      properties:
        data:
          type: array
          items: {}  # Type varies by usage
        pagination:
          $ref: '#/components/schemas/PaginationInfo'

# Usage with different data types
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                required: [data, pagination]
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/PaginationInfo'
```
