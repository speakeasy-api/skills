---
short_description: Authentication and authorization in OpenAPI
long_description: Security schemes define authentication methods including API keys, HTTP auth (Basic, Bearer), OAuth2, and OpenID Connect. Apply globally or per-operation.
source:
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/openapi/security/*.mdx"
    ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
    last_reconciled: "2025-12-11"
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/openapi/security/security-schemes/security-api-key.mdx,security-http.mdx"
    ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
    last_reconciled: "2025-12-11"
    notes: "Added detailed API key patterns, multiple key authentication, Digest auth, and error response documentation"
---

# Security Schemes in OpenAPI

Security schemes define how clients authenticate with the API.

## Security Scheme Types

OpenAPI supports these authentication methods:

- **apiKey** - API key in header, query, or cookie
- **http** - HTTP authentication (Basic, Bearer, Digest)
- **oauth2** - OAuth 2.0 flows
- **openIdConnect** - OpenID Connect Discovery

## Defining Security Schemes

Security schemes are defined in `components/securitySchemes`:

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          scopes:
            read: Read access
            write: Write access

    OpenID:
      type: openIdConnect
      openIdConnectUrl: https://example.com/.well-known/openid-configuration
```

## Applying Security

### Global Security

Apply to all operations:

```yaml
security:
  - ApiKeyAuth: []
```

### Per-Operation Security

```yaml
paths:
  /public:
    get:
      summary: Public endpoint
      security: []  # Override global - no auth required

  /protected:
    get:
      summary: Protected endpoint
      security:
        - BearerAuth: []
```

### Multiple Schemes (OR)

Client can use any of these:

```yaml
security:
  - ApiKeyAuth: []
  - BearerAuth: []
```

### Multiple Schemes (AND)

Client must provide both:

```yaml
security:
  - ApiKeyAuth: []
    BearerAuth: []
```

## API Key Authentication

API keys are the most common authentication method for machine-to-machine APIs. They support passing a pre-shared secret via header, cookie, or query parameter.

> **Security Note:** Pass API keys via headers or cookies rather than query parameters. Query parameters are often logged by servers and intermediaries, increasing the risk of exposure.

### Header (Recommended)

```yaml
components:
  securitySchemes:
    ApiKeyHeader:
      type: apiKey
      in: header
      name: X-API-Key
      description: |
        API key for authentication. Obtain your API key from the developer portal.
        Contact support@example.com to request access.
```

Usage:

```http
GET /api/resource
X-API-Key: your-api-key-here
```

### Query Parameter (Not Recommended)

```yaml
components:
  securitySchemes:
    ApiKeyQuery:
      type: apiKey
      in: query
      name: api_key
      description: |
        **Warning:** Passing API keys in query parameters is less secure
        as they may be logged. Use header-based authentication instead.
```

Usage:

```http
GET /api/resource?api_key=your-api-key-here
```

### Cookie

```yaml
components:
  securitySchemes:
    ApiKeyCookie:
      type: apiKey
      in: cookie
      name: api_key
      description: API key passed via cookie
```

### Multiple API Keys

Some APIs require multiple keys simultaneously (e.g., app ID + app key):

```yaml
security:
  - AppId: []
    AppKey: []  # No leading dash = AND relationship

components:
  securitySchemes:
    AppId:
      type: apiKey
      name: X-App-Id
      in: header
      description: Application identifier
    AppKey:
      type: apiKey
      name: X-App-Key
      in: header
      description: Application secret key
```

Both keys must be provided in the same request.

## HTTP Authentication

### Basic Auth

```yaml
components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
      description: Basic HTTP authentication
```

Usage:

```http
GET /api/resource
Authorization: Basic base64(username:password)
```

### Bearer Token (JWT)

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT bearer token authentication
```

Usage:

```http
GET /api/resource
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Digest Auth

Digest authentication is more secure than Basic auth, using a challenge-response mechanism with hashed credentials:

```yaml
components:
  securitySchemes:
    DigestAuth:
      type: http
      scheme: digest
      description: |
        HTTP Digest authentication provides better security than Basic auth
        by hashing credentials with a server-provided nonce.
```

Example request:

```http
GET /api/resource
Authorization: Digest username="user",
  realm="example",
  nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
  uri="/api/resource",
  response="6629fae49393a05397450978507c4ef1"
```

## OAuth 2.0

### Authorization Code Flow

```yaml
components:
  securitySchemes:
    OAuth2AuthCode:
      type: oauth2
      description: OAuth 2.0 authorization code flow
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          refreshUrl: https://example.com/oauth/refresh
          scopes:
            read:users: Read user data
            write:users: Modify user data
            admin: Administrative access
```

### Client Credentials Flow

```yaml
components:
  securitySchemes:
    OAuth2ClientCreds:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://example.com/oauth/token
          scopes:
            api:read: Read API access
            api:write: Write API access
```

### Implicit Flow

```yaml
components:
  securitySchemes:
    OAuth2Implicit:
      type: oauth2
      flows:
        implicit:
          authorizationUrl: https://example.com/oauth/authorize
          scopes:
            read: Read access
            write: Write access
```

### Password Flow

```yaml
components:
  securitySchemes:
    OAuth2Password:
      type: oauth2
      flows:
        password:
          tokenUrl: https://example.com/oauth/token
          scopes:
            read: Read access
            write: Write access
```

### Using OAuth Scopes

```yaml
paths:
  /users:
    get:
      security:
        - OAuth2AuthCode:
          - read:users
    post:
      security:
        - OAuth2AuthCode:
          - write:users
    delete:
      security:
        - OAuth2AuthCode:
          - admin
```

## OpenID Connect

```yaml
components:
  securitySchemes:
    OpenID:
      type: openIdConnect
      openIdConnectUrl: https://example.com/.well-known/openid-configuration
      description: OpenID Connect authentication

security:
  - OpenID:
    - openid
    - profile
    - email
```

## Multiple Auth Methods

Allow clients to choose:

```yaml
components:
  securitySchemes:
    ApiKey:
      type: apiKey
      in: header
      name: X-API-Key

    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - ApiKey: []      # OR
  - BearerAuth: []  # This one
```

Require multiple methods:

```yaml
security:
  - ApiKey: []      # AND
    BearerAuth: []  # This one
```

## Security Responses

Document authentication and authorization failures to help SDK users understand error conditions:

### 401 Unauthorized Response

Returned when authentication credentials are missing or invalid:

```yaml
paths:
  /protected:
    get:
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Success
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  responses:
    Unauthorized:
      description: Unauthorized - Missing or invalid authentication credentials
      headers:
        WWW-Authenticate:
          description: Authentication scheme and realm
          schema:
            type: string
          example: 'Bearer realm="api"'
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
```

### 403 Forbidden Response

Returned when credentials are valid but lack necessary permissions:

```yaml
components:
  responses:
    Forbidden:
      description: Forbidden - Valid credentials but insufficient permissions
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
                example: insufficient_permissions
              message:
                type: string
                example: User does not have permission to access this resource
              required_scopes:
                type: array
                items:
                  type: string
                example: ["admin", "write:users"]
```

**Reuse across operations:**

```yaml
paths:
  /users:
    get:
      responses:
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
    post:
      responses:
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
```

## Common Patterns

### API Key + Optional Bearer

```yaml
security:
  - ApiKey: []

paths:
  /public:
    get:
      security: []  # No auth

  /protected:
    get:
      security:
        - BearerAuth: []  # Override with Bearer
```

### Different Auth Per Environment

Use overlays or server variables:

```yaml
servers:
  - url: https://dev.example.com
    description: Development (API key)
  - url: https://api.example.com
    description: Production (OAuth2)

components:
  securitySchemes:
    DevAuth:
      type: apiKey
      in: header
      name: X-Dev-Key
    ProdAuth:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          scopes:
            api: API access
```

## Best Practices

1. Use Bearer JWT for modern APIs
2. Document required scopes clearly
3. Always define 401/403 responses for protected endpoints
4. Use HTTPS for all authenticated endpoints
5. Prefer `bearer` over custom header names
6. Document token format in `description`
7. Use OAuth2 for third-party integrations
8. Consider API key for internal/service-to-service calls
9. Never document actual credentials in examples
10. Use `openIdConnect` when available for better client support

## Security Extensions

### Speakeasy Auth Examples

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      x-speakeasy-example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Validation

```bash
speakeasy validate openapi -s spec.yaml
```

## Reference

- OpenAPI Security: https://spec.openapis.org/oas/latest.html#security-scheme-object
- OAuth 2.0: https://oauth.net/2/
- OpenID Connect: https://openid.net/connect/

---

## Pre-defined TODO List

When configuring security schemes in OpenAPI, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Identify required authentication mechanisms | Identifying authentication mechanisms |
| 2 | Add securitySchemes to components section | Adding securitySchemes to components |
| 3 | Configure HTTP authentication (Basic or Bearer) | Configuring HTTP authentication |
| 4 | Add API key schemes if needed | Adding API key schemes |
| 5 | Apply security requirements globally or per-operation | Applying security requirements |
| 6 | Validate security configuration | Validating security configuration |

**Usage:**
```
TodoWrite([
  {content: "Identify required authentication mechanisms", status: "pending", activeForm: "Identifying authentication mechanisms"},
  {content: "Add securitySchemes to components section", status: "pending", activeForm: "Adding securitySchemes to components"},
  {content: "Configure HTTP authentication (Basic or Bearer)", status: "pending", activeForm: "Configuring HTTP authentication"},
  {content: "Add API key schemes if needed", status: "pending", activeForm: "Adding API key schemes"},
  {content: "Apply security requirements globally or per-operation", status: "pending", activeForm: "Applying security requirements"},
  {content: "Validate security configuration", status: "pending", activeForm: "Validating security configuration"}
])
```

