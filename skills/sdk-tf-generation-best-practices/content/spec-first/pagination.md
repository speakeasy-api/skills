---
short_description: Document pagination in OpenAPI specifications
long_description: Pagination allows APIs to return subsets of large collections. This guide covers query parameters, response metadata, hypermedia links, and Speakeasy x-speakeasy-pagination extension for SDK pagination handling.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/pagination.mdx, src/content/docs/sdks/customize/runtime/pagination.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Pagination in OpenAPI

Pagination divides large result sets into manageable pages to avoid overwhelming servers and clients.

## Common Pagination Strategies

See API Design Guide for detailed pagination strategies: `/api-design/pagination`

**CHOOSE ONE approach:**

1. **Offset/Limit** (page-based): `?page=1&limit=20`
2. **Cursor** (token-based): `?cursor=abc123`
3. **URL-based**: Use hypermedia links for next/prev pages

## Query Parameters

Most common pagination approach using `page` and `limit` parameters:

```yaml
paths:
  /stations:
    get:
      summary: Get a list of train stations
      description: Returns a paginated and searchable list of all train stations.
      operationId: get-stations
      parameters:
        - name: page
          in: query
          description: The page number to return
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
          example: 1
        - name: limit
          in: query
          description: The number of items to return per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
          example: 10
```

**Key points:**
- `page` defaults to 1
- `limit` has minimum and maximum constraints
- Both parameters are optional

## Response Metadata

Include pagination information in response body using a `meta` object:

```yaml
responses:
  '200':
    description: A paginated list of train stations.
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                $ref: '#/components/schemas/Station'
            meta:
              type: object
              properties:
                page:
                  type: integer
                  example: 2
                size:
                  type: integer
                  example: 10
                total_pages:
                  type: integer
                  example: 100
```

**Example response:**

```json
{
  "data": [...],
  "meta": {
    "page": 2,
    "size": 10,
    "total_pages": 100
  }
}
```

## Hypermedia Links

Provide navigation links instead of requiring clients to construct URLs:

```yaml
responses:
  '200':
    description: OK
    content:
      application/json:
        schema:
          allOf:
            - $ref: '#/components/schemas/Wrapper-Collection'
            - properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Station'
            - properties:
                links:
                  allOf:
                    - $ref: '#/components/schemas/Links-Self'
                    - $ref: '#/components/schemas/Links-Pagination'

components:
  schemas:
    Links-Self:
      description: The link to the current resource.
      type: object
      properties:
        self:
          type: string
          format: uri
    Links-Pagination:
      description: Links to the next and previous pages of a paginated response.
      type: object
      properties:
        next:
          type: string
          format: uri
        prev:
          type: string
          format: uri
    Wrapper-Collection:
      type: object
      properties:
        data:
          description: The wrapper for a collection is an array of objects.
          type: array
          items:
            type: object
        links:
          description: A set of hypermedia links which serve as controls for the client.
          type: object
          readOnly: true
```

**Example response:**

```json
{
  "data": [...],
  "links": {
    "self": "https://api.example.com/stations?page=2",
    "next": "https://api.example.com/stations?page=3",
    "prev": "https://api.example.com/stations?page=1"
  }
}
```

## HTTP Header Pagination

Use custom headers instead of response body (less common):

```yaml
paths:
  /stations:
    get:
      summary: Get a list of train stations
      description: Returns a paginated and searchable list of all train stations.
      operationId: get-stations
      responses:
        '200':
          description: A paginated list of train stations.
          headers:
            X-Total-Count:
              description: The total number of items in the collection.
              schema:
                type: integer
                example: 1000
            X-Page:
              description: The current page number.
              schema:
                type: integer
                example: 2
            X-Per-Page:
              description: The number of items per page.
              schema:
                type: integer
                example: 10
            Link:
              description: A set of hypermedia links which serve as controls for the client.
              schema:
                type: string
                example: |
                  <https://api.example.com/stations?page=2>; rel="self",
                  <https://api.example.com/stations?page=3>; rel="next",
                  <https://api.example.com/stations?page=1>; rel="prev"
```

> **Note:** Header-based pagination has no standard format. Document clearly.

## Speakeasy Pagination Extension

Speakeasy SDKs support automatic pagination handling using `x-speakeasy-pagination`. This extension enables structured pagination handling so developers can iterate through paginated results without manual page management.

### Extension Configuration

The `x-speakeasy-pagination` extension has three components:

| Component | Description |
|-----------|-------------|
| `type` | Pagination strategy: `offsetLimit`, `cursor`, or `url` |
| `inputs` | Parameters that control pagination (page, offset, limit, cursor) |
| `outputs` | JSONPath expressions identifying results and pagination metadata |

### Type 1: Offset/Limit Pagination

**Page-based example:**

```yaml
/stations:
  get:
    parameters:
      - name: page
        in: query
        schema:
          type: integer
        required: true
    responses:
      "200":
        description: OK
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: integer
              required:
                - data
    x-speakeasy-pagination:
      type: offsetLimit
      inputs:
        - name: page
          in: parameters
          type: page
      outputs:
        results: $.data
```

The SDK automatically increments the `page` parameter on successive calls. Pagination stops when the results array is empty or falls below the configured limit.

**Offset-based example:**

```yaml
x-speakeasy-pagination:
  type: offsetLimit
  inputs:
    - name: offset
      in: parameters
      type: offset
    - name: limit
      in: parameters
      type: limit
  outputs:
    results: $.data.resultArray
```

With offset pagination, the offset increments by the returned results count.

### Type 2: Cursor-Based Pagination

Use cursor values extracted from previous responses:

```yaml
x-speakeasy-pagination:
  type: cursor
  inputs:
    - name: since
      in: requestBody
      type: cursor
  outputs:
    nextCursor: $.data.resultArray[-1].created_at
```

The `[-1]` JSONPath syntax extracts the last array element. The cursor value populates the input parameter for subsequent requests.

### Type 3: URL-Based Pagination

When APIs return explicit next-page URLs:

```yaml
x-speakeasy-pagination:
  type: url
  outputs:
    nextUrl: $.links.next
```

The response must include a field containing the complete URL for the next page.

### Input Configuration

| Field | Description |
|-------|-------------|
| `name` | Parameter or request-body property name |
| `in` | Either `parameters` or `requestBody` |
| `type` | One of: `page`, `offset`, `limit`, `cursor` |

### Output Configuration

| Field | Description |
|-------|-------------|
| `results` | JSONPath to results array (stops when empty or smaller than limit) |
| `numPages` | JSONPath to total page count (stops when exceeded) |
| `nextCursor` | JSONPath for cursor-based pagination |
| `nextUrl` | JSONPath for URL-based pagination |

### SDK Usage Pattern

Generated SDKs provide intuitive iteration:

```python
# Python example
response = sdk.get_stations(page=1)
while response is not None:
    for station in response.data:
        process(station)
    response = response.next()
```

```typescript
// TypeScript example
let response = await sdk.getStations({ page: 1 });
while (response !== null) {
    for (const station of response.data) {
        process(station);
    }
    response = await response.next();
}
```

When pagination completes, `next()` returns `null`, cleanly ending iteration without throwing errors.

## Best Practices

1. Always document default values for pagination parameters
2. Set reasonable limits on `limit` parameter (e.g., max 100)
3. Include total count when possible for client pagination controls
4. Prefer hypermedia links over client-constructed URLs
5. Be consistent across all paginated endpoints
6. Document pagination behavior in endpoint descriptions

## Reusable Components

Define pagination schemas once and reference across endpoints:

```yaml
components:
  parameters:
    PageParam:
      name: page
      in: query
      description: Page number
      schema:
        type: integer
        minimum: 1
        default: 1
    LimitParam:
      name: limit
      in: query
      description: Items per page
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 10
```

Reference in operations:

```yaml
paths:
  /stations:
    get:
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
```

Learn more about components: `/openapi/components`

---

## Pre-defined TODO List

When implementing pagination in OpenAPI, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Choose pagination strategy (offset, cursor, or URL-based) | Choosing pagination strategy |
| 2 | Add pagination parameters to operation | Adding pagination parameters |
| 3 | Define response metadata structure | Defining response metadata |
| 4 | Add x-speakeasy-pagination extension if using Speakeasy | Adding x-speakeasy-pagination extension |
| 5 | Create reusable parameter components | Creating reusable parameters |
| 6 | Test pagination with speakeasy validate | Testing pagination with validate |

**Usage:**
```
TodoWrite([
  {content: "Choose pagination strategy (offset, cursor, or URL-based)", status: "pending", activeForm: "Choosing pagination strategy"},
  {content: "Add pagination parameters to operation", status: "pending", activeForm: "Adding pagination parameters"},
  {content: "Define response metadata structure", status: "pending", activeForm: "Defining response metadata"},
  {content: "Add x-speakeasy-pagination extension if using Speakeasy", status: "pending", activeForm: "Adding x-speakeasy-pagination extension"},
  {content: "Create reusable parameter components", status: "pending", activeForm: "Creating reusable parameters"},
  {content: "Test pagination with speakeasy validate", status: "pending", activeForm: "Testing pagination with validate"}
])
```

