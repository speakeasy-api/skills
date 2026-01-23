# Responses

Best practices for defining API responses in OpenAPI specifications.

## Basic Response Structure

```yaml
paths:
  /users/{id}:
    get:
      operationId: users_get
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

## Status Codes

Choose appropriate HTTP status codes based on the outcome.

### Success Responses (2xx)

| Code | Meaning | Use For |
|------|---------|---------|
| 200 | OK | Successful GET, PUT, PATCH, or POST that returns data |
| 201 | Created | Successful POST that creates a resource |
| 202 | Accepted | Request accepted for async processing |
| 204 | No Content | Successful DELETE or update with no response body |

```yaml
# 200 OK - Return data
get:
  responses:
    '200':
      description: Success
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/User'

# 201 Created - Resource created
post:
  responses:
    '201':
      description: User created successfully
      headers:
        Location:
          schema: {type: string}
          description: URI of created resource
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/User'

# 202 Accepted - Async processing
post:
  responses:
    '202':
      description: Request accepted for processing
      content:
        application/json:
          schema:
            type: object
            properties:
              job_id: {type: string}
              status_url: {type: string}

# 204 No Content - No response body
delete:
  responses:
    '204':
      description: Successfully deleted
```

### Client Error Responses (4xx)

| Code | Meaning | Use For |
|------|---------|---------|
| 400 | Bad Request | Invalid request payload or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Request conflicts with current state |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |

```yaml
responses:
  '400':
    description: Invalid request
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          error: "Invalid email format"
          field: "email"

  '401':
    description: Authentication required
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          error: "Missing or invalid API key"

  '403':
    description: Forbidden
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          error: "Insufficient permissions to access this resource"

  '404':
    description: Resource not found
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          error: "User not found"
          resource_id: "123"

  '409':
    description: Conflict
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          error: "Email already in use"
          field: "email"

  '422':
    description: Validation error
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ValidationError'
        example:
          error: "Validation failed"
          details:
            - field: "email"
              message: "Invalid email format"
            - field: "age"
              message: "Must be at least 13"

  '429':
    description: Rate limit exceeded
    headers:
      Retry-After:
        schema: {type: integer}
        description: Seconds to wait before retry
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          error: "Rate limit exceeded"
          retry_after: 60
```

### Server Error Responses (5xx)

| Code | Meaning | Use For |
|------|---------|---------|
| 500 | Internal Server Error | Unexpected server error |
| 502 | Bad Gateway | Upstream service error |
| 503 | Service Unavailable | Temporary unavailability |
| 504 | Gateway Timeout | Upstream timeout |

```yaml
responses:
  '500':
    description: Internal server error
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'

  '503':
    description: Service temporarily unavailable
    headers:
      Retry-After:
        schema: {type: integer}
        description: Seconds until service is available
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
```

## Error Response Schemas

Define consistent error response schemas:

```yaml
components:
  schemas:
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
        request_id:
          type: string
          description: Unique request identifier for support
        documentation_url:
          type: string
          format: uri
          description: Link to error documentation

    ValidationError:
      type: object
      required: [error, details]
      properties:
        error:
          type: string
          description: Overall error message
        details:
          type: array
          items:
            type: object
            required: [field, message]
            properties:
              field:
                type: string
                description: Field that failed validation
              message:
                type: string
                description: Validation error message
              code:
                type: string
                description: Machine-readable error code
```

## Response Headers

Document important response headers:

```yaml
responses:
  '200':
    description: Success
    headers:
      X-RateLimit-Limit:
        schema: {type: integer}
        description: Total requests allowed per window
      X-RateLimit-Remaining:
        schema: {type: integer}
        description: Requests remaining in current window
      X-RateLimit-Reset:
        schema: {type: integer}
        description: Unix timestamp when window resets
      ETag:
        schema: {type: string}
        description: Entity tag for caching
      Cache-Control:
        schema: {type: string}
        description: Caching directives
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
```

## Content Types

### JSON (Most Common)

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
```

### Multiple Content Types

Support content negotiation:

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'

      application/xml:
        schema:
          $ref: '#/components/schemas/User'

      text/csv:
        schema:
          type: string
          description: CSV representation of user data
```

### Binary Responses (File Downloads)

```yaml
paths:
  /files/{id}/download:
    get:
      operationId: files_download
      responses:
        '200':
          description: File content
          headers:
            Content-Disposition:
              schema: {type: string}
              description: Attachment filename
              example: 'attachment; filename="document.pdf"'
            Content-Type:
              schema: {type: string}
              description: MIME type of the file
          content:
            application/octet-stream:
              schema:
                type: string
                format: binary

            # Or specific types
            image/png:
              schema:
                type: string
                format: binary

            application/pdf:
              schema:
                type: string
                format: binary
```

## Streaming Responses

### Server-Sent Events (SSE)

Use `text/event-stream` for server-sent events:

```yaml
paths:
  /events:
    get:
      operationId: events_stream
      summary: Stream real-time events
      description: |
        Opens a persistent connection and streams events as they occur.
        Events follow the Server-Sent Events (SSE) format.

      responses:
        '200':
          description: Event stream
          content:
            text/event-stream:
              schema:
                type: string
                description: |
                  Server-sent events stream. Each event follows the SSE format:

                  ```
                  event: message
                  data: {"type": "notification", "content": "..."}
                  id: 12345

                  ```

                  Event types:
                  - `message`: Regular notification
                  - `error`: Error event
                  - `heartbeat`: Connection keepalive

              examples:
                notification_stream:
                  summary: Notification stream example
                  value: |
                    event: message
                    data: {"type": "notification", "message": "New order received"}
                    id: 1

                    event: message
                    data: {"type": "notification", "message": "Order processing complete"}
                    id: 2

                    event: heartbeat
                    data: {"timestamp": 1234567890}
                    id: 3
```

### Chunked Transfer

For large responses sent in chunks:

```yaml
paths:
  /export:
    post:
      operationId: data_export
      summary: Export large dataset
      description: |
        Exports data as a stream. Response is sent using chunked
        transfer encoding for efficient streaming of large datasets.

      responses:
        '200':
          description: Data export stream
          headers:
            Transfer-Encoding:
              schema: {type: string}
              example: "chunked"
          content:
            application/x-ndjson:
              schema:
                type: string
                description: |
                  Newline-delimited JSON stream. Each line is a complete
                  JSON object representing one record.

              example: |
                {"id": 1, "name": "Alice", "email": "alice@example.com"}
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
```

### WebSocket (Referenced)

OpenAPI doesn't directly model WebSocket connections, but you can document them:

```yaml
paths:
  /ws/notifications:
    get:
      operationId: notifications_websocket
      summary: WebSocket connection for real-time notifications
      description: |
        Establishes a WebSocket connection for bidirectional real-time messaging.

        **Connection**: `wss://api.example.com/ws/notifications`

        **Authentication**: Pass API key in `Authorization` header during handshake.

        **Message Format**:
        ```json
        {
          "type": "notification",
          "data": {...}
        }
        ```

        See [WebSocket Documentation](https://docs.example.com/websockets) for details.

      responses:
        '101':
          description: Switching Protocols (WebSocket established)
```

## Pagination Responses

Include pagination metadata in responses:

```yaml
responses:
  '200':
    description: Paginated list of users
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
                  description: Number of items skipped
                next_offset:
                  type: integer
                  nullable: true
                  description: Offset for next page, null if last page
        examples:
          page_one:
            summary: First page
            value:
              data:
                - {id: 1, name: "Alice"}
                - {id: 2, name: "Bob"}
              pagination:
                total: 100
                limit: 20
                offset: 0
                next_offset: 20
```

## Reusable Responses

Define common responses in components:

```yaml
components:
  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Resource not found"
            code: "NOT_FOUND"

    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Missing or invalid authentication"
            code: "UNAUTHORIZED"

    ValidationError:
      description: Validation error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidationError'

    RateLimitExceeded:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema: {type: integer}
          description: Seconds to wait before retry
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

# Use in operations
paths:
  /users/{id}:
    get:
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'
        '401':
          $ref: '#/components/responses/Unauthorized'
```

## Async Operations

For long-running operations:

```yaml
paths:
  /reports/generate:
    post:
      operationId: reports_generate
      summary: Generate report (async)
      responses:
        '202':
          description: Report generation started
          headers:
            Location:
              schema: {type: string}
              description: URL to poll for status
          content:
            application/json:
              schema:
                type: object
                required: [job_id, status, status_url]
                properties:
                  job_id:
                    type: string
                    format: uuid
                    description: Unique job identifier
                  status:
                    type: string
                    enum: [pending, processing]
                    description: Current job status
                  status_url:
                    type: string
                    format: uri
                    description: URL to check job status
                  estimated_completion:
                    type: string
                    format: date-time
                    description: Estimated completion time

  /jobs/{job_id}:
    get:
      operationId: jobs_get_status
      summary: Check job status
      responses:
        '200':
          description: Job status
          content:
            application/json:
              schema:
                type: object
                required: [job_id, status]
                properties:
                  job_id: {type: string}
                  status:
                    type: string
                    enum: [pending, processing, completed, failed]
                  progress:
                    type: integer
                    minimum: 0
                    maximum: 100
                    description: Completion percentage
                  result_url:
                    type: string
                    format: uri
                    description: URL to download result (when completed)
                  error:
                    type: string
                    description: Error message (when failed)
```

## Common Pitfalls

### Avoid

**Missing error responses**:
```yaml
responses:
  '200':
    description: Success
  # ❌ No 404, 401, 500, etc.
```

**Generic descriptions**:
```yaml
'200':
  description: OK
'404':
  description: Not found
  # ❌ Not helpful
```

**Inconsistent error formats**:
```yaml
# Different formats across endpoints
# Endpoint 1
'400':
  schema: {type: string}  # Plain string

# Endpoint 2
'400':
  schema:
    properties:
      error: {type: string}  # Object

# ❌ Inconsistent
```

**Missing content wrapper**:
```yaml
'200':
  description: Success
  schema:
    $ref: '#/components/schemas/User'
  # ❌ Missing content wrapper
```

**Correct**:
```yaml
'200':
  description: Success
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/User'
```

**Not documenting streaming format**:
```yaml
'200':
  content:
    text/event-stream:
      schema: {type: string}
  # ❌ No description of event format
```

### Do

- Document all expected responses (success and errors)
- Use appropriate status codes (don't use 200 for everything)
- Provide specific, helpful descriptions
- Use consistent error response schemas
- Document response headers (rate limits, pagination, caching)
- Include examples for complex responses
- Wrap schemas in `content` with media type
- Document streaming formats clearly
- Use reusable response components for common patterns
- Include pagination metadata in list responses

## Summary Checklist

For each operation:

- [ ] At least one success response (2xx) defined
- [ ] Common error responses documented (401, 404, 500, etc.)
- [ ] All responses wrapped in `content` with media type
- [ ] Schemas defined (inline or referenced)
- [ ] Specific, helpful descriptions
- [ ] Response headers documented (if any)
- [ ] Examples provided for complex responses
- [ ] Consistent error response format
- [ ] Streaming format documented (if applicable)
- [ ] Pagination metadata included (for lists)
- [ ] Binary responses use `format: binary`
- [ ] Async operations include status URLs

## Advanced Patterns

### Conditional Responses

Different response schemas based on request:

```yaml
paths:
  /data:
    get:
      parameters:
        - name: format
          in: query
          schema:
            type: string
            enum: [summary, detailed]
      responses:
        '200':
          description: |
            Data response. Schema depends on `format` parameter:
            - `summary`: Returns basic information
            - `detailed`: Returns full details
          content:
            application/json:
              schema:
                oneOf:
                  - $ref: '#/components/schemas/SummaryData'
                  - $ref: '#/components/schemas/DetailedData'
```

### Hypermedia (HATEOAS)

Include links to related resources:

```yaml
responses:
  '200':
    description: Success with hypermedia links
    content:
      application/json:
        schema:
          type: object
          required: [data, links]
          properties:
            data:
              $ref: '#/components/schemas/User'
            links:
              type: object
              properties:
                self:
                  type: string
                  format: uri
                orders:
                  type: string
                  format: uri
                avatar:
                  type: string
                  format: uri
        example:
          data:
            id: 123
            name: "John Doe"
          links:
            self: "https://api.example.com/users/123"
            orders: "https://api.example.com/users/123/orders"
            avatar: "https://api.example.com/users/123/avatar"
```
