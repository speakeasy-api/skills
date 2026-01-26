# Request Bodies

Best practices for defining request bodies in OpenAPI operations.

## Basic Request Body

A request body describes the payload sent to the server:

```yaml
paths:
  /users:
    post:
      operationId: users_create
      requestBody:
        required: true
        description: User data to create
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
```

## Content Types

### JSON (Most Common)

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required: [email, name]
        properties:
          email:
            type: string
            format: email
          name:
            type: string
          age:
            type: integer
```

### XML

```yaml
requestBody:
  content:
    application/xml:
      schema:
        type: object
        properties:
          user:
            type: object
            properties:
              name: {type: string}
              email: {type: string}
```

### Plain Text

```yaml
requestBody:
  content:
    text/plain:
      schema:
        type: string
        example: "This is raw text content"
```

### Multiple Content Types

Support multiple formats for the same operation:

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/User'
      examples:
        basic:
          value:
            name: "John Doe"
            email: "john@example.com"

    application/xml:
      schema:
        $ref: '#/components/schemas/User'
      examples:
        basic:
          value: |
            <user>
              <name>John Doe</name>
              <email>john@example.com</email>
            </user>
```

## File Uploads

### Single File Upload

Use `multipart/form-data` with `format: binary`:

```yaml
paths:
  /files/upload:
    post:
      operationId: files_upload
      summary: Upload a file
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file:
                  type: string
                  format: binary
                  description: The file to upload
```

### File Upload with Metadata

Include additional fields alongside the file:

```yaml
requestBody:
  required: true
  content:
    multipart/form-data:
      schema:
        type: object
        required: [file]
        properties:
          file:
            type: string
            format: binary
            description: The file to upload

          description:
            type: string
            description: File description

          tags:
            type: array
            items:
              type: string
            description: Tags for categorization

          public:
            type: boolean
            default: false
            description: Whether the file is publicly accessible
```

### Multiple File Upload

Allow uploading multiple files:

```yaml
requestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          files:
            type: array
            items:
              type: string
              format: binary
            description: Multiple files to upload

          album_name:
            type: string
            description: Album name for the files
```

### File Upload with Specific Types

Restrict file types using content type:

```yaml
requestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          image:
            type: string
            format: binary
            description: Image file (JPEG, PNG, or GIF)

      encoding:
        image:
          contentType: image/jpeg, image/png, image/gif
```

### Base64-Encoded Files in JSON

For base64-encoded files in JSON payload:

```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
        required: [filename, content]
        properties:
          filename:
            type: string
            description: Original filename

          content:
            type: string
            format: byte
            description: Base64-encoded file content

          mime_type:
            type: string
            description: MIME type of the file
            example: "image/png"
```

**When to use**:
- API requires JSON-only communication
- File sizes are small
- Base64 encoding overhead is acceptable

**Prefer `multipart/form-data` when**:
- Uploading large files (base64 adds ~33% overhead)
- Uploading multiple files
- Better client library support needed

## Encoding

### Form Data Encoding

The `encoding` property specifies how form data is serialized:

```yaml
requestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          file:
            type: string
            format: binary

          metadata:
            type: object
            properties:
              tags:
                type: array
                items:
                  type: string
              visibility:
                type: string
                enum: [public, private]

      encoding:
        file:
          contentType: image/png, image/jpeg

        metadata:
          contentType: application/json
          # Encode the metadata object as JSON
```

### URL-Encoded Forms

For traditional HTML form submissions:

```yaml
requestBody:
  content:
    application/x-www-form-urlencoded:
      schema:
        type: object
        required: [username, password]
        properties:
          username:
            type: string
          password:
            type: string
            format: password
          remember_me:
            type: boolean
            default: false

      encoding:
        remember_me:
          style: form
          explode: true
```

## Required vs Optional

Mark whether the request body is required:

```yaml
# Required request body
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/User'

# Optional request body (rare)
requestBody:
  required: false
  description: Optional filter criteria
  content:
    application/json:
      schema:
        type: object
        properties:
          filter: {type: string}
```

**Most request bodies should be required.** Optional request bodies are uncommon and can confuse API consumers.

## Reusable Request Bodies

Define reusable request bodies in components:

```yaml
components:
  requestBodies:
    UserCreate:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CreateUserRequest'

    FileUpload:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            properties:
              file:
                type: string
                format: binary

# Reference in operations
paths:
  /users:
    post:
      requestBody:
        $ref: '#/components/requestBodies/UserCreate'

  /files:
    post:
      requestBody:
        $ref: '#/components/requestBodies/FileUpload'
```

**When to reuse**:
- Multiple operations accept the same payload structure
- Complex request bodies used across endpoints

**When to inline**:
- Operation-specific payloads
- Simple, one-off structures

## Partial Updates (PATCH)

For PATCH operations, make all fields optional:

```yaml
paths:
  /users/{id}:
    patch:
      operationId: users_patch
      summary: Partially update a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
                  format: email
                age:
                  type: integer
              # No required array - all fields optional
              # Only send fields being updated

            examples:
              update_name:
                summary: Update only name
                value:
                  name: "Jane Doe"

              update_email:
                summary: Update only email
                value:
                  email: "jane.doe@example.com"
```

**Convention**: PATCH payloads should have no required fields since the client sends only what changes.

## Null Values

Handle null values explicitly:

```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:
          # Can be string or explicitly null
          middle_name:
            type: [string, "null"]
            description: Middle name, or null to clear

          # Can be omitted or provided
          nickname:
            type: string
            description: Optional nickname
```

**Distinguish**:
- **Omitted field**: Don't modify existing value
- **Null value**: Clear/remove existing value
- **Empty string**: Set to empty string (different from null)

## Content Negotiation

Document how the API handles different content types:

```yaml
paths:
  /data/import:
    post:
      operationId: data_import
      summary: Import data
      description: |
        Accepts data in JSON or CSV format. The API auto-detects
        the format based on Content-Type header.

      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Record'

          text/csv:
            schema:
              type: string
              description: |
                CSV format with headers in first row.
                Columns: id, name, email, created_at

            example: |
              id,name,email,created_at
              1,John Doe,john@example.com,2023-01-15
              2,Jane Smith,jane@example.com,2023-01-16
```

## Validation in Request Bodies

Use JSON Schema validation keywords:

```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
        required: [email, password, terms_accepted]
        properties:
          email:
            type: string
            format: email
            maxLength: 255

          password:
            type: string
            format: password
            minLength: 8
            maxLength: 72
            pattern: '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])'
            description: |
              Must contain at least:
              - 8 characters
              - One uppercase letter
              - One lowercase letter
              - One digit
              - One special character (@$!%*?&)

          username:
            type: string
            minLength: 3
            maxLength: 32
            pattern: '^[a-zA-Z0-9_]+$'
            description: Alphanumeric and underscore only

          age:
            type: integer
            minimum: 13
            maximum: 120
            description: Must be at least 13 years old

          terms_accepted:
            type: boolean
            enum: [true]
            description: Must explicitly accept terms
```

## Common Pitfalls

### Avoid

**Forgetting to specify content type**:
```yaml
requestBody:
  schema:
    type: object
  # ❌ Missing content wrapper
```

**Correct**:
```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
```

**Using wrong format for files**:
```yaml
file:
  type: string
  # ❌ Missing format: binary
```

**Correct**:
```yaml
file:
  type: string
  format: binary
```

**Vague descriptions**:
```yaml
requestBody:
  description: Request data
  # ❌ Not helpful
```

**Correct**:
```yaml
requestBody:
  description: User profile information including email, name, and optional preferences
```

**Making PATCH fields required**:
```yaml
patch:
  requestBody:
    content:
      application/json:
        schema:
          required: [name, email]  # ❌ PATCH should have optional fields
```

**Not documenting file size limits**:
```yaml
file:
  type: string
  format: binary
  # ❌ No size limit documented
```

**Correct**:
```yaml
file:
  type: string
  format: binary
  description: File to upload (maximum 10MB)
```

### Do

- Always wrap schemas in `content` with appropriate media type
- Use `format: binary` for file uploads
- Use `multipart/form-data` for file uploads (not JSON with base64 unless necessary)
- Make PATCH payloads fully optional
- Document file size limits and accepted types
- Provide validation rules with helpful descriptions
- Use `required: true` for most request bodies
- Include examples for complex payloads
- Be explicit about null vs omitted fields
- Use reusable components for common request shapes

## Summary Checklist

For each request body:

- [ ] Wrapped in `content` with appropriate media type
- [ ] Schema defined (inline or referenced)
- [ ] `required` field set appropriately (usually `true`)
- [ ] Description explains what the payload contains
- [ ] File uploads use `format: binary` with `multipart/form-data`
- [ ] Validation rules applied where appropriate
- [ ] Examples provided for complex structures
- [ ] PATCH operations have optional fields
- [ ] File size limits documented (if applicable)
- [ ] Multiple content types supported if needed
- [ ] Encoding specified for form data (if needed)

## Advanced Patterns

### Conditional Request Bodies

Some operations may accept different payloads based on parameters:

```yaml
paths:
  /content:
    post:
      operationId: content_create
      parameters:
        - name: type
          in: query
          required: true
          schema:
            type: string
            enum: [article, video, image]

      requestBody:
        required: true
        content:
          application/json:
            schema:
              oneOf:
                - $ref: '#/components/schemas/ArticleContent'
                - $ref: '#/components/schemas/VideoContent'
                - $ref: '#/components/schemas/ImageContent'
              discriminator:
                propertyName: content_type
                mapping:
                  article: '#/components/schemas/ArticleContent'
                  video: '#/components/schemas/VideoContent'
                  image: '#/components/schemas/ImageContent'

        description: |
          Content payload. Structure depends on `type` parameter:
          - `article`: Provide title, body, and author
          - `video`: Provide title, video_url, and duration
          - `image`: Provide title, image_url, and alt_text
```

### Bulk Operations

For operations that accept multiple items:

```yaml
paths:
  /users/bulk:
    post:
      operationId: users_bulk_create
      summary: Create multiple users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [users]
              properties:
                users:
                  type: array
                  items:
                    $ref: '#/components/schemas/CreateUserRequest'
                  minItems: 1
                  maxItems: 100
                  description: Array of users to create (max 100)
```

### Request Body with External Reference

Link to external documentation for complex payloads:

```yaml
requestBody:
  required: true
  description: |
    Webhook configuration payload.

    For detailed schema and examples, see the
    [Webhook Configuration Guide](https://docs.example.com/webhooks/config).
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/WebhookConfig'
```
