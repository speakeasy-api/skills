# Arazzo Test Specification Reference

Complete reference for writing custom API workflow tests using Arazzo.

## Document Structure

```yaml
arazzo: 1.0.0
info:
  title: Test Suite
  summary: E2E tests for SDK
  version: 1.0.0
sourceDescriptions:
  - name: my-api
    url: ./openapi.yaml
    type: openapi
workflows:
  - workflowId: test-workflow
    steps:
      - stepId: step-1
        operationId: someOperation
        # ...
```

## Workflows

Each workflow is an independent test case:

```yaml
workflows:
  - workflowId: user-lifecycle
    description: Test user CRUD operations
    steps:
      # Steps execute in order
      - stepId: create-user
        # ...
      - stepId: verify-user
        # ...
      - stepId: delete-user
        # ...
```

## Steps

### Basic Step

```yaml
steps:
  - stepId: get-resource
    operationId: getResource  # Must match OpenAPI operationId
    parameters:
      - name: id
        in: path
        value: "123"
    successCriteria:
      - condition: $statusCode == 200
```

### With Request Body

```yaml
steps:
  - stepId: create-resource
    operationId: createResource
    requestBody:
      contentType: application/json
      payload:
        name: "test-resource"
        type: "example"
        metadata:
          key: "value"
    successCriteria:
      - condition: $statusCode == 201
```

### With Outputs

Capture values for later steps:

```yaml
steps:
  - stepId: create-resource
    operationId: createResource
    requestBody:
      payload:
        name: "test"
    successCriteria:
      - condition: $statusCode == 201
    outputs:
      resourceId: $response.body#/id
      resourceName: $response.body#/name
```

## Chaining Steps

Reference outputs from previous steps:

```yaml
workflows:
  - workflowId: resource-lifecycle
    steps:
      - stepId: create
        operationId: createResource
        requestBody:
          payload:
            name: "test-resource"
        successCriteria:
          - condition: $statusCode == 201
        outputs:
          id: $response.body#/id

      - stepId: get
        operationId: getResource
        parameters:
          - name: id
            in: path
            value: $steps.create.outputs.id
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/name == "test-resource"

      - stepId: update
        operationId: updateResource
        parameters:
          - name: id
            in: path
            value: $steps.create.outputs.id
        requestBody:
          payload:
            name: "updated-resource"
        successCriteria:
          - condition: $statusCode == 200

      - stepId: delete
        operationId: deleteResource
        parameters:
          - name: id
            in: path
            value: $steps.create.outputs.id
        successCriteria:
          - condition: $statusCode == 204
```

## Success Criteria

### Status Code

```yaml
successCriteria:
  - condition: $statusCode == 200
  - condition: $statusCode >= 200
  - condition: $statusCode < 300
```

### Response Headers

```yaml
successCriteria:
  - condition: $response.header.Content-Type == "application/json"
  - condition: $response.header.X-Request-Id != null
```

### Response Body (JSONPath)

```yaml
successCriteria:
  # Exact value
  - condition: $response.body#/status == "active"

  # Numeric comparison
  - condition: $response.body#/count > 0
  - condition: $response.body#/total >= 10

  # Existence
  - condition: $response.body#/id != null

  # Nested path
  - condition: $response.body#/data/user/email == "test@example.com"

  # Array element
  - condition: $response.body#/items/0/name == "first-item"
```

## Environment Variables

Reference sensitive values from environment:

```yaml
steps:
  - stepId: authenticated-request
    operationId: getProtectedResource
    parameters:
      - name: Authorization
        in: header
        value: Bearer $env.API_TOKEN
    successCriteria:
      - condition: $statusCode == 200
```

Set when running:
```bash
API_TOKEN=secret123 speakeasy test
```

## Request Body Replacements

Modify payload using outputs:

```yaml
steps:
  - stepId: get-user
    operationId: getUser
    parameters:
      - name: id
        in: path
        value: $steps.create-user.outputs.id
    outputs:
      user: $response.body

  - stepId: update-user
    operationId: updateUser
    parameters:
      - name: id
        in: path
        value: $steps.create-user.outputs.id
    requestBody:
      contentType: application/json
      payload: $steps.get-user.outputs.user
      replacements:
        - target: /name
          value: "New Name"
        - target: /email
          value: "new@example.com"
```

## Security Configuration

### Global Security

```yaml
sourceDescriptions:
  - name: my-api
    url: ./openapi.yaml
    type: openapi
    x-speakeasy-security:
      apiKey: $env.API_KEY
```

### Per-Step Override

```yaml
steps:
  - stepId: admin-request
    operationId: adminOperation
    x-speakeasy-security:
      bearerAuth: $env.ADMIN_TOKEN
```

## Server Selection

```yaml
sourceDescriptions:
  - name: my-api
    url: ./openapi.yaml
    type: openapi
    x-speakeasy-server-id: staging
```

Or per step:
```yaml
steps:
  - stepId: production-call
    operationId: someOperation
    x-speakeasy-server-url: https://api.production.example.com
```

## Disabling Tests

Disable via overlay for flaky or WIP tests:

```yaml
# disable-tests-overlay.yaml
overlay: 1.0.0
info:
  title: Disable flaky tests
actions:
  - target: $["workflows"][?(@.workflowId=="flaky-test")]
    update:
      x-speakeasy-test:
        disabled: true
```

## Complete Example

```yaml
arazzo: 1.0.0
info:
  title: User API Tests
  version: 1.0.0

sourceDescriptions:
  - name: user-api
    url: ./openapi.yaml
    type: openapi

workflows:
  - workflowId: user-crud-lifecycle
    description: Full user lifecycle test
    steps:
      - stepId: create-user
        operationId: createUser
        requestBody:
          contentType: application/json
          payload:
            email: "test-$env.TEST_RUN_ID@example.com"
            first_name: "Test"
            last_name: "User"
            role: "member"
        successCriteria:
          - condition: $statusCode == 201
          - condition: $response.body#/id != null
        outputs:
          userId: $response.body#/id
          userEmail: $response.body#/email

      - stepId: get-user
        operationId: getUser
        parameters:
          - name: id
            in: path
            value: $steps.create-user.outputs.userId
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/email == $steps.create-user.outputs.userEmail
          - condition: $response.body#/first_name == "Test"

      - stepId: update-user
        operationId: updateUser
        parameters:
          - name: id
            in: path
            value: $steps.create-user.outputs.userId
        requestBody:
          contentType: application/json
          payload:
            first_name: "Updated"
            role: "admin"
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/first_name == "Updated"
          - condition: $response.body#/role == "admin"

      - stepId: list-users
        operationId: listUsers
        parameters:
          - name: limit
            in: query
            value: 10
          - name: role
            in: query
            value: "admin"
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/total >= 1

      - stepId: delete-user
        operationId: deleteUser
        parameters:
          - name: id
            in: path
            value: $steps.create-user.outputs.userId
        successCriteria:
          - condition: $statusCode == 204

      - stepId: verify-deleted
        operationId: getUser
        parameters:
          - name: id
            in: path
            value: $steps.create-user.outputs.userId
        successCriteria:
          - condition: $statusCode == 404
```

## Running Tests

```bash
# Run all tests
speakeasy test

# Run specific target
speakeasy test --target my-sdk

# Verbose output
speakeasy test --verbose
```
