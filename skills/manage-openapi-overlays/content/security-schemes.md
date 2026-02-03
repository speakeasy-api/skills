# Security Schemes Configuration

Configure authentication methods in OpenAPI for SDK generation.

## Security Scheme Types

| Type | Use Case |
|------|----------|
| `apiKey` | API key in header, query, or cookie |
| `http` | Basic, Bearer, or Digest authentication |
| `oauth2` | OAuth 2.0 flows |
| `openIdConnect` | OpenID Connect Discovery |

## API Key Authentication

### Header (Recommended)

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key from developer portal
```

### Query Parameter (Less Secure)

```yaml
components:
  securitySchemes:
    ApiKeyQuery:
      type: apiKey
      in: query
      name: api_key
```

> **Warning:** Query parameters may be logged. Prefer header-based auth.

### Multiple API Keys (AND)

Some APIs require multiple keys:

```yaml
security:
  - AppId: []
    AppKey: []  # No dash = AND relationship

components:
  securitySchemes:
    AppId:
      type: apiKey
      name: X-App-Id
      in: header
    AppKey:
      type: apiKey
      name: X-App-Key
      in: header
```

## HTTP Authentication

### Bearer Token (JWT)

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### Basic Auth

```yaml
components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
```

## OAuth 2.0

### Authorization Code Flow

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          scopes:
            read: Read access
            write: Write access
            admin: Admin access
```

### Client Credentials Flow

```yaml
components:
  securitySchemes:
    OAuth2ClientCredentials:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://example.com/oauth/token
          scopes:
            api: API access
```

## Applying Security

### Global (All Operations)

```yaml
# At document root
security:
  - ApiKeyAuth: []
```

### Per-Operation Override

```yaml
paths:
  /public:
    get:
      security: []  # No auth required

  /admin:
    get:
      security:
        - BearerAuth: []
        - OAuth2: [admin]  # Requires admin scope
```

### Multiple Options (OR)

Client can use any:

```yaml
security:
  - ApiKeyAuth: []
  - BearerAuth: []
```

### Multiple Required (AND)

Client must provide both:

```yaml
security:
  - ApiKeyAuth: []
    SessionToken: []
```

## Custom Security via Overlay

### Add Security Scheme

```yaml
overlay: 1.0.0
info:
  title: Add Security
  version: 1.0.0
actions:
  - target: $.components
    update:
      securitySchemes:
        ApiKeyAuth:
          type: apiKey
          in: header
          name: X-API-Key

  - target: $
    update:
      security:
        - ApiKeyAuth: []
```

### Multi-Part Custom Auth (HMAC)

For complex authentication patterns:

```yaml
actions:
  - target: $.components
    update:
      securitySchemes:
        HmacAuth:
          type: http
          scheme: custom
          x-speakeasy-custom-security-scheme:
            schema:
              type: object
              properties:
                accessKey:
                  type: string
                secretKey:
                  type: string
```

With `envVarPrefix: MYAPI` in gen.yaml, generates:
- `MYAPI_ACCESS_KEY`
- `MYAPI_SECRET_KEY`

### Override Per-Operation

```yaml
actions:
  - target: "$.paths['/admin'].get"
    update:
      security:
        - AdminAuth: []
```

### Make Endpoint Public

```yaml
actions:
  - target: "$.paths['/health'].get"
    update:
      security: []
```

## SDK Security Configuration

Generated SDKs support security at instantiation:

**TypeScript:**
```typescript
const sdk = new SDK({
  apiKey: process.env.API_KEY,
});
```

**Python:**
```python
sdk = SDK(api_key=os.environ["API_KEY"])
```

**Go:**
```go
sdk := SDK.New(
    SDK.WithSecurity(shared.Security{
        APIKey: os.Getenv("API_KEY"),
    }),
)
```

## Environment Variables

Configure automatic env var mapping in gen.yaml:

```yaml
<language>:
  envVarPrefix: "MYAPI"
```

This maps:
- `MYAPI_API_KEY` → API key
- `MYAPI_BEARER_AUTH` → Bearer token
- `MYAPI_USERNAME` / `MYAPI_PASSWORD` → Basic auth
