---
short_description: Configure SDK runtime behavior for retries, timeouts, pagination, and servers
long_description: |
  Comprehensive guide for configuring SDK runtime behavior using OpenAPI extensions
  and SDK initialization options. Covers retry strategies, timeout configuration,
  pagination patterns, server selection, and custom HTTP client integration.
source:
  - url: "https://speakeasy.com/docs/customize-sdks/retries"
    last_reconciled: "2025-12-11"
  - url: "https://speakeasy.com/docs/customize-sdks/timeouts"
    last_reconciled: "2025-12-11"
  - url: "https://speakeasy.com/docs/customize-sdks/pagination"
    last_reconciled: "2025-12-11"
  - url: "https://speakeasy.com/docs/customize-sdks/servers"
    last_reconciled: "2025-12-11"
  - url: "https://speakeasy.com/docs/customize-sdks/custom-http-client"
    last_reconciled: "2025-12-11"
related:
  - "../plans/sdk-generation.md"
  - "./hooks.md"
  - "../sdk-languages/typescript.md"
  - "../sdk-languages/python.md"
  - "../sdk-languages/go.md"
---

# SDK Runtime Configuration

Configure SDK runtime behavior using OpenAPI extensions and initialization options. This guide covers retries, timeouts, pagination, server selection, and custom HTTP clients.

## Retry Configuration

Automatically retry failed requests due to network errors or specific HTTP status codes.

### Global Retries

Configure retries for all SDK operations using the `x-speakeasy-retries` extension at the root of the OpenAPI document:

```yaml
openapi: 3.0.3
info:
  title: Swagger Petstore
  version: 1.0.11
servers:
  - url: https://petstore3.swagger.io/api/v3
x-speakeasy-retries:
  strategy: backoff
  backoff:
    initialInterval: 500        # 500 milliseconds
    maxInterval: 60000          # 60 seconds
    maxElapsedTime: 3600000     # 1 hour
    exponent: 1.5
  statusCodes:
    - 5XX                       # Retry all 5xx errors
  retryConnectionErrors: true
```

### Retry Configuration Options

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| `strategy` | `string` | Retry strategy (`backoff` only) | Yes |
| `backoff.initialInterval` | `integer` | Initial retry interval in milliseconds | No |
| `backoff.maxInterval` | `integer` | Maximum interval between retries in milliseconds | No |
| `backoff.maxElapsedTime` | `integer` | Maximum elapsed time for retries in milliseconds | No |
| `backoff.exponent` | `number` | Exponent for increasing retry intervals | No |
| `statusCodes` | `array` | HTTP status codes to retry on | Yes |
| `retryConnectionErrors` | `boolean` | Whether to retry connection errors | No |

**Default backoff values:**
- `initialInterval`: 500
- `maxInterval`: 60000
- `maxElapsedTime`: 3600000
- `exponent`: 1.5

**Status code patterns:**
- Specific codes: `"408"`, `"500"`, `"502"`, `"503"`
- Wildcard ranges: `"5XX"` (retries 500-599), `"4XX"` (retries 400-499)

### Per-Operation Retries

Override global retry configuration for specific operations:

```yaml
paths:
  /pet/findByStatus:
    get:
      operationId: findPetsByStatus
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 500
          maxInterval: 60000
          maxElapsedTime: 3600000
          exponent: 1.5
        statusCodes:
          - 408
          - 500
          - 502
          - 503
        retryConnectionErrors: true
```

### Runtime Retry Override

**CHOOSE ONE:**

**Option 1: Disable retries globally**

```typescript
// TypeScript
const sdk = new SDK({retryConfig: {strategy: "none"}});
```

```python
# Python
s = SDK(retry_config=RetryConfig(
    strategy='none',
    backoff=None,
    retry_connection_errors=False
))
```

```go
// Go
s := sdk.New(sdk.WithRetryConfig(utils.RetryConfig{Strategy: "none"}))
```

**Option 2: Override retry configuration per-request**

```typescript
// TypeScript
await sdk.findPetsByStatus(request, {
  strategy: "backoff",
  backoff: {
    initialInterval: 100,
    maxInterval: 10000,
    exponent: 1.1,
    maxElapsedTime: 60000,
  },
  retryConnectionErrors: false,
});
```

```python
# Python
res = s.find_pets_by_status(request, RetryConfig(
    strategy='backoff',
    backoff=BackoffStrategy(
        initial_interval=100,
        max_interval=10000,
        exponent=1.1,
        max_elapsed_time=60000
    ),
    retry_connection_errors=False
))
```

```go
// Go
s.FindPetsByStatus(&operations.FindPetsByStatusRequest{},
    operations.WithRetries(utils.RetryConfig{
        Strategy: "backoff",
        Backoff: &utils.BackoffStrategy{
            InitialInterval: 100,
            MaxInterval: 10000,
            MaxElapsedTime: 60000,
            Exponent: 1.1,
        },
        RetryConnectionErrors: false,
    },
))
```

### Idempotency Headers

For endpoints with idempotency headers, retries use the same idempotency key:

```yaml
paths:
  /pet:
    put:
      operationId: putPet
      x-speakeasy-retries:
        strategy: backoff
        statusCodes:
          - 5XX
        retryConnectionErrors: false
      parameters:
        - name: Idempotency-Key
          schema:
            type: string
          in: header
```

### Respecting Retry-After Headers

SDKs automatically respect `Retry-After` headers if present:

```yaml
responses:
  "429":
    description: Too Many Requests
    headers:
      Retry-After:
        description: Seconds to wait before retrying
        schema:
          type: integer
          example: 120
```

The SDK waits for the specified duration before retrying, as long as it's within the max elapsed time.

> **Note:** Retry-After support is currently available in TypeScript with additional language support coming.

---

## Timeout Configuration

Configure request timeouts using the `x-speakeasy-timeout` extension. Timeout values are always in milliseconds.

### Global Timeouts

```yaml
openapi: 3.0.3
info:
  title: Swagger Petstore
  version: 1.0.11
servers:
  - url: https://petstore3.swagger.io/api/v3
x-speakeasy-timeout: 1000  # 1 second
```

### Per-Operation Timeouts

```yaml
paths:
  /pet/findByStatus:
    get:
      operationId: findPetsByStatus
      x-speakeasy-timeout: 2000  # 2 seconds
```

### Runtime Timeout Override

**CHOOSE ONE:**

**Option 1: Override timeout globally**

```typescript
// TypeScript
const sdk = new SDK({timeoutMs: 100});
```

```python
# Python
s = SDK(timeout_ms=100)
```

```go
// Go
s := sdk.New(sdk.WithTimeout(100 * time.Millisecond))
```

**Option 2: Override timeout per-request**

```typescript
// TypeScript
await sdk.findPetsByStatus(request, {
  timeoutMs: 1000,
});
```

```python
# Python
res = s.find_pets_by_status(request, timeout_ms=100)
```

```go
// Go
s.FindPetsByStatus(&operations.FindPetsByStatusRequest{},
    operations.WithOperationTimeout(100 * time.Millisecond),
)
```

---

## Pagination Configuration

Configure pagination using the `x-speakeasy-pagination` extension to enable automatic page iteration.

### Offset/Limit Pagination

**Pattern 1: Using page number**

```yaml
/paginated/endpoint:
  get:
    parameters:
      - name: page
        in: query
        schema:
          type: integer
        required: true
    responses:
      "200":
        content:
          application/json:
            schema:
              type: object
              properties:
                resultArray:
                  type: array
                  items:
                    type: integer
    x-speakeasy-pagination:
      type: offsetLimit
      inputs:
        - name: page
          in: parameters
          type: page             # Auto-increments on next()
      outputs:
        results: $.resultArray   # Returns null when empty
```

**Pattern 2: Using offset**

```yaml
x-speakeasy-pagination:
  type: offsetLimit
  inputs:
    - name: offset
      in: parameters
      type: offset           # Increments by results length
    - name: limit
      in: parameters
      type: limit            # Used to determine exhaustion
  outputs:
    results: $.data.resultArray
```

If `limit` is defined, `next()` returns `null` when results length < limit value.

**Pattern 3: Using numPages**

```yaml
x-speakeasy-pagination:
  type: offsetLimit
  inputs:
    - name: page
      in: parameters
      type: page
  outputs:
    numPages: $.data.numPages  # Returns null when page > numPages
```

### Cursor-Based Pagination

```yaml
x-speakeasy-pagination:
  type: cursor
  inputs:
    - name: since
      in: requestBody        # Can also be in parameters
      type: cursor
  outputs:
    nextCursor: $.data.resultArray[-1].created_at  # JSONPath with negative indexing
```

Request body structure:

```json
{
  "since": ""
}
```

Response structure:

```json
{
  "data": {
    "resultArray": [
      {
        "created_at": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

### URL-Based Pagination

```yaml
/paginated/endpoint:
  get:
    responses:
      "200":
        content:
          application/json:
            schema:
              type: object
              properties:
                results:
                  type: array
                  items:
                    type: object
                next:
                  type: string
                  format: uri
    x-speakeasy-pagination:
      type: url
      outputs:
        nextUrl: $.next
```

Response structure:

```json
{
  "results": [{"field": "value"}],
  "next": "http://some_url?page=2"
}
```

### Pagination Input Types

| Type | Description |
|------|-------------|
| `page` | Auto-increments on calling `next()` |
| `offset` | Increments by number of results returned (requires `outputs.results`) |
| `limit` | When provided, `next()` returns null if results < limit |
| `cursor` | Populated with value from `outputs.nextCursor` (required for cursor pagination) |

### Pagination Output Types

| Output | Description |
|--------|-------------|
| `results` | Returns null if array is empty (required by `offset` input) |
| `numPages` | Returns null if page > numPages (requires `page` input) |
| `nextCursor` | Populates cursor input with this value (required by cursor pagination) |

### SDK Usage

```python
response = sdk.paginatedEndpoint(page=1)
while response is not None:
    # Process response
    for item in response.result_array:
        print(item)

    response = response.next()  # Returns None when exhausted
```

---

## Server Configuration

Configure server URLs and dynamic server selection.

### Default Server Selection

The first server in the `servers` array is used as the default:

```yaml
servers:
  - url: https://prod.example.com       # Default
    description: Production environment
  - url: https://sandbox.example.com
    description: Sandbox environment
```

### Declaring Base Server URL

If the OpenAPI document lacks server definitions, set a default in `gen.yaml`:

```yaml
generation:
  baseServerUrl: "https://prod.example.com"
```

### Templated URLs

Use variables in server URLs for dynamic configuration:

```yaml
servers:
  - url: https://{customer}.yourdomain.com
    variables:
      customer:
        default: api
        description: The customer subdomain
```

> **Note:** Templating is only supported for global server URLs, not per-operation servers.

### Server IDs

Define server IDs for better developer experience:

```yaml
servers:
  - url: https://prod.example.com
    description: Production environment
    x-speakeasy-server-id: prod
  - url: https://sandbox.example.com
    description: Sandbox environment
    x-speakeasy-server-id: sandbox
```

### Runtime Server Selection

**CHOOSE ONE:**

**Option 1: Select by index**

```typescript
// TypeScript
const sdk = new SDK({ serverIdx: 1 });
```

```python
# Python
s = SDK(server_idx=1)
```

```go
// Go
s := sdk.New(sdk.WithServerIndex(1))
```

**Option 2: Select by URL**

```typescript
// TypeScript
const sdk = new SDK({
  // Without x-speakeasy-server-id
  serverURL: "https://sandbox.example.com",

  // With x-speakeasy-server-id
  server: "sandbox",
});
```

```python
# Python
s = SDK(
    # Without x-speakeasy-server-id
    server_url="https://sandbox.example.com",

    # With x-speakeasy-server-id
    server="sandbox"
)
```

```go
// Go
s := sdk.New(
    // Without x-speakeasy-server-id
    sdk.WithServerURL("https://sandbox.example.com"),

    // With x-speakeasy-server-id
    sdk.WithServer("sandbox"),
)
```

**Option 3: Override per-operation**

```typescript
// TypeScript
await sdk.tag1.listTest1(operationSecurity, page, headerParam1, queryParam1, {
  serverURL: "https://sandbox.example.com",
});
```

```python
# Python
res = s.tag1.list_test1(
    "API_KEY",
    server_url="https://sandbox.example.com",
    page=100,
    header_param1='header value',
    query_param1='query value'
)
```

```go
// Go
res, err := s.Tag1.ListTest1(
    ctx,
    operationSecurity,
    sdk.WithServerURL("https://sandbox.example.com"),
    page,
    headerParam1,
    queryParam1,
)
```

> **Warning:** If using relative paths in the OpenAPI document, account for the baseURL when configuring server URLs at runtime.

---

## Custom HTTP Clients

Provide custom HTTP clients for proxies, custom telemetry, additional headers, or preconfigured options.

### TypeScript Custom HTTP Client

```typescript
import { SDK } from "openapi";
import { HTTPClient } from "openapi/dist/commonjs/lib/http";

// Create HTTPClient with custom fetcher
const httpClient = new HTTPClient({
  fetcher: async (request) => fetch(request),
});

// Add request lifecycle hooks
httpClient.addHook("requestError", (err) => {
  console.log(`Request failed: ${err}`);
});

// Initialize SDK with custom client
const sdk = new SDK({ httpClient });
```

### Python Custom HTTP Client

```python
import requests
from sdk import SDK, HttpClient

class RequestsHttpClient(HttpClient):
    def __init__(self):
        self.session = requests.Session()

    def send(self, request, **kwargs):
        return self.session.send(request.prepare())

    def build_request(
        self,
        method,
        url,
        *,
        content=None,
        headers=None,
        **kwargs,
    ):
        return requests.Request(
            method=method,
            url=url,
            data=content,
            headers=headers,
        )

# Initialize SDK with custom client
client = RequestsHttpClient()
sdk = SDK(client=client)
```

### Go Custom HTTP Client

```go
/* The Go SDK accepts any client that implements a
   Do(*http.Request) (*http.Response, error) method */

// Custom HTTP client with caching
c := NewCachedClient(&http.Client{}, cache)

opts := []sdk.SDKOption{
    sdk.WithClient(c),
}

s := sdk.New(opts)
```

### Java Custom HTTP Client

```java
/* Java SDK accepts clients implementing the HTTPClient interface */

// Custom HTTP client
YourHttpClient client = new YourHttpClient();

SDK.Builder builder = SDK.builder();
builder.setClient(client);

SDK sdk = builder.build();
```

### C# Custom HTTP Client

```csharp
/* Custom client must implement ISpeakeasyHttpClient */

var httpClient = new YourHttpClient();
var sdk = new SDK(client: httpClient);
```

---

## Best Practices

1. **Retry configuration**: Start conservative (3-5 retries, exponential backoff) and tune based on API behavior
2. **Timeouts**: Set realistic timeouts based on typical API response times; consider long-running operations
3. **Pagination**: Use `cursor` pagination for real-time data, `offsetLimit` for stable datasets
4. **Server selection**: Use `x-speakeasy-server-id` for clearer SDK API
5. **Custom HTTP clients**: Implement for cross-cutting concerns like auth, logging, metrics
6. **Idempotency**: Always include idempotency headers for retry-safe operations
7. **Status codes**: Be specific with status codes to retry (avoid blanket `4XX` retries)

---

## Pre-defined TODO List

When configuring SDK runtime behavior, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Configure global retry strategy in OpenAPI | Configuring global retries |
| 2 | Configure per-operation retries if needed | Configuring per-operation retries |
| 3 | Configure global and per-operation timeouts | Configuring timeouts |
| 4 | Configure pagination for list endpoints | Configuring pagination |
| 5 | Define server URLs and IDs | Defining server configuration |
| 6 | Test retry behavior with failing endpoints | Testing retry behavior |
| 7 | Test timeout behavior with slow endpoints | Testing timeout behavior |
| 8 | Test pagination with multi-page results | Testing pagination |
| 9 | Document runtime configuration options in README | Documenting runtime configuration |

**Usage:**
```
TodoWrite([
  {content: "Configure global retry strategy in OpenAPI", status: "pending", activeForm: "Configuring global retries"},
  {content: "Configure per-operation retries if needed", status: "pending", activeForm: "Configuring per-operation retries"},
  {content: "Configure global and per-operation timeouts", status: "pending", activeForm: "Configuring timeouts"},
  {content: "Configure pagination for list endpoints", status: "pending", activeForm: "Configuring pagination"},
  {content: "Define server URLs and IDs", status: "pending", activeForm: "Defining server configuration"},
  {content: "Test retry behavior with failing endpoints", status: "pending", activeForm: "Testing retry behavior"},
  {content: "Test timeout behavior with slow endpoints", status: "pending", activeForm: "Testing timeout behavior"},
  {content: "Test pagination with multi-page results", status: "pending", activeForm: "Testing pagination"},
  {content: "Document runtime configuration options in README", status: "pending", activeForm: "Documenting runtime configuration"}
])
```
