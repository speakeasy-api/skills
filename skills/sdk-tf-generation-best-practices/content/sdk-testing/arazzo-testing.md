---
short_description: "Custom end-to-end API tests using Arazzo specification"
long_description: |
  Guide for using Arazzo format to define custom API test workflows. Arazzo enables
  declarative test definitions with success criteria, payload templates, workflow
  orchestration, security configuration, and environment variable support for SDK testing.
source:
  repo: "speakeasy-api/speakeasy"
  path: "docs/sdks/sdk-contract-testing/custom-contract-tests.mdx"
  ref: "main"
  last_reconciled: "2025-12-11"
---

# Custom End-to-End API Contract Tests with Arazzo

Use Speakeasy to create custom end-to-end contract tests that run against a real API. This guide covers writing complex tests using the Arazzo Specification, including:

- Server URLs
- Security credentials
- Environment variable-provided values
- Multi-step workflows
- Request/response chaining

> **Recommendation**: Fully set up SDK tests in all SDK repositories before exploring custom contract tests.

## What is Arazzo?

Arazzo (OpenAPI Arazzo Specification) is a simple, human-readable, and extensible specification for defining API workflows. Arazzo powers custom test generation, allowing rich tests capable of:

- Testing multiple operations
- Testing different inputs
- Validating correct responses
- Running against a real API or mock server
- Configuring setup and teardown routines for complex E2E tests

When a `.speakeasy/tests.arazzo.yaml` file is found in the SDK repo, the Arazzo workflow generates tests for each workflow defined in the file.

## Prerequisites

Before generating tests, ensure that the testing feature prerequisites are met (Enterprise tier account with SDK contract add-on enabled).

---

## Basic Arazzo Document Structure

```yaml
arazzo: 1.0.0
info:
  title: Test Suite
  summary: E2E tests for the SDK and API
  version: 0.0.1
sourceDescriptions:
  - name: The API
    url: https://example.com/openapi.yaml
    type: openapi
workflows:
  - workflowId: create_resource
    steps:
      - stepId: create
        operationId: createResource
        requestBody:
          contentType: application/json
          payload:
            name: "test-resource"
        successCriteria:
          - condition: $statusCode == 201
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `arazzo` | string | Arazzo specification version. Use `1.0.1` or `1.0.0` |
| `info` | object | Metadata about the test suite (title, version, summary) |
| `sourceDescriptions` | array | References to API specifications being tested |
| `workflows` | array | List of test workflow definitions |

---

## Writing Custom End-to-End Tests

Example Arazzo document defining a user resource lifecycle test:

```yaml
arazzo: 1.0.0
info:
  title: Test Suite
  summary: E2E tests for the SDK and API
  version: 0.0.1
sourceDescriptions:
  - name: The API
    url: https://example.com/openapi.yaml
    type: openapi
workflows:
  - workflowId: user-lifecycle
    steps:
      - stepId: create
        operationId: createUser
        requestBody:
          contentType: application/json
          payload:
            email: "Trystan_Crooks@hotmail.com"
            first_name: "Trystan"
            last_name: "Crooks"
            age: 32
            postal_code: 94110
            metadata:
              allergies: "none"
              color: "red"
              height: 182
              weight: 77
              is_smoking: true
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.header.Content-Type == "application/json"
          - condition: $response.body#/email == Trystan_Crooks@hotmail.com
          - condition: $response.body#/postal_code == 94110
        outputs:
          id: $response.body#/id

      - stepId: get
        operationId: getUser
        parameters:
          - name: id
            in: path
            value: $steps.create.outputs.id
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.header.Content-Type == "application/json"
          - condition: $response.body#/email == Trystan_Crooks@hotmail.com
          - condition: $response.body#/first_name == Trystan
          - condition: $response.body#/last_name == Crooks
          - condition: $response.body#/age == 32
          - condition: $response.body#/postal_code == 94110
        outputs:
          user: $response.body
          age: $response.body#/age

      - stepId: update
        operationId: updateUser
        parameters:
          - name: id
            in: path
            value: $steps.create.outputs.id
        requestBody:
          contentType: application/json
          payload: $steps.get.outputs.user
          replacements:
            - target: /postal_code
              value: 94107
            - target: /age
              value: $steps.get.outputs.age
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/postal_code == 94107

      - stepId: delete
        operationId: deleteUser
        parameters:
          - name: id
            in: path
            value: $steps.create.outputs.id
        successCriteria:
          - condition: $statusCode == 200
```

This workflow defines four steps that feed into each other:

1. Create a user
2. Retrieve that user via its new ID
3. Update the user
4. Delete the user

This is possible because the workflow defines outputs for certain steps that serve as inputs for following steps.

---

## Workflow Definition

Each workflow describes a sequence of API operations:

```yaml
workflows:
  - workflowId: user_lifecycle
    summary: Test user creation, update, and deletion
    inputs:
      type: object
      properties:
        username:
          type: string
          default: "testuser"
    steps:
      - stepId: create_user
        operationId: createUser
        requestBody:
          contentType: application/json
          payload:
            username: $inputs.username
            email: "test@example.com"
        successCriteria:
          - condition: $statusCode == 201
        outputs:
          userId: $response.body.id
```

### Workflow Fields

| Field | Type | Description |
|-------|------|-------------|
| `workflowId` | string | Unique identifier for the workflow |
| `summary` | string | Brief description |
| `description` | string | Detailed description |
| `inputs` | object | JSON Schema for workflow inputs |
| `steps` | array | Ordered list of test steps |
| `outputs` | object | Values to export from workflow |

---

## Step Definition

Each step represents a single API operation:

```yaml
steps:
  - stepId: test_operation
    operationId: myOperation
    description: Test the myOperation endpoint
    parameters:
      - name: id
        in: path
        value: "123"
      - name: filter
        in: query
        value: "active"
    requestBody:
      contentType: application/json
      payload:
        field1: "value1"
        field2: 42
    successCriteria:
      - condition: $statusCode == 200
      - condition: $response.header.Content-Type == "application/json"
      - condition: $response.body.status == "success"
    outputs:
      resultId: $response.body.id
```

### Step Fields

| Field | Type | Description |
|-------|------|-------------|
| `stepId` | string | Unique step identifier within workflow |
| `operationId` | string | OpenAPI operation to call |
| `description` | string | Step description |
| `parameters` | array | Path, query, header parameters |
| `requestBody` | object | Request body configuration |
| `successCriteria` | array | Conditions that must be true |
| `outputs` | object | Values to extract from response |

---

## Inputs and Outputs

### Workflow Inputs

Provide input parameters to workflows using the `inputs` field, which is a JSON Schema object:

```yaml
workflows:
  - workflowId: some-test
    inputs:
      type: object
      properties:
        email:
          type: string
          examples:
            - Trystan_Crooks@hotmail.com
        firstName:
          type: string
          examples:
            - Trystan
        lastName:
          type: string
          examples:
            - Crooks
    steps:
      - stepId: create
        operationId: createUser
        requestBody:
          contentType: application/json
          payload:
            email: "$inputs.email"
            first_name: "$inputs.firstName"
            last_name: "$inputs.lastName"
        successCriteria:
          - condition: $statusCode == 200
```

Test generation uses examples defined for a property as literal values. If no examples are defined, values are randomly generated.

### Step References

Parameters and request body payloads can reference values from previous steps using runtime expressions:

```yaml
workflows:
  - workflowId: some-test
    steps:
      - stepId: create
        operationId: createUser
        requestBody:
          contentType: application/json
          payload:
            email: "test@example.com"
        successCriteria:
          - condition: $statusCode == 200
        outputs:
          id: $response.body#/id

      - stepId: get
        operationId: getUser
        parameters:
          - name: id
            in: path
            value: $steps.create.outputs.id
        successCriteria:
          - condition: $statusCode == 200
```

### Inline Values

Provide literal values inline for parameters or request body payloads:

```yaml
steps:
  - stepId: update
    operationId: updateUser
    parameters:
      - name: id
        in: path
        value: "some-test-id"
    requestBody:
      contentType: application/json
      payload:
        email: "Trystan_Crooks@hotmail.com"
        first_name: "Trystan"
        last_name: "Crooks"
        age: 32
        postal_code: 94110
    successCriteria:
      - condition: $statusCode == 200
```

### Payload Values with Replacements

Use the `payload` field with the `replacements` field to overlay payload values:

```yaml
steps:
  - stepId: get
    # ...
    outputs:
      user: $response.body

  - stepId: update
    operationId: updateUser
    parameters:
      - name: id
        in: path
        value: "some-test-id"
    requestBody:
      contentType: application/json
      payload: $steps.get.outputs.user
      replacements:
        - target: /postal_code
          value: 94107
        - target: /age
          value: $steps.some-other-step.outputs.age
    successCriteria:
      - condition: $statusCode == 200
```

### Step Outputs

Define outputs for each step to use values from response bodies in following steps:

```yaml
steps:
  - stepId: create
    operationId: createUser
    requestBody:
      contentType: application/json
      payload:
        email: "test@example.com"
    successCriteria:
      - condition: $statusCode == 200
    outputs:
      id: $response.body#/id
      email: $response.body#/email
      age: $response.body#/age
      allergies: $response.body#/metadata/allergies
```

Currently, Speakeasy supports only referencing values from response bodies using runtime expressions and JSON pointers.

---

## Success Criteria

The `successCriteria` field contains a list of criterion objects used to validate step success and form the basis of test assertions:

```yaml
successCriteria:
  # Status code check
  - condition: $statusCode == 200

  # Header check
  - condition: $response.header.Content-Type == "application/json"

  # Body field check
  - condition: $response.body#/email == Trystan_Crooks@hotmail.com

  # Or full object comparison
  - context: $response.body
    type: simple
    condition: |
      {
        "email": "Trystan_Crooks@hotmail.com",
        "first_name": "Trystan",
        "last_name": "Crooks",
        "age": 32,
        "postal_code": 94110
      }
```

Speakeasy's implementation currently only supports `simple` criteria and equality (`==`) and inequality (`!=`) operators for comparing values and testing status codes, response headers, and response bodies.

> **Note**: While the Arazzo specification defines additional operators like `>`, `<`, `>=`, `<=`, `~`, and `!~`, Speakeasy currently only supports `==` and `!=`.

To test values within the response body, due to the typed nature of SDKs, include criteria for testing the status code and content type to help the generator determine which response schema to validate against.

### Runtime Expression Syntax

| Expression | Description |
|------------|-------------|
| `$statusCode` | HTTP status code |
| `$response.header.X` | Response header value |
| `$response.body` | Full response body |
| `$response.body#/field` | Specific body field (JSON pointer) |
| `$inputs.name` | Workflow input value |
| `$steps.stepId.outputs.name` | Output from previous step |

---

## Configuring API Server

By default, tests run against Speakeasy's mock server at `http://localhost:18080`. The mock server validates SDK functionality but does not guarantee API correctness.

Configure tests to run against another URL using the `x-speakeasy-test-server` extension:

```yaml
arazzo: 1.0.0
# ...
x-speakeasy-test-server:
  baseUrl: "https://api.example.com"  # All workflows run against this URL

workflows:
  - workflowId: some-test
    x-speakeasy-test-server:
      baseUrl: "x-env: CUSTOM_API_URL"  # Overrides top-level config
    # ...
```

If the extension is at the top level, all workflows run against the specified server URL. If within a workflow, only that workflow runs against the specified URL.

### Environment Variables in Server URLs

The server URL can be a static URL or use `x-env: ENV_VAR_NAME` to pull from an environment variable:

```yaml
x-speakeasy-test-server:
  baseUrl: "x-env: CUSTOM_API_URL; http://localhost:18080"  # Default if env var not set
```

> **Warning**: The `TEST_SERVER_URL` environment variable is reserved for Speakeasy's mock server. When running `speakeasy test`, if the mock server is generated and enabled, `TEST_SERVER_URL` is automatically set to the mock server URL and overwrites any existing value while running.

To use a custom test server instead of the mock server:

- Use the `--disable-mockserver` flag when running `speakeasy test`
- Use a different environment variable name (like `CUSTOM_API_URL`)

---

## Configuring Security Credentials

When running tests against a real API, configure security credentials using the `x-speakeasy-test-security` extension.

The extension allows static values, values from environment variables, or runtime expressions referencing outputs from previous steps.

> **Important**: The keys under `value` must exactly match the names of `securitySchemes` defined in the OpenAPI document's `components.securitySchemes` section.

### Security Scheme Mapping

If the OpenAPI document defines:

```yaml
components:
  securitySchemes:
    myApiKeyScheme:
      type: apiKey
      in: header
      name: X-API-Key
    myBasicAuthScheme:
      type: http
      scheme: basic
    myBearerTokenScheme:
      type: http
      scheme: bearer
    myOAuth2Scheme:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://api.example.com/oauth2/token
          scopes: {}
```

Then the Arazzo configuration should reference these exact scheme names:

```yaml
arazzo: 1.0.0
# ...
x-speakeasy-test-security:
  value:
    myApiKeyScheme: "x-env: TEST_API_KEY"
    myBasicAuthScheme:
      username: "test-user"
      password: "x-env: TEST_PASSWORD"
    myBearerTokenScheme: "x-env: TEST_BEARER_TOKEN"
    myOAuth2Scheme:
      clientId: "x-env: MY_CLIENT_ID"
      clientSecret: "x-env: MY_CLIENT_SECRET"
      tokenURL: "http://test-server/oauth2/token"

workflows:
  - workflowId: some-test
    x-speakeasy-test-security:  # Override for specific workflow
      value:
        myApiKeyScheme: "test-key"
    steps:
      - stepId: step1
        x-speakeasy-test-security:  # Override for specific step
          value:
            myBearerTokenScheme: "x-env: TEST_AUTH_TOKEN"
        # ...
```

> **Note**: For OAuth2 schemes, override the `tokenURL` to redirect authentication flow to a test server instead of the production endpoint.

### Dynamic Security with Runtime Expressions

Use runtime expressions to populate security credentials dynamically from outputs of previous steps:

```yaml
workflows:
  - workflowId: createUser
    x-speakeasy-test-security:
      value:
        apiKey: $steps.authenticate.outputs.token
    steps:
      - stepId: authenticate
        workflowId: authenticate
        requestBody:
          contentType: application/json
          payload:
            username: "trystan.crooks@example.com"
            password: "x-env: TEST_PASSWORD"
        successCriteria:
          - condition: $steps.authenticate.outputs.token != ""
        outputs:
          token: $response.body#/token

      - stepId: create
        operationId: createUser
        requestBody:
          contentType: application/json
          payload:
            email: "Trystan_Crooks@hotmail.com"
            first_name: "Trystan"
            last_name: "Crooks"
        successCriteria:
          - condition: $statusCode == 200
```

In this example:

- The workflow defines `x-speakeasy-test-security` at the workflow level with `apiKey: $steps.authenticate.outputs.token`
- The first step calls an authentication workflow and captures the token in outputs
- All subsequent steps use this dynamically obtained token for authentication

This enables complex authentication flows where tokens must be obtained dynamically during test execution.

---

## Environment Variables

Use environment variables to fill in input values from dynamic sources:

```yaml
workflows:
  - workflowId: my-env-var-test
    steps:
      - stepId: update
        operationId: updateUser
        parameters:
          - name: id
            in: path
            value: "x-env: TEST_ID; default"  # With optional default
        requestBody:
          contentType: application/json
          payload:
            email: "x-env: TEST_EMAIL; default@example.com"
            first_name: "Trystan"
            last_name: "Crooks"
            age: 32
        successCriteria:
          - condition: $statusCode == 200
```

The format is `x-env: ENV_VAR_NAME; default_value`. If the environment variable is not set, the default value is used.

---

## Testing Binary Data Operations

Some operations require binary data (e.g., file uploads and downloads). Use the `x-file` directive:

```yaml
workflows:
  - workflowId: postFile
    steps:
      - stepId: test
        operationId: postFile
        requestBody:
          contentType: multipart/form-data
          payload:
            file: "x-file: some-test-file.txt"
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.header.Content-Type == "application/octet-stream"
          - context: $response.body
            condition: "x-file: some-other-test-file.dat"
            type: simple
```

Files are sourced from the `.speakeasy/testfiles` directory in the SDK repo root. The path in the `x-file` directive is relative to the `testfiles` directory.

---

## Disabling Tests via Overlay

Use overlays to disable tests for specific operations:

```yaml
# tests-overlay.yaml
overlay: 1.0.0
info:
  title: Disable Failing Tests
  version: 1.0.0
actions:
  # Disable test for a specific endpoint
  - target: $.paths['/v4/domains/{domain}/records'].get
    update:
      x-speakeasy-test: false

  # Disable test for endpoint requiring special setup
  - target: $.paths['/admin/dangerous-operation'].post
    update:
      x-speakeasy-test: false

  # Disable test for rate-limited endpoint
  - target: $.paths['/bulk-import'].post
    update:
      x-speakeasy-test: false
```

### When to Disable Tests

| Scenario | Reason |
|----------|--------|
| External dependencies | Endpoint calls external services |
| Rate limiting | Endpoint has strict rate limits |
| Side effects | Operation has irreversible effects |
| Special authentication | Requires OAuth flow or MFA |
| Flaky behavior | API returns inconsistent results |
| Long-running operations | Async operations that timeout |

---

## Best Practices

### 1. Organize Workflows by Feature

```yaml
workflows:
  # Group related operations
  - workflowId: user_crud
    summary: User CRUD operations

  - workflowId: user_permissions
    summary: User permission management

  - workflowId: user_authentication
    summary: User auth flows
```

### 2. Use Meaningful Step IDs

```yaml
steps:
  # Good: descriptive step IDs
  - stepId: create_admin_user
  - stepId: verify_admin_permissions
  - stepId: revoke_admin_access

  # Avoid: generic step IDs
  - stepId: step1
  - stepId: step2
```

### 3. Clean Up Test Resources

```yaml
workflows:
  - workflowId: resource_lifecycle
    steps:
      - stepId: create_resource
        # ... create
        outputs:
          resourceId: $response.body.id

      - stepId: test_operations
        # ... test

      - stepId: cleanup_resource
        operationId: deleteResource
        parameters:
          - name: id
            in: path
            value: $steps.create_resource.outputs.resourceId
        successCriteria:
          - condition: $statusCode == 204
```

### 4. Handle Authentication

```yaml
workflows:
  - workflowId: authenticated_operations
    inputs:
      type: object
      properties:
        apiToken:
          type: string
    steps:
      - stepId: authenticated_call
        operationId: protectedEndpoint
        parameters:
          - name: Authorization
            in: header
            value: "Bearer $inputs.apiToken"
```

---

## Pre-defined TODO List

When setting up Arazzo custom tests, initialize the TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Create .speakeasy/tests.arazzo.yaml with custom workflow | Creating custom test workflow |
| 2 | Define workflow inputs and steps | Defining workflow structure |
| 3 | Configure success criteria for each step | Configuring success criteria |
| 4 | Set up step outputs for chaining | Setting up step outputs |
| 5 | Configure x-speakeasy-test-server for real API | Configuring test server |
| 6 | Configure x-speakeasy-test-security credentials | Configuring security credentials |
| 7 | Add environment variables for dynamic values | Adding environment variables |
| 8 | Run speakeasy test to validate custom tests | Running custom tests |
| 9 | Add cleanup steps for test resources | Adding cleanup steps |
| 10 | Integrate custom tests into CI pipeline | Integrating into CI |

**Usage:**
```
TodoWrite([
  {content: "Create .speakeasy/tests.arazzo.yaml with custom workflow", status: "pending", activeForm: "Creating custom test workflow"},
  {content: "Define workflow inputs and steps", status: "pending", activeForm: "Defining workflow structure"},
  {content: "Configure success criteria for each step", status: "pending", activeForm: "Configuring success criteria"},
  {content: "Set up step outputs for chaining", status: "pending", activeForm: "Setting up step outputs"},
  {content: "Configure x-speakeasy-test-server for real API", status: "pending", activeForm: "Configuring test server"},
  {content: "Configure x-speakeasy-test-security credentials", status: "pending", activeForm: "Configuring security credentials"},
  {content: "Add environment variables for dynamic values", status: "pending", activeForm: "Adding environment variables"},
  {content: "Run speakeasy test to validate custom tests", status: "pending", activeForm: "Running custom tests"},
  {content: "Add cleanup steps for test resources", status: "pending", activeForm: "Adding cleanup steps"},
  {content: "Integrate custom tests into CI pipeline", status: "pending", activeForm: "Integrating into CI"}
])
```

**Related documentation:**
- `./contract-testing.md` - SDK contract testing overview and bootstrapping
- `./integration-testing.md` - Integration test patterns
- `../spec-first/overlays.md` - Overlay configuration including test disabling
- `../plans/sdk-generation.md` - Full SDK generation workflow
