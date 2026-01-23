# Schemas

Best practices for defining data models in OpenAPI specifications.

## Quick Patterns

### Basic Types

OpenAPI schemas support standard JSON types:

```yaml
# String
type: string

# Number (integer)
type: integer

# Number (float/double)
type: number

# Boolean
type: boolean

# Array
type: array
items:
  type: string

# Object
type: object
properties:
  id: {type: integer}
  name: {type: string}
```

### String Formats

Use `format` for semantic validation and better SDK generation:

```yaml
# Date (YYYY-MM-DD)
type: string
format: date

# DateTime (ISO 8601)
type: string
format: date-time

# Email
type: string
format: email

# URI
type: string
format: uri

# UUID
type: string
format: uuid

# Binary data (base64)
type: string
format: byte

# Password (masked in docs)
type: string
format: password
```

## Enums

Enums restrict values to a predefined set. Use string enums with clear, semantic values.

### Good Enum Patterns

```yaml
# Status enum
type: string
enum:
  - pending
  - approved
  - rejected
  - cancelled
description: Current status of the request

# Priority enum
type: string
enum:
  - low
  - medium
  - high
  - urgent

# HTTP method enum
type: string
enum:
  - GET
  - POST
  - PUT
  - PATCH
  - DELETE
```

### Enum Best Practices

**Do**:
- Use lowercase with underscores for multi-word values: `in_progress`, `pending_approval`
- Use semantic, self-documenting values
- Keep values stable (don't rename existing values)
- Document what each value means if not obvious

**Avoid**:
- Numeric strings: `enum: ["0", "1", "2"]` (unclear meaning)
- Generic values: `enum: ["value1", "value2"]` (not semantic)
- Unclear abbreviations: `enum: ["pnd", "appr", "rjt"]` (hard to understand)
- SCREAMING_SNAKE_CASE unless matching an external standard

### Enum with Descriptions

For complex enums, document each value:

```yaml
type: string
enum:
  - trial
  - basic
  - premium
  - enterprise
description: |
  Subscription tier:
  - `trial`: 14-day trial with limited features
  - `basic`: $10/month, up to 10 users
  - `premium`: $50/month, up to 50 users
  - `enterprise`: Custom pricing, unlimited users
```

### Extensible Enums

For enums that might grow, document this clearly:

```yaml
type: string
enum:
  - email
  - sms
  - push
  - webhook
description: |
  Notification delivery method. Additional methods may be added in future API versions.
  Clients should handle unknown values gracefully.
```

## Nullable Types

Handling null values depends on your OpenAPI version.

### OpenAPI 3.1 (Recommended)

OpenAPI 3.1 uses JSON Schema 2020-12, which supports type arrays:

```yaml
# Nullable string
type: [string, "null"]

# or using nullable keyword (still supported)
type: string
nullable: true
```

### OpenAPI 3.0

Use the `nullable` keyword:

```yaml
type: string
nullable: true
```

### Required vs Optional vs Nullable

These are distinct concepts:

```yaml
type: object
properties:
  # Required, non-null
  id:
    type: integer

  # Required, nullable
  middle_name:
    type: [string, "null"]

  # Optional, non-null (can be omitted)
  nickname:
    type: string

  # Optional, nullable (can be omitted OR null)
  suffix:
    type: [string, "null"]

required: [id, middle_name]
```

**In practice**:
- **Required + non-null**: Must be present, cannot be null
- **Required + nullable**: Must be present, can be null
- **Optional + non-null**: Can be omitted, but if present cannot be null
- **Optional + nullable**: Can be omitted, and if present can be null

## Polymorphism

Polymorphism allows a field to be one of several types or a combination of types.

### oneOf (Exactly One Type)

Use `oneOf` when a value must match exactly one schema. Common for type discrimination.

```yaml
PaymentMethod:
  oneOf:
    - $ref: '#/components/schemas/CreditCard'
    - $ref: '#/components/schemas/BankAccount'
    - $ref: '#/components/schemas/PayPal'
  discriminator:
    propertyName: type
    mapping:
      credit_card: '#/components/schemas/CreditCard'
      bank_account: '#/components/schemas/BankAccount'
      paypal: '#/components/schemas/PayPal'

CreditCard:
  type: object
  required: [type, card_number, expiry, cvv]
  properties:
    type:
      type: string
      enum: [credit_card]
    card_number:
      type: string
    expiry:
      type: string
    cvv:
      type: string

BankAccount:
  type: object
  required: [type, account_number, routing_number]
  properties:
    type:
      type: string
      enum: [bank_account]
    account_number:
      type: string
    routing_number:
      type: string

PayPal:
  type: object
  required: [type, email]
  properties:
    type:
      type: string
      enum: [paypal]
    email:
      type: string
      format: email
```

**When to use**: Type discrimination, mutually exclusive options.

### allOf (Composition/Inheritance)

Use `allOf` to combine schemas, typically for inheritance patterns.

```yaml
# Base schema
User:
  type: object
  required: [id, email]
  properties:
    id:
      type: integer
    email:
      type: string
      format: email
    name:
      type: string

# Extended schema (inherits from User)
AdminUser:
  allOf:
    - $ref: '#/components/schemas/User'
    - type: object
      required: [permissions]
      properties:
        permissions:
          type: array
          items:
            type: string
        admin_level:
          type: integer
          minimum: 1
          maximum: 5
```

**Result**: AdminUser has all properties from User plus `permissions` and `admin_level`.

**When to use**: Inheritance, extending base models, composition of concerns.

### anyOf (One or More Types)

Use `anyOf` when a value can match one or more schemas. Less common but useful for flexible unions.

```yaml
SearchFilter:
  anyOf:
    - $ref: '#/components/schemas/TextFilter'
    - $ref: '#/components/schemas/DateFilter'
    - $ref: '#/components/schemas/NumericFilter'
  description: |
    Search filter. Can match text, dates, numeric ranges, or combinations thereof.

TextFilter:
  type: object
  properties:
    text_query:
      type: string

DateFilter:
  type: object
  properties:
    start_date:
      type: string
      format: date
    end_date:
      type: string
      format: date

NumericFilter:
  type: object
  properties:
    min_value:
      type: number
    max_value:
      type: number
```

**When to use**: Flexible filters, overlapping properties, "one or more" validation.

### Comparison Table

| Keyword | Validation | Use Case |
|---------|------------|----------|
| `oneOf` | Matches exactly one schema | Type discrimination, mutually exclusive types |
| `allOf` | Matches all schemas | Inheritance, composition, extending base types |
| `anyOf` | Matches one or more schemas | Flexible unions, overlapping properties |

## Discriminators

Discriminators provide a hint about which schema applies in a `oneOf` scenario. This improves performance and enables better SDK generation.

### Basic Discriminator

```yaml
Pet:
  oneOf:
    - $ref: '#/components/schemas/Dog'
    - $ref: '#/components/schemas/Cat'
    - $ref: '#/components/schemas/Bird'
  discriminator:
    propertyName: petType

Dog:
  type: object
  required: [petType, bark]
  properties:
    petType:
      type: string
      enum: [Dog]
    bark:
      type: string
      description: Sound the dog makes

Cat:
  type: object
  required: [petType, meow]
  properties:
    petType:
      type: string
      enum: [Cat]
    meow:
      type: string

Bird:
  type: object
  required: [petType, chirp]
  properties:
    petType:
      type: string
      enum: [Bird]
    chirp:
      type: string
```

### Discriminator with Mapping

Use explicit mapping when discriminator values don't match schema names:

```yaml
PaymentMethod:
  oneOf:
    - $ref: '#/components/schemas/CreditCard'
    - $ref: '#/components/schemas/BankAccount'
    - $ref: '#/components/schemas/PayPalAccount'
  discriminator:
    propertyName: type
    mapping:
      credit_card: '#/components/schemas/CreditCard'
      bank_account: '#/components/schemas/BankAccount'
      paypal: '#/components/schemas/PayPalAccount'
```

**The discriminator property must**:
- Exist in all schemas within the `oneOf`
- Be required in all schemas
- Have a unique value (typically enum) in each schema

### Why Use Discriminators?

1. **Performance**: Parsers can quickly identify which schema to validate against
2. **SDK Generation**: Generates type-safe unions with proper type guards
3. **Documentation**: Makes polymorphic types clearer to API consumers
4. **Error Messages**: Better validation errors when type doesn't match

### Discriminator Best Practices

**Do**:
- Always use with `oneOf` (not `anyOf` or `allOf`)
- Make discriminator property required in all schemas
- Use enum values for discriminator property
- Provide explicit mapping when values differ from schema names

**Avoid**:
- Optional discriminator properties
- Discriminators without enums (hard to validate)
- Implicit mapping when schema names are unclear

## Validation Keywords

OpenAPI supports JSON Schema validation keywords:

```yaml
type: object
properties:
  username:
    type: string
    minLength: 3
    maxLength: 32
    pattern: '^[a-zA-Z0-9_]+$'

  age:
    type: integer
    minimum: 0
    maximum: 150

  email:
    type: string
    format: email

  tags:
    type: array
    items:
      type: string
    minItems: 1
    maxItems: 10
    uniqueItems: true

  score:
    type: number
    multipleOf: 0.5
    minimum: 0
    maximum: 100
```

### Common Validation Keywords

| Type | Keywords | Example |
|------|----------|---------|
| String | `minLength`, `maxLength`, `pattern` | `minLength: 8` |
| Number | `minimum`, `maximum`, `multipleOf` | `minimum: 0` |
| Array | `minItems`, `maxItems`, `uniqueItems` | `maxItems: 100` |
| Object | `minProperties`, `maxProperties` | `minProperties: 1` |

## Naming Conventions

### Component Schema Names

Use **PascalCase** for component schemas:

```yaml
components:
  schemas:
    User:           # PascalCase
    OrderHistory:   # PascalCase
    PaymentMethod:  # PascalCase
```

### Property Names

Use **snake_case** for property names (common REST convention):

```yaml
properties:
  user_id: {type: integer}
  first_name: {type: string}
  created_at: {type: string, format: date-time}
```

**Alternative**: Use **camelCase** if that's your API convention, but be consistent:

```yaml
properties:
  userId: {type: integer}
  firstName: {type: string}
  createdAt: {type: string, format: date-time}
```

**Pick one convention and apply it consistently throughout your spec.**

## Reusability Patterns

### When to Create Reusable Schemas

**Create components for**:
- Models used in multiple operations
- Domain objects (User, Order, Product)
- Common error responses
- Pagination structures
- Nested objects used repeatedly

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id: {type: integer}
        name: {type: string}

    PaginatedResponse:
      type: object
      properties:
        data:
          type: array
          items: {}  # Defined by usage
        pagination:
          $ref: '#/components/schemas/PaginationInfo'

    PaginationInfo:
      type: object
      properties:
        total: {type: integer}
        limit: {type: integer}
        offset: {type: integer}
```

### When to Use Inline Schemas

**Keep inline for**:
- Operation-specific request shapes
- Simple query parameter objects
- Unique one-off structures
- Small objects unlikely to be reused

```yaml
paths:
  /users/search:
    post:
      requestBody:
        content:
          application/json:
            schema:
              # Inline - specific to this operation
              type: object
              properties:
                query: {type: string}
                filters:
                  type: object
                  properties:
                    active: {type: boolean}
                    role: {type: string}
```

## Advanced Patterns

### Read-Only and Write-Only Properties

Mark properties that are only returned or only accepted:

```yaml
User:
  type: object
  properties:
    id:
      type: integer
      readOnly: true    # Only in responses
    password:
      type: string
      writeOnly: true   # Only in requests
    email:
      type: string
    created_at:
      type: string
      format: date-time
      readOnly: true
```

**Result**:
- `readOnly` properties are omitted from request schemas
- `writeOnly` properties are omitted from response schemas

### Conditional Schemas (dependentSchemas)

OpenAPI 3.1 supports conditional validation:

```yaml
Order:
  type: object
  properties:
    shipping_method:
      type: string
      enum: [standard, express, pickup]
    shipping_address:
      $ref: '#/components/schemas/Address'
    pickup_location:
      type: string
  dependentSchemas:
    shipping_method:
      if:
        properties:
          shipping_method:
            const: pickup
      then:
        required: [pickup_location]
      else:
        required: [shipping_address]
```

**Use when**: Field requirements depend on other field values.

### Additional Properties

Control whether unknown properties are allowed:

```yaml
# Strict schema (no additional properties)
StrictUser:
  type: object
  properties:
    id: {type: integer}
    name: {type: string}
  additionalProperties: false

# Allow any additional properties
FlexibleUser:
  type: object
  properties:
    id: {type: integer}
    name: {type: string}
  additionalProperties: true

# Allow additional properties of specific type
UserMetadata:
  type: object
  properties:
    id: {type: integer}
  additionalProperties:
    type: string
```

**Default**: `additionalProperties` is `true` (allows unknown properties).

## Common Pitfalls

### Avoid

**Ambiguous discriminators**:
```yaml
# Bad - discriminator value not unique
Animal:
  oneOf:
    - $ref: '#/components/schemas/Dog'
    - $ref: '#/components/schemas/Cat'
  discriminator:
    propertyName: type
# Dog and Cat both have `type: "pet"` ❌
```

**Missing required on discriminator**:
```yaml
# Bad - discriminator not required
Dog:
  properties:
    type: {type: string}
# Should include: required: [type]
```

**Overusing allOf for simple extension**:
```yaml
# Overly complex
AdminUser:
  allOf:
    - $ref: '#/components/schemas/User'
    - type: object
      properties:
        admin_level: {type: integer}

# Simpler for one field
AdminUser:
  type: object
  properties:
    id: {type: integer}
    email: {type: string}
    admin_level: {type: integer}
```

**Inconsistent naming**:
```yaml
# Bad - mixed conventions
properties:
  user_id: {type: integer}
  firstName: {type: string}  # ❌ Mixed snake_case and camelCase
  CreatedAt: {type: string}  # ❌ PascalCase for property
```

**Generic descriptions**:
```yaml
# Bad
User:
  description: User object  # Doesn't add information

# Good
User:
  description: Represents a registered user account with authentication and profile information
```

### Do

- Use discriminators with `oneOf` for type-safe polymorphism
- Make discriminator properties required with enum values
- Choose one naming convention and apply consistently
- Validate with appropriate keywords (minLength, minimum, pattern)
- Document complex schemas with detailed descriptions
- Use `readOnly`/`writeOnly` appropriately
- Balance reusability with clarity

## Summary Checklist

When defining schemas:

- [ ] Choose appropriate types and formats
- [ ] Use semantic enum values (not numbers or abbreviations)
- [ ] Handle nullability explicitly (OpenAPI 3.0 vs 3.1)
- [ ] Apply discriminators to `oneOf` schemas
- [ ] Use validation keywords where appropriate
- [ ] Apply consistent naming conventions
- [ ] Create components for reused models
- [ ] Keep operation-specific schemas inline
- [ ] Mark read-only and write-only properties
- [ ] Provide clear, specific descriptions
- [ ] Document complex polymorphic types
