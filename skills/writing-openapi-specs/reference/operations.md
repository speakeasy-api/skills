# Operations

Best practices for defining API operations (endpoints and HTTP methods) in OpenAPI.

## Operation Basics

An operation describes a single API endpoint with a specific HTTP method:

```yaml
paths:
  /users/{id}:
    get:           # Operation
      operationId: users_get
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema: {type: integer}
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

## Operation IDs

**Always define `operationId`** for every operation. This is critical for SDK generation and tooling.

### Naming Pattern

Use **lowercase with underscores** following the `resource_action` pattern:

```yaml
# Good - clear resource_action pattern
paths:
  /users:
    get:
      operationId: users_list
    post:
      operationId: users_create

  /users/{id}:
    get:
      operationId: users_get
    put:
      operationId: users_update
    patch:
      operationId: users_patch
    delete:
      operationId: users_delete

  /users/{id}/avatar:
    put:
      operationId: users_upload_avatar
    delete:
      operationId: users_delete_avatar
```

### Common Action Verbs

| Action | Use For | Example |
|--------|---------|---------|
| `list` | GET collection (multiple items) | `users_list` |
| `get` | GET single item | `users_get` |
| `create` | POST new item | `users_create` |
| `update` | PUT (full replacement) | `users_update` |
| `patch` | PATCH (partial update) | `users_patch` |
| `delete` | DELETE item | `users_delete` |
| `search` | POST with search criteria | `users_search` |
| `upload` | POST/PUT file | `users_upload_avatar` |
| `download` | GET file/export | `reports_download` |

### Avoid

```yaml
# Avoid - auto-generated style
operationId: GetApiV1Users

# Avoid - camelCase without resource
operationId: listUsers

# Avoid - vague names
operationId: doStuff
operationId: handleRequest
```

### SDK Generation Context

Operation IDs directly affect generated SDK method names. With Speakeasy extensions:

```yaml
paths:
  /users:
    get:
      operationId: users_list
      x-speakeasy-group: users
      # Generates: sdk.users.list()

  /orders/{id}:
    get:
      operationId: orders_get
      x-speakeasy-group: orders
      # Generates: sdk.orders.get(id)
```

## HTTP Methods

Use HTTP methods according to their semantic meaning:

### GET - Retrieve Resources

```yaml
paths:
  /users:
    get:
      operationId: users_list
      summary: List all users
      # GET should be idempotent and safe (no side effects)

  /users/{id}:
    get:
      operationId: users_get
      summary: Get a specific user
```

**Characteristics**:
- Safe (no modifications)
- Idempotent (multiple calls have same effect)
- Cacheable
- No request body

### POST - Create or Complex Operations

```yaml
paths:
  /users:
    post:
      operationId: users_create
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'

  /users/search:
    post:
      operationId: users_search
      summary: Search users with complex criteria
      # POST for search when criteria are too complex for query params
```

**Characteristics**:
- Creates new resources
- Not idempotent (multiple calls create multiple resources)
- Can include request body
- Use for operations that don't fit other methods

### PUT - Full Replacement

```yaml
paths:
  /users/{id}:
    put:
      operationId: users_update
      summary: Replace user (full update)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      # Client must send complete representation
```

**Characteristics**:
- Replaces entire resource
- Idempotent (multiple calls have same effect)
- Client sends complete representation
- Unspecified fields are removed/reset

### PATCH - Partial Update

```yaml
paths:
  /users/{id}:
    patch:
      operationId: users_patch
      summary: Partially update user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name: {type: string}
                email: {type: string}
              # Only include fields being updated
```

**Characteristics**:
- Updates specific fields
- May or may not be idempotent
- Client sends only changed fields
- Unspecified fields remain unchanged

### DELETE - Remove Resources

```yaml
paths:
  /users/{id}:
    delete:
      operationId: users_delete
      summary: Delete a user
      responses:
        '204':
          description: Successfully deleted
        '404':
          description: User not found
```

**Characteristics**:
- Removes resources
- Idempotent (deleting twice has same effect as once)
- Typically no request body
- Common responses: 204 (No Content), 200 (with details), 404 (Not Found)

### Method Selection Guide

| Goal | Method | Idempotent? | Request Body? |
|------|--------|-------------|---------------|
| Retrieve resource(s) | GET | Yes | No |
| Create resource | POST | No | Yes |
| Replace resource | PUT | Yes | Yes |
| Update specific fields | PATCH | Maybe | Yes |
| Remove resource | DELETE | Yes | Optional |
| Complex search | POST | Yes | Yes |

## Summaries and Descriptions

### Summary

Short, concise description shown in documentation navigation:

```yaml
get:
  summary: List all users
  # Keep under 50 characters for best display
```

### Description

Detailed information using CommonMark syntax:

```yaml
get:
  summary: List all users
  description: |
    Returns a paginated list of all active users in the system.

    ## Pagination
    Use `limit` and `offset` parameters to paginate results.

    ## Filtering
    Filter by `role` to retrieve users with specific permissions.

    ## Rate Limits
    - 100 requests per minute per API key
    - 1000 requests per hour per IP address

    ## Example
    ```
    GET /users?limit=20&offset=40&role=admin
    ```
```

**Summary Best Practices**:
- Use imperative form: "Get user", "Create order", "Delete resource"
- Be specific but brief
- Avoid redundancy with operationId

**Description Best Practices**:
- Explain important behaviors not obvious from schema
- Document rate limits, permissions, side effects
- Use CommonMark for formatting (headers, lists, code blocks)
- Include usage examples for complex operations

## Tags

Tags group operations in documentation and SDK generation.

### Basic Tags

```yaml
paths:
  /users:
    get:
      tags: [user-management]
      operationId: users_list

  /users/{id}:
    get:
      tags: [user-management]
      operationId: users_get

  /orders:
    get:
      tags: [order-processing]
      operationId: orders_list
```

### Tag Definitions

Define tags at the root level for richer documentation:

```yaml
tags:
  - name: user-management
    description: |
      Operations for managing user accounts, including creation, retrieval,
      updates, and deletion. Requires `users:read` or `users:write` permissions.
    externalDocs:
      description: User Management Guide
      url: https://docs.example.com/users

  - name: order-processing
    description: Operations for processing customer orders
```

### Tag Naming

**Convention**: Use **lowercase with hyphens**:

```yaml
# Good
tags: [user-management, order-processing, payment-methods]

# Avoid
tags: [UserManagement, order_processing, PaymentMethods]
```

**Rationale**: Machine-friendly, URL-safe, consistent with REST conventions.

### Multiple Tags

Operations can have multiple tags:

```yaml
paths:
  /users/{id}/orders:
    get:
      tags:
        - user-management
        - order-processing
      operationId: users_list_orders
      summary: Get orders for a specific user
```

**Use sparingly**: Multiple tags can complicate navigation.

## Deprecation

Mark operations as deprecated when they should no longer be used:

```yaml
paths:
  /users/legacy:
    get:
      deprecated: true
      operationId: users_list_legacy
      summary: List users (legacy endpoint)
      description: |
        **DEPRECATED**: Use `/users` endpoint instead.

        This endpoint is deprecated as of version 2.0 and will be removed in version 3.0.
        Please migrate to the new `/users` endpoint which provides improved pagination
        and filtering.

        **Migration Guide**: https://docs.example.com/migration/users
```

**Best Practices for Deprecation**:
- Set `deprecated: true`
- Explain why it's deprecated
- Point to replacement endpoint
- Specify removal timeline if known
- Link to migration guide
- Keep the operation functional (don't break existing clients)

## External Documentation

Link to additional documentation:

```yaml
paths:
  /webhooks:
    post:
      operationId: webhooks_register
      summary: Register a webhook
      externalDocs:
        description: Webhook Configuration Guide
        url: https://docs.example.com/webhooks/setup
```

## Operation-Level Servers

Override base server URL for specific operations:

```yaml
servers:
  - url: https://api.example.com/v1
    description: Main API server

paths:
  /files/upload:
    post:
      operationId: files_upload
      servers:
        - url: https://uploads.example.com/v1
          description: Dedicated upload server
      # This operation uses a different base URL
```

**Use when**: Specific operations use different infrastructure (uploads, webhooks, regional endpoints).

## Operation Organization Patterns

### RESTful Resource Pattern

Organize operations around resources:

```yaml
paths:
  # Collection operations
  /users:
    get:
      operationId: users_list
    post:
      operationId: users_create

  # Single resource operations
  /users/{id}:
    get:
      operationId: users_get
    put:
      operationId: users_update
    patch:
      operationId: users_patch
    delete:
      operationId: users_delete

  # Sub-resource operations
  /users/{id}/orders:
    get:
      operationId: users_list_orders

  /users/{id}/avatar:
    put:
      operationId: users_upload_avatar
    delete:
      operationId: users_delete_avatar
```

### Action-Based Operations

For operations that don't fit CRUD:

```yaml
paths:
  /users/{id}/activate:
    post:
      operationId: users_activate
      summary: Activate a user account

  /users/{id}/suspend:
    post:
      operationId: users_suspend
      summary: Suspend a user account

  /orders/{id}/cancel:
    post:
      operationId: orders_cancel
      summary: Cancel an order

  /reports/generate:
    post:
      operationId: reports_generate
      summary: Generate a new report
```

**Use POST** for action-based operations that don't map to standard REST verbs.

## Common Pitfalls

### Avoid

**Missing operationId**:
```yaml
get:
  summary: Get users
  # ❌ No operationId - tools will generate one
```

**Inconsistent naming**:
```yaml
# ❌ Mixed styles in same spec
operationId: users_list
operationId: getOrder
operationId: CreatePayment
```

**Non-semantic HTTP methods**:
```yaml
# ❌ GET with side effects
/users/{id}/activate:
  get:
    operationId: users_activate
    # GET should not modify state - use POST
```

**Vague summaries**:
```yaml
summary: Does user stuff
summary: Handles request
summary: API endpoint
```

**Complex operations without descriptions**:
```yaml
post:
  operationId: users_search
  summary: Search users
  # ❌ No description explaining search capabilities
```

### Do

- Always define `operationId`
- Use consistent naming conventions throughout
- Choose HTTP methods based on semantics
- Write specific summaries and detailed descriptions
- Use tags to organize operations logically
- Mark deprecated operations clearly with migration paths
- Document complex behaviors and edge cases
- Use CommonMark for rich formatting in descriptions

## Summary Checklist

For each operation:

- [ ] `operationId` defined with `resource_action` pattern
- [ ] Appropriate HTTP method (GET/POST/PUT/PATCH/DELETE)
- [ ] Clear, specific summary (under 50 chars)
- [ ] Detailed description for complex operations
- [ ] Tagged appropriately for organization
- [ ] Deprecated operations marked with migration info
- [ ] External docs linked where appropriate
- [ ] Parameters, request body, and responses defined
- [ ] Success and error responses documented

## SDK-Friendly Extensions

For Speakeasy SDK generation, consider these extensions:

```yaml
paths:
  /users:
    get:
      operationId: users_list
      x-speakeasy-group: users
      x-speakeasy-name-override: listAll
      # Generates: sdk.users.listAll()

  /orders/{id}/refund:
    post:
      operationId: orders_refund
      x-speakeasy-group: orders
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 500
          maxInterval: 60000
          maxElapsedTime: 3600000
          exponent: 1.5
      # Adds automatic retry logic
```

**Common Speakeasy Extensions**:
- `x-speakeasy-group`: Groups operations into SDK namespaces
- `x-speakeasy-name-override`: Overrides generated method name
- `x-speakeasy-retries`: Configures retry behavior
- `x-speakeasy-errors`: Defines error handling strategies

See Speakeasy documentation for complete extension reference.
