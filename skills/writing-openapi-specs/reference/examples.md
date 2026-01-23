# Examples

Best practices for providing examples in OpenAPI specifications.

## Why Examples Matter

Good examples:
- Improve API documentation readability
- Help SDK generation produce better code samples
- Clarify expected data formats
- Demonstrate edge cases and variations
- Reduce integration time for API consumers

## Example vs Examples

OpenAPI supports two keywords:

| Keyword | Use Case | Support |
|---------|----------|---------|
| `example` | Single, inline example | OpenAPI 3.0, 3.1 |
| `examples` | Multiple named examples | OpenAPI 3.0, 3.1 (preferred) |

**Prefer `examples`** (plural) for better SDK generation and documentation:

```yaml
# ✓ Preferred: examples (plural)
schema:
  type: object
  properties:
    name: {type: string}
examples:
  basic:
    value:
      name: "John Doe"
  empty_name:
    value:
      name: ""

# ❌ Avoid: example (singular)
schema:
  type: object
  properties:
    name: {type: string}
example:
  name: "John Doe"
```

## Example Placement

Examples can appear at multiple levels:

### Schema-Level Examples

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id: {type: integer}
        name: {type: string}
      example:
        id: 123
        name: "John Doe"
```

### Property-Level Examples

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          example: 123
        email:
          type: string
          format: email
          example: "john@example.com"
        status:
          type: string
          enum: [active, inactive, pending]
          example: "active"
```

### Media Type Examples

```yaml
paths:
  /users:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
            examples:
              basic_user:
                summary: Basic user
                description: A standard user account
                value:
                  name: "John Doe"
                  email: "john@example.com"
              admin_user:
                summary: Admin user
                description: User with administrative privileges
                value:
                  name: "Admin User"
                  email: "admin@example.com"
                  role: "admin"
```

### Response Examples

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
        examples:
          success:
            summary: Successful response
            value:
              id: 123
              name: "John Doe"
              email: "john@example.com"
              created_at: "2024-01-01T00:00:00Z"
```

## Multiple Named Examples

Use the `examples` object for multiple variations:

```yaml
paths:
  /users:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              minimal:
                summary: Minimal user
                description: Only required fields
                value:
                  email: "user@example.com"
                  password: "securePassword123"

              complete:
                summary: Complete user
                description: All available fields
                value:
                  email: "user@example.com"
                  password: "securePassword123"
                  name: "John Doe"
                  phone: "+1-555-0123"
                  preferences:
                    newsletter: true
                    notifications: true

              with_profile:
                summary: User with profile
                description: User with extended profile information
                value:
                  email: "user@example.com"
                  password: "securePassword123"
                  name: "John Doe"
                  profile:
                    bio: "Software engineer"
                    location: "San Francisco, CA"
                    website: "https://example.com"
```

## External Examples

Reference examples from external files:

```yaml
examples:
  user_large:
    summary: Large user object
    externalValue: https://example.com/examples/user-large.json

  user_minimal:
    summary: Minimal user
    value:
      id: 1
      name: "John"
```

**Use `externalValue` when**:
- Example is very large (>100 lines)
- Example is reused across multiple specs
- Example is generated dynamically

## Example Best Practices

### Use Realistic Data

```yaml
# ✓ Good: Realistic data
examples:
  user:
    value:
      id: 12345
      email: "alice.johnson@example.com"
      name: "Alice Johnson"
      created_at: "2024-01-15T10:30:00Z"

# ❌ Avoid: Placeholder data
examples:
  user:
    value:
      id: 1
      email: "test@test.com"
      name: "Test User"
      created_at: "2020-01-01T00:00:00Z"
```

### Show Different Scenarios

```yaml
responses:
  '200':
    description: User list
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                $ref: '#/components/schemas/User'
            pagination:
              $ref: '#/components/schemas/PaginationInfo'
        examples:
          empty_list:
            summary: Empty result set
            value:
              data: []
              pagination:
                total: 0
                limit: 20
                offset: 0

          single_page:
            summary: Single page of results
            value:
              data:
                - {id: 1, name: "Alice"}
                - {id: 2, name: "Bob"}
              pagination:
                total: 2
                limit: 20
                offset: 0

          multiple_pages:
            summary: First page of many
            value:
              data:
                - {id: 1, name: "Alice"}
                - {id: 2, name: "Bob"}
              pagination:
                total: 150
                limit: 20
                offset: 0
                next_offset: 20
```

### Include Edge Cases

```yaml
examples:
  minimum_value:
    summary: Minimum allowed value
    value:
      amount: 0.01
      currency: "USD"

  maximum_value:
    summary: Maximum allowed value
    value:
      amount: 999999.99
      currency: "USD"

  zero_value:
    summary: Zero value transaction
    value:
      amount: 0.00
      currency: "USD"
      type: "refund"

  unicode_text:
    summary: Unicode characters
    value:
      name: "François Müller"
      bio: "こんにちは 👋"

  long_text:
    summary: Maximum length text
    value:
      description: "A".repeat(1000)  # Max 1000 chars
```

### Show Error Examples

```yaml
responses:
  '400':
    description: Validation error
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ValidationError'
        examples:
          invalid_email:
            summary: Invalid email format
            value:
              error: "Validation failed"
              code: "VALIDATION_ERROR"
              details:
                - field: "email"
                  message: "Invalid email format"

          missing_required:
            summary: Missing required fields
            value:
              error: "Validation failed"
              code: "VALIDATION_ERROR"
              details:
                - field: "email"
                  message: "Email is required"
                - field: "password"
                  message: "Password is required"

          password_too_short:
            summary: Password requirements not met
            value:
              error: "Validation failed"
              code: "VALIDATION_ERROR"
              details:
                - field: "password"
                  message: "Password must be at least 8 characters"

  '404':
    description: Resource not found
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        examples:
          user_not_found:
            summary: User not found
            value:
              error: "User not found"
              code: "NOT_FOUND"
              resource_id: "12345"

  '409':
    description: Conflict
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        examples:
          duplicate_email:
            summary: Email already in use
            value:
              error: "Email already in use"
              code: "CONFLICT"
              field: "email"
```

## Parameter Examples

### Query Parameter Examples

```yaml
parameters:
  - name: filter
    in: query
    description: Filter expression
    schema:
      type: string
    examples:
      by_status:
        summary: Filter by status
        value: "status:active"

      by_date_range:
        summary: Filter by date range
        value: "created_at:>=2024-01-01 AND created_at:<=2024-12-31"

      complex_filter:
        summary: Complex filter
        value: "status:active AND role:admin AND created_at:>2024-01-01"

  - name: sort
    in: query
    description: Sort order
    schema:
      type: string
    example: "name:asc,created_at:desc"
```

### Path Parameter Examples

```yaml
parameters:
  - name: id
    in: path
    required: true
    schema:
      type: string
      format: uuid
    example: "a7b8c9d0-e1f2-4567-8901-234567890abc"
```

## Reusable Examples

Store common examples in components:

```yaml
components:
  examples:
    BasicUser:
      summary: Basic user
      value:
        id: 1
        email: "john@example.com"
        name: "John Doe"

    AdminUser:
      summary: Admin user
      value:
        id: 2
        email: "admin@example.com"
        name: "Admin User"
        role: "admin"
        permissions: ["read", "write", "delete"]

    ValidationError:
      summary: Validation error
      value:
        error: "Validation failed"
        code: "VALIDATION_ERROR"
        details:
          - field: "email"
            message: "Invalid email format"

# Use in operations
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              examples:
                basic:
                  $ref: '#/components/examples/BasicUser'
                admin:
                  $ref: '#/components/examples/AdminUser'
```

## Example Structure

### Complete Example Object

```yaml
examples:
  example_name:
    summary: Short description (shown in docs)
    description: Longer explanation (optional)
    value:
      # Inline example value
    # OR
    externalValue: https://example.com/example.json
```

### Summary vs Description

```yaml
examples:
  complete_user:
    summary: Complete user profile
    description: |
      This example shows a user profile with all optional
      fields populated, including profile information,
      preferences, and notification settings.
    value:
      id: 123
      email: "user@example.com"
      # ... more fields
```

## Examples for Different Content Types

### JSON Examples

```yaml
content:
  application/json:
    schema:
      $ref: '#/components/schemas/User'
    examples:
      user:
        value:
          id: 123
          name: "John Doe"
```

### XML Examples

```yaml
content:
  application/xml:
    schema:
      $ref: '#/components/schemas/User'
    examples:
      user:
        value: |
          <?xml version="1.0" encoding="UTF-8"?>
          <user>
            <id>123</id>
            <name>John Doe</name>
          </user>
```

### CSV Examples

```yaml
content:
  text/csv:
    schema:
      type: string
    examples:
      user_export:
        summary: User export
        value: |
          id,name,email,created_at
          1,Alice,alice@example.com,2024-01-01
          2,Bob,bob@example.com,2024-01-02
```

### Plain Text Examples

```yaml
content:
  text/plain:
    schema:
      type: string
    examples:
      simple:
        value: "This is plain text content"
```

## Examples for Complex Types

### Array Examples

```yaml
schema:
  type: array
  items:
    type: string
examples:
  tags:
    summary: Tag list
    value: ["api", "documentation", "sdk"]

  empty:
    summary: Empty array
    value: []
```

### Nested Object Examples

```yaml
schema:
  type: object
  properties:
    user:
      type: object
      properties:
        name: {type: string}
        address:
          type: object
          properties:
            street: {type: string}
            city: {type: string}
examples:
  complete:
    value:
      user:
        name: "John Doe"
        address:
          street: "123 Main St"
          city: "San Francisco"
          state: "CA"
          zip: "94102"
```

### Polymorphic Examples

```yaml
schema:
  oneOf:
    - $ref: '#/components/schemas/CreditCard'
    - $ref: '#/components/schemas/BankAccount'
examples:
  credit_card:
    summary: Credit card payment
    value:
      type: "credit_card"
      card_number: "4111111111111111"
      expiry: "12/25"
      cvv: "123"

  bank_account:
    summary: Bank account payment
    value:
      type: "bank_account"
      account_number: "1234567890"
      routing_number: "021000021"
```

## Common Pitfalls

### Avoid

**Inconsistent example data**:
```yaml
# ❌ Examples contradict schema
schema:
  type: object
  required: [id, name]
  properties:
    id: {type: integer}
    name: {type: string}
example:
  name: "John"
  # Missing required 'id' field
```

**Unrealistic placeholder data**:
```yaml
# ❌ Not helpful
example:
  id: 1
  name: "string"
  email: "user@example.com"
```

**Examples without context**:
```yaml
# ❌ No summary or description
examples:
  example1:
    value: {...}
  example2:
    value: {...}

# ✓ Clear labels
examples:
  minimal_request:
    summary: Minimal required fields
    value: {...}
  complete_request:
    summary: All fields populated
    value: {...}
```

**Missing examples for complex operations**:
```yaml
# ❌ Complex search endpoint with no examples
/search:
  post:
    requestBody:
      content:
        application/json:
          schema:
            # Complex nested filter schema
            # No examples provided
```

### Do

- Use realistic, production-like data
- Provide multiple examples showing variations
- Include edge cases (empty, minimum, maximum)
- Show error response examples
- Use clear summaries for each example
- Keep examples consistent with schema constraints
- Include examples for complex operations
- Reference reusable examples from components
- Use `examples` (plural) over `example` (singular)

## Summary Checklist

For examples:

- [ ] Use `examples` (plural) instead of `example` (singular)
- [ ] Provide multiple examples for complex types
- [ ] Use realistic data (not "test" or "foo")
- [ ] Include summaries for each named example
- [ ] Show different scenarios (minimal, complete, edge cases)
- [ ] Include error response examples
- [ ] Examples match schema constraints
- [ ] Complex operations have clear examples
- [ ] Parameter examples provided where helpful
- [ ] Reusable examples defined in components
- [ ] External examples used for large payloads
- [ ] Examples show polymorphic variations

## Advanced Patterns

### Dynamic Examples

For generated documentation, reference example generators:

```yaml
examples:
  random_user:
    summary: Randomly generated user
    externalValue: https://api.example.com/examples/generate/user
```

### Versioned Examples

Show examples for different API versions:

```yaml
examples:
  v1_format:
    summary: API v1 response format
    description: Legacy format for backward compatibility
    value:
      user_id: 123
      user_name: "John"

  v2_format:
    summary: API v2 response format
    description: Current format with ISO timestamps
    value:
      id: 123
      name: "John Doe"
      created_at: "2024-01-01T00:00:00Z"
```

### Localized Examples

```yaml
examples:
  english:
    summary: English content
    value:
      title: "Welcome"
      message: "Hello, World!"

  spanish:
    summary: Spanish content
    value:
      title: "Bienvenido"
      message: "¡Hola, Mundo!"

  japanese:
    summary: Japanese content
    value:
      title: "ようこそ"
      message: "こんにちは、世界！"
```
