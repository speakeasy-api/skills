---
short_description: OpenAPI schema objects and data types
long_description: Schema objects define data types in OpenAPI including strings, numbers, booleans, arrays, objects, enums, and null. Based on JSON Schema with OpenAPI extensions for API documentation.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/schemas.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# OpenAPI Schemas

Schema objects define all data types used as input or output in OpenAPI specifications.

## Supported Data Types

- **Strings** - Character sequences, dates, times, passwords, byte, binary
- **Numbers** - Integers or floating-point
- **Booleans** - True or false values
- **Arrays** - Collections of other data types
- **Objects** - Key-value pair collections
- **Enums** - Fixed lists of possible values
- **Null** - Null values

## JSON Schema Foundation

OpenAPI 3.1 uses JSON Schema 2020-12 with minor modifications:

- `description` - May contain CommonMark markdown syntax
- `format` - Extended with additional OpenAPI-specific formats

## OpenAPI Extensions to JSON Schema

| Field | Type | Description |
|-------|------|-------------|
| `discriminator` | Discriminator Object | Differentiate related schemas based on field value |
| `xml` | XML Object | How schema should be represented as XML |
| `externalDocs` | External Documentation Object | Link to external documentation |
| `example` | Any | Example value (deprecated, use `examples` instead) |
| `x-*` | Any | Custom extension fields |

## Basic Schema Example

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
          examples:
            - "123e4567-e89b-12d3-a456-426614174000"
        name:
          type: string
          examples:
            - "John Doe"
        age:
          type: integer
          minimum: 0
          maximum: 150
          examples:
            - 42
        email:
          type: string
          format: email
          examples:
            - "john@example.com"
      required:
        - id
        - name
        - email
```

## String Schemas

```yaml
BasicString:
  type: string
  examples:
    - "Hello World"

Email:
  type: string
  format: email
  examples:
    - "user@example.com"

DateTime:
  type: string
  format: date-time
  examples:
    - "2024-01-15T10:30:00Z"

UUID:
  type: string
  format: uuid
  examples:
    - "123e4567-e89b-12d3-a456-426614174000"

Pattern:
  type: string
  pattern: "^[A-Z]{3}-[0-9]{4}$"
  examples:
    - "ABC-1234"
```

## Number Schemas

```yaml
Integer:
  type: integer
  examples:
    - 42

IntegerWithRange:
  type: integer
  minimum: 1
  maximum: 100
  examples:
    - 50

Float:
  type: number
  format: float
  examples:
    - 3.14159

Double:
  type: number
  format: double
  examples:
    - 2.71828182845905
```

## Boolean Schema

```yaml
IsActive:
  type: boolean
  examples:
    - true
    - false
```

## Array Schemas

```yaml
StringArray:
  type: array
  items:
    type: string
  examples:
    - ["apple", "banana", "orange"]

ObjectArray:
  type: array
  items:
    $ref: "#/components/schemas/User"
  minItems: 1
  maxItems: 100
```

## Object Schemas

```yaml
Address:
  type: object
  properties:
    street:
      type: string
    city:
      type: string
    country:
      type: string
    postalCode:
      type: string
      pattern: "^[0-9]{5}$"
  required:
    - street
    - city
    - country
  additionalProperties: false
```

## Enum Schemas

```yaml
Status:
  type: string
  enum:
    - pending
    - approved
    - rejected
  examples:
    - "pending"

Priority:
  type: integer
  enum:
    - 1
    - 2
    - 3
    - 4
    - 5
  examples:
    - 3
```

## Null Values

**OpenAPI 3.0:**

```yaml
NullableString:
  type: string
  nullable: true
```

**OpenAPI 3.1 (JSON Schema compliant):**

```yaml
NullableString:
  type: [string, "null"]

# Or using oneOf
NullableString:
  oneOf:
    - type: string
    - type: "null"
```

## Composition

### allOf (AND)

```yaml
Employee:
  allOf:
    - $ref: "#/components/schemas/Person"
    - type: object
      properties:
        employeeId:
          type: string
        department:
          type: string
```

### oneOf (XOR)

```yaml
Pet:
  oneOf:
    - $ref: "#/components/schemas/Cat"
    - $ref: "#/components/schemas/Dog"
  discriminator:
    propertyName: petType
    mapping:
      cat: "#/components/schemas/Cat"
      dog: "#/components/schemas/Dog"
```

### anyOf (OR)

```yaml
Contact:
  anyOf:
    - type: object
      properties:
        email:
          type: string
          format: email
    - type: object
      properties:
        phone:
          type: string
```

## Polymorphism with Discriminator

```yaml
components:
  schemas:
    Animal:
      type: object
      required:
        - animalType
      properties:
        animalType:
          type: string
      discriminator:
        propertyName: animalType
        mapping:
          cat: "#/components/schemas/Cat"
          dog: "#/components/schemas/Dog"

    Cat:
      allOf:
        - $ref: "#/components/schemas/Animal"
        - type: object
          properties:
            meow:
              type: boolean

    Dog:
      allOf:
        - $ref: "#/components/schemas/Animal"
        - type: object
          properties:
            bark:
              type: boolean
```

## Read-Only and Write-Only

```yaml
User:
  type: object
  properties:
    id:
      type: string
      readOnly: true  # Only in responses
    password:
      type: string
      writeOnly: true # Only in requests
    username:
      type: string
```

## Deprecated Fields

```yaml
User:
  type: object
  properties:
    oldField:
      type: string
      deprecated: true
      description: "Use newField instead"
    newField:
      type: string
```

## Common Patterns

### Pagination Response

```yaml
PagedResults:
  type: object
  properties:
    data:
      type: array
      items:
        $ref: "#/components/schemas/Item"
    meta:
      type: object
      properties:
        page:
          type: integer
        pageSize:
          type: integer
        totalPages:
          type: integer
```

### Error Response

```yaml
Error:
  type: object
  properties:
    code:
      type: string
    message:
      type: string
    details:
      type: object
  required:
    - code
    - message
```

## Best Practices

1. Always provide `examples` (not deprecated `example`)
2. Use `$ref` to avoid duplication
3. Set `additionalProperties: false` when strict validation needed
4. Use `description` with CommonMark for rich documentation
5. Define schemas in `components/schemas` for reusability
6. Use appropriate formats (`email`, `uuid`, `date-time`, etc.)
7. Set reasonable `minimum`, `maximum`, `minLength`, `maxLength` constraints
8. Use `required` array to specify mandatory fields
9. Prefer `readOnly`/`writeOnly` over separate request/response schemas when appropriate

## Validation Commands

```bash
speakeasy validate openapi -s spec.yaml
```

## Reference

- JSON Schema 2020-12: https://json-schema.org/draft/2020-12/
- OpenAPI Specification: https://spec.openapis.org/oas/latest.html
- Learn JSON Schema: https://www.learnjsonschema.com

---

## Pre-defined TODO List

When defining schemas in OpenAPI, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Identify all data types used in API | Identifying data types |
| 2 | Define reusable schemas in components/schemas | Defining reusable schemas |
| 3 | Add examples to all schema properties | Adding examples to properties |
| 4 | Set validation rules (min, max, pattern) | Setting validation rules |
| 5 | Mark required fields in required array | Marking required fields |
| 6 | Use $ref for schema reuse | Using $ref for schema reuse |
| 7 | Validate schema definitions | Validating schema definitions |

**Usage:**
```
TodoWrite([
  {content: "Identify all data types used in API", status: "pending", activeForm: "Identifying data types"},
  {content: "Define reusable schemas in components/schemas", status: "pending", activeForm: "Defining reusable schemas"},
  {content: "Add examples to all schema properties", status: "pending", activeForm: "Adding examples to properties"},
  {content: "Set validation rules (min, max, pattern)", status: "pending", activeForm: "Setting validation rules"},
  {content: "Mark required fields in required array", status: "pending", activeForm: "Marking required fields"},
  {content: "Use $ref for schema reuse", status: "pending", activeForm: "Using $ref for schema reuse"},
  {content: "Validate schema definitions", status: "pending", activeForm: "Validating schema definitions"}
])
```

