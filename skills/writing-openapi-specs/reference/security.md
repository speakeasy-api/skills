# Security

Best practices for defining authentication and authorization in OpenAPI specifications.

## Security Schemes

Define security schemes in `components/securitySchemes`, then apply them globally or per-operation.

### API Key Authentication

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: |
        API key authentication. Include your API key in the `X-API-Key` header.

        Example: `X-API-Key: your-api-key-here`

# Apply globally
security:
  - ApiKeyAuth: []

# Or per-operation
paths:
  /users:
    get:
      security:
        - ApiKeyAuth: []
```

**API Key Locations**:

```yaml
# Header (most common)
ApiKeyHeader:
  type: apiKey
  in: header
  name: X-API-Key

# Query parameter (less secure, avoid for sensitive operations)
ApiKeyQuery:
  type: apiKey
  in: query
  name: api_key

# Cookie
ApiKeyCookie:
  type: apiKey
  in: cookie
  name: api_key
```

### HTTP Bearer Token (JWT)

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT bearer token authentication.

        Include the token in the Authorization header:
        `Authorization: Bearer <token>`

security:
  - BearerAuth: []
```

### HTTP Basic Authentication

```yaml
components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
      description: |
        HTTP Basic authentication using username and password.

        Credentials are base64-encoded: `Authorization: Basic <base64(username:password)>`

# Apply to specific operation
paths:
  /login:
    post:
      security:
        - BasicAuth: []
```

### OAuth 2.0

#### Authorization Code Flow

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      description: OAuth 2.0 authorization code flow
      flows:
        authorizationCode:
          authorizationUrl: https://api.example.com/oauth/authorize
          tokenUrl: https://api.example.com/oauth/token
          refreshUrl: https://api.example.com/oauth/refresh
          scopes:
            read: Read access to resources
            write: Write access to resources
            admin: Administrative access
            users:read: Read user information
            users:write: Modify user information
            orders:read: Read order information
            orders:write: Create and modify orders

# Apply with specific scopes
security:
  - OAuth2:
      - read
      - write

# Per-operation with different scopes
paths:
  /users:
    get:
      security:
        - OAuth2: [users:read]

    post:
      security:
        - OAuth2: [users:write]

  /admin:
    get:
      security:
        - OAuth2: [admin]
```

#### Client Credentials Flow

For service-to-service authentication:

```yaml
components:
  securitySchemes:
    OAuth2ClientCredentials:
      type: oauth2
      description: OAuth 2.0 client credentials flow for service accounts
      flows:
        clientCredentials:
          tokenUrl: https://api.example.com/oauth/token
          scopes:
            api:read: Read API resources
            api:write: Modify API resources

security:
  - OAuth2ClientCredentials: [api:read, api:write]
```

#### Implicit Flow

```yaml
components:
  securitySchemes:
    OAuth2Implicit:
      type: oauth2
      description: OAuth 2.0 implicit flow (use with caution)
      flows:
        implicit:
          authorizationUrl: https://api.example.com/oauth/authorize
          scopes:
            read: Read access
            write: Write access
```

**Note**: Implicit flow is less secure. Prefer authorization code flow with PKCE.

#### Password Flow

```yaml
components:
  securitySchemes:
    OAuth2Password:
      type: oauth2
      description: OAuth 2.0 resource owner password flow
      flows:
        password:
          tokenUrl: https://api.example.com/oauth/token
          refreshUrl: https://api.example.com/oauth/refresh
          scopes:
            read: Read access
            write: Write access
```

**Note**: Password flow is less secure. Use only for trusted first-party clients.

### OpenID Connect

```yaml
components:
  securitySchemes:
    OpenIdConnect:
      type: openIdConnect
      description: OpenID Connect authentication
      openIdConnectUrl: https://api.example.com/.well-known/openid-configuration

security:
  - OpenIdConnect: []
```

## Applying Security

### Global Security

Apply to all operations:

```yaml
security:
  - BearerAuth: []

paths:
  /users:
    get:
      # Inherits global security
    post:
      # Inherits global security
```

### Per-Operation Security

Override global security for specific operations:

```yaml
security:
  - BearerAuth: []

paths:
  /public:
    get:
      security: []  # Public endpoint, no authentication

  /admin:
    get:
      security:
        - BearerAuth: []
        - OAuth2: [admin]
      # Requires both BearerAuth AND OAuth2 with admin scope
```

### Multiple Security Options (OR)

Allow multiple authentication methods:

```yaml
paths:
  /users:
    get:
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      # Client can use BearerAuth OR ApiKeyAuth
```

### Combined Security Requirements (AND)

Require multiple authentication methods simultaneously:

```yaml
paths:
  /sensitive:
    post:
      security:
        - BearerAuth: []
          ApiKeyAuth: []
      # Client must provide BOTH BearerAuth AND ApiKeyAuth
```

## OAuth Scopes

### Scope Naming Conventions

Use **colon-separated** hierarchy:

```yaml
scopes:
  # Resource:action pattern
  users:read: Read user information
  users:write: Create and modify users
  users:delete: Delete users

  orders:read: Read order information
  orders:write: Create and modify orders
  orders:delete: Cancel orders

  admin: Full administrative access

  # Granular permissions
  users:profile:read: Read user profiles
  users:profile:write: Update user profiles
  users:settings:read: Read user settings
  users:settings:write: Update user settings
```

### Scope Granularity

**Coarse-grained** (simple APIs):
```yaml
scopes:
  read: Read access to all resources
  write: Write access to all resources
  admin: Full administrative access
```

**Fine-grained** (complex APIs):
```yaml
scopes:
  users:read: Read users
  users:write: Modify users
  orders:read: Read orders
  orders:write: Modify orders
  billing:read: Read billing info
  billing:write: Modify billing
  reports:generate: Generate reports
  webhooks:manage: Manage webhooks
```

**Choose granularity based on**:
- API complexity
- Security requirements
- Client use cases
- Maintenance overhead

### Per-Operation Scopes

Apply specific scopes to operations:

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.example.com/oauth/authorize
          tokenUrl: https://api.example.com/oauth/token
          scopes:
            users:read: Read user information
            users:write: Modify users
            users:delete: Delete users

paths:
  /users:
    get:
      security:
        - OAuth2: [users:read]

    post:
      security:
        - OAuth2: [users:write]

  /users/{id}:
    get:
      security:
        - OAuth2: [users:read]

    put:
      security:
        - OAuth2: [users:write]

    delete:
      security:
        - OAuth2: [users:delete]
```

## Public vs Protected Endpoints

### Public Endpoints

```yaml
security:
  - BearerAuth: []  # Global default

paths:
  /health:
    get:
      security: []  # Override: no authentication required
      operationId: health_check
      summary: Health check endpoint
      description: Public endpoint to check API availability

  /docs:
    get:
      security: []  # Public documentation
      operationId: api_docs
```

### Mixed Security Levels

```yaml
paths:
  /users:
    get:
      security: []  # Public - list users
      description: Public directory of users

  /users/{id}:
    get:
      security:
        - BearerAuth: []  # Protected - view full profile
      description: View detailed user profile (authentication required)

    put:
      security:
        - OAuth2: [users:write]  # Protected with specific scope
      description: Update user profile (requires users:write scope)
```

## Security Best Practices

### Do

**Document security clearly**:
```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT bearer token authentication.

        **Obtaining a token:**
        1. Make a POST request to `/auth/login` with credentials
        2. Include the returned token in subsequent requests

        **Token format:**
        ```
        Authorization: Bearer <your-jwt-token>
        ```

        **Token expiration:**
        Tokens expire after 1 hour. Use the refresh token to obtain a new access token.

        **Required claims:**
        - `sub`: User ID
        - `exp`: Expiration timestamp
        - `scope`: Space-separated list of scopes
```

**Use appropriate security for operation sensitivity**:
```yaml
paths:
  /public-data:
    get:
      security: []  # Public

  /user-data:
    get:
      security:
        - BearerAuth: []  # Basic authentication

  /admin:
    post:
      security:
        - OAuth2: [admin]  # Strict permissions
```

**Document permission requirements**:
```yaml
paths:
  /users/{id}:
    put:
      summary: Update user
      description: |
        Update user information.

        **Permissions:**
        - Users can update their own profile (user:self)
        - Admins can update any profile (admin)
      security:
        - OAuth2: [users:write]
```

**Specify security responses**:
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
          description: Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: "Missing or invalid authentication token"
        '403':
          description: Insufficient permissions
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: "You don't have permission to access this resource"
```

### Avoid

**API keys in query parameters** (for sensitive operations):
```yaml
# ❌ Avoid for sensitive operations
ApiKeyQuery:
  type: apiKey
  in: query
  name: api_key
# Query params are logged in server logs, browser history, etc.

# ✓ Prefer headers
ApiKeyHeader:
  type: apiKey
  in: header
  name: X-API-Key
```

**Vague scope descriptions**:
```yaml
# ❌ Not helpful
scopes:
  read: Read stuff
  write: Write stuff

# ✓ Specific
scopes:
  users:read: Read user profiles and settings
  users:write: Create and modify user accounts
```

**Forgetting to document security**:
```yaml
# ❌ No description
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer

# ✓ Clear documentation
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT bearer token. Obtain from /auth/login endpoint.
        Include in Authorization header: Bearer <token>
```

**Not specifying 401/403 responses**:
```yaml
# ❌ Missing auth error responses
paths:
  /protected:
    get:
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Success
        # Missing 401, 403

# ✓ Complete responses
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
        '403':
          $ref: '#/components/responses/Forbidden'
```

## Common Patterns

### Token Refresh

Document token refresh flow:

```yaml
paths:
  /auth/login:
    post:
      summary: Authenticate user
      security: []  # No auth required for login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email: {type: string, format: email}
                password: {type: string, format: password}
      responses:
        '200':
          description: Authentication successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    description: JWT access token (expires in 1 hour)
                  refresh_token:
                    type: string
                    description: Refresh token (expires in 30 days)
                  expires_in:
                    type: integer
                    description: Token expiration in seconds

  /auth/refresh:
    post:
      summary: Refresh access token
      security: []  # Uses refresh token in body, not header
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [refresh_token]
              properties:
                refresh_token:
                  type: string
      responses:
        '200':
          description: Token refreshed
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token: {type: string}
                  expires_in: {type: integer}
```

### Multiple Authentication Methods

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      description: JWT for user authentication

    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for service authentication

# Global: require one of the two
security:
  - BearerAuth: []
  - ApiKeyAuth: []

paths:
  /users:
    get:
      # Accepts either BearerAuth or ApiKeyAuth
      description: |
        Retrieve users.

        **Authentication:**
        - User authentication: JWT bearer token
        - Service authentication: API key
```

### Permission Levels

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.example.com/oauth/authorize
          tokenUrl: https://api.example.com/oauth/token
          scopes:
            # Read-only access
            read: Read-only access to non-sensitive data

            # Standard user access
            user: Standard user access
            user:profile: Manage own profile
            user:orders: Manage own orders

            # Manager access
            manager: Manager-level access
            manager:reports: View team reports
            manager:approvals: Approve team requests

            # Admin access
            admin: Full administrative access
            admin:users: Manage all users
            admin:settings: Modify system settings

paths:
  /profile:
    get:
      security:
        - OAuth2: [user:profile]

  /admin/users:
    get:
      security:
        - OAuth2: [admin:users]
```

## Summary Checklist

For security:

- [ ] Security schemes defined in `components/securitySchemes`
- [ ] Appropriate scheme types chosen (apiKey, http, oauth2, openIdConnect)
- [ ] Clear descriptions for each scheme
- [ ] Global security applied (if appropriate)
- [ ] Per-operation security for special cases
- [ ] Public endpoints explicitly marked with `security: []`
- [ ] OAuth scopes clearly defined and documented
- [ ] Scope naming follows consistent convention
- [ ] 401/403 responses documented for protected endpoints
- [ ] Token refresh documented (if applicable)
- [ ] Authentication instructions included
- [ ] Multiple auth methods documented (if applicable)

## Advanced Patterns

### Rate Limiting (Via Extensions)

Document rate limiting in security context:

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: |
        API key authentication.

        **Rate Limits:**
        - 100 requests per minute per API key
        - 1000 requests per hour per API key

        Rate limit headers are included in responses:
        - `X-RateLimit-Limit`: Total requests allowed
        - `X-RateLimit-Remaining`: Requests remaining
        - `X-RateLimit-Reset`: Unix timestamp when limit resets

        When rate limit is exceeded, you'll receive a 429 response
        with a `Retry-After` header indicating seconds to wait.
```

### API Key + IP Allowlist

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: |
        API key authentication with IP allowlisting.

        **Security:**
        - API key must be valid
        - Request must originate from allowlisted IP address

        Configure IP allowlist in account settings.
```

### Mutual TLS

Document mTLS requirements:

```yaml
components:
  securitySchemes:
    MutualTLS:
      type: mutualTLS
      description: |
        Mutual TLS authentication using client certificates.

        **Requirements:**
        1. Valid client certificate issued by our CA
        2. Certificate must not be expired or revoked
        3. Certificate subject must match registered account

        **Setup:**
        1. Request client certificate from support
        2. Install certificate in your HTTP client
        3. Make requests to https://api.example.com

security:
  - MutualTLS: []
```
