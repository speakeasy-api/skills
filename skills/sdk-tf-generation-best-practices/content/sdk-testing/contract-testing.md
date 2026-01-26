---
short_description: "Speakeasy-generated SDK contract testing with Arazzo"
long_description: |
  Automated contract testing for Speakeasy-generated SDKs using the Arazzo specification.
  Includes test generation, mock server support, bootstrapping workflows, and GitHub Actions
  integration for validating SDK correctness against API contracts.
source:
  repo: "speakeasy-api/speakeasy"
  path: "docs/sdks/sdk-contract-testing"
  ref: "main"
  last_reconciled: "2025-12-11"
---

# SDK Contract Testing

Speakeasy verifies SDK functionality by generating and running contract tests. Contract tests validate that SDKs correctly serialize requests, deserialize responses, and match the API contract defined in the OpenAPI specification.

> **Beta**: SDK contract testing is considered beta maturity. Breaking changes may occur and not all languages are supported. Currently supported: TypeScript, Python, Go, and Java.

## Design Philosophy

Speakeasy contract tests are designed to be:

- **Human readable**: Tests avoid convoluted abstractions and are easy to read and debug.
- **Batteries-included**: Tests can be generated for SDK operations with a mock API server working out of the box, avoiding complex test environment setups like data seeding.
- **Rich in coverage**: Generated tests verify all possible data fields to ensure full coverage. If examples are not available, realistic values are used based on name, type, and format information.
- **Customizable**: Custom tests are supported alongside generated tests.
- **Minimal dependencies**: Speakeasy avoids unnecessary dependencies, prioritizing native language libraries.
- **Easy integration**: Testing integrates easily into existing API development and testing workflows.
- **Open standards**: Based on the Arazzo Specification - no vendor lock-in.

## Features

Speakeasy uses the Arazzo Specification to generate tests for APIs. Arazzo is a simple, human-readable, and extensible specification for defining API workflows.

Contract test generation provides:

- Contract tests for operations in the OpenAPI document (when enabled), including:
  - Generating or modifying `.speakeasy/tests.arazzo.yaml` to include tests for operations
  - Using examples from the OpenAPI document or autogenerating based on field name, type, and format
  - Generating a mock server capable of responding to API requests
- Custom tests and workflows for any use case, with capabilities like:
  - Testing multiple operations in sequence
  - Testing different inputs
  - Validating correct responses
  - Running against a real API or mock server
  - Configuring setup and teardown routines for complex E2E tests

---

## Prerequisites

To enable testing features, the following are required:

- An existing, successfully generating SDK
- The Speakeasy CLI or a GitHub repository with Actions enabled
- Docker or equivalent container runtime (if using the mock server for local testing)
- An Enterprise tier account
- Enable the SDK contract add-on in settings/billing

---

## Bootstrapping Tests

Automatically generate tests for all SDK operations using the Speakeasy CLI.

### Enabling Test Generation

Navigate to the SDK repository and run:

```bash
speakeasy configure tests
```

This command enables both `generateTests` and `generateNewTests` settings in the `gen.yaml` configuration file.

Test generation is controlled by the following settings in the `generation` section:

```yaml
configVersion: 2.0.0
generation:
  tests:
    generateTests: true      # Controls whether tests are generated during speakeasy run
    generateNewTests: true   # Controls whether new tests are added for new operations
```

**Settings:**

| Setting | Description |
|---------|-------------|
| `generateTests` | When `true`, tests defined in `.speakeasy/tests.arazzo.yaml` are generated during `speakeasy run` |
| `generateNewTests` | When `true`, new tests are automatically added to `.speakeasy/tests.arazzo.yaml` for new operations |

When enabling for the first time, this generates tests for all operations in the OpenAPI document. Going forward, it only generates tests for operations not already found in the `.speakeasy/tests.arazzo.yaml` file.

### Generated Test Location

Generated test files are written in language-specific locations, relative to the SDK root:

| Language | Location |
|----------|----------|
| Go | `tests/` |
| Python | `tests/` |
| TypeScript | `src/__tests__` |
| Java | `src/test/java` |

If the mock server is generated, its output is in a `mockserver` directory under these locations.

### Disabling Test Generation

To completely disable test generation, delete the `.speakeasy/tests.arazzo.yaml` file:

```bash
rm .speakeasy/tests.arazzo.yaml
```

The existence of this file triggers test generation. Once removed, no tests are generated regardless of configuration.

### Disable Tests for Specific Operations

To disable generation of tests for a specific operation, set `x-speakeasy-test: false`:

```yaml
paths:
  /example1:
    get:
      # This operation will generate testing (default behavior)
      # ... operation configuration ...
  /example2:
    get:
      # This operation will not generate testing
      x-speakeasy-test: false
      # ... operation configuration ...
```

---

## Running Tests

Tests can be run via CLI, GitHub Actions, or as part of the generation workflow.

### Via CLI

Run tests for all SDKs:

```bash
speakeasy test -t all
```

Or select specific targets interactively:

```bash
speakeasy test
```

### During Generation

Enable running tests during `speakeasy run` by modifying `.speakeasy/workflow.yaml`:

```yaml
targets:
  example-target:
    # ... other configuration ...
    testing:
      enabled: true
```

### Viewing Test Reports

View test reports in the Tests tab under a particular SDK in the Speakeasy dashboard at app.speakeasy.com.

---

## Customizing Tests

### Automatic Test Synchronization

Speakeasy synchronizes workflows in `.speakeasy/tests.arazzo.yaml` based on the `x-speakeasy-test-rebuild` extension.

**Auto-sync with OpenAPI changes (`x-speakeasy-test-rebuild: true`):**

When set to `true`, the workflow automatically stays in sync with the OpenAPI specification. The test is rebuilt each time the spec changes, incorporating:

- New parameters
- Request body field changes
- Response body updates
- Updates to examples

```yaml
arazzo: 1.0.0
workflows:
  - workflowId: some-test
    x-speakeasy-test-rebuild: true  # Test auto-syncs with OpenAPI changes
    # ...
```

**Manual test maintenance (`x-speakeasy-test-rebuild: false` or omitted):**

When omitted or set to `false`, the workflow requires manual maintenance and won't sync with the OpenAPI specification. Use this when:

- Writing custom tests with specific logic
- Maintaining test state independent from OpenAPI document
- Catching breaking changes or regressions in API behavior

```yaml
arazzo: 1.0.0
workflows:
  - workflowId: some-test
    x-speakeasy-test-rebuild: false  # Manual maintenance required
    # ...
```

### Grouping Tests

By default, all tests are generated into a single file (e.g., `sdk.test.ts`, `test_sdk.py`, `SDKTest.java`). Configure grouping with `x-speakeasy-test-group`:

```yaml
arazzo: 1.0.0
workflows:
  - workflowId: some-test
    x-speakeasy-test-group: user  # Groups in user.test.ts/test_user.py/user_test.go
    # ...
```

### Generate Tests for Specific Targets

Control which languages generate tests using `x-speakeasy-test-targets` or `x-speakeasy-test-targets-exclude`:

```yaml
arazzo: 1.0.0
workflows:
  - workflowId: some-test
    x-speakeasy-test-targets:  # Only generate for TypeScript
      - typescript
    # ...
```

Or exclude specific targets:

```yaml
arazzo: 1.0.0
workflows:
  - workflowId: some-test
    x-speakeasy-test-targets-exclude:  # Generate for all except TypeScript
      - typescript
    # ...
```

### Rebuilding Tests from Scratch

Once tests are bootstrapped, the Arazzo document is only modified automatically when new operations are detected. To bootstrap all workflows from scratch:

```bash
speakeasy configure tests --rebuild
```

To selectively rebuild individual tests:

1. Delete the specific workflow from `.speakeasy/tests.arazzo.yaml`
2. Remove the corresponding entry in `.speakeasy/gen.lock` under `generatedTests`

For example, to rebuild a test for the `createLink` operation:

```yaml
generatedTests:
  createLink: "2025-05-21T12:47:32+10:00"  # Delete this line to rebuild
```

This approach preserves other manual changes to the arazzo document.

---

## GitHub Actions Integration

Automatically run tests on SDK pull requests via GitHub Actions.

### Setting Up GitHub Actions Check

After completing GitHub setup, run:

```bash
speakeasy configure tests
```

This produces a GitHub Actions workflow that enables running SDK tests as a check on pull requests:

```yaml
name: Test SDKs
permissions:
  checks: write
  contents: write
  pull-requests: write
  statuses: write

on:
  workflow_dispatch:
    inputs:
      target:
        description: Specific target to test
        type: string
  pull_request:
    paths:
      - "**"
    branches:
      - main

jobs:
  test:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/sdk-test.yaml@v15
    with:
      target: ${{ github.event.inputs.target }}
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
```

### Ensuring Tests Run on Automated PR Creation

> **Warning**: Pull requests created by the action using the default GITHUB_TOKEN cannot trigger other workflows. When on: pull_request or on: push workflows act as checks on pull requests, they will not run by default.

To ensure testing checks run when an SDK PR is created, implement one of:

**Installing the Speakeasy GitHub App:**

Install the Speakeasy GitHub App and grant access to the SDK repository. This enables triggering testing runs after PR creation. Visit https://github.com/apps/speakeasy-github or follow instructions in the CLI or dashboard.

**Setting up a GitHub PAT:**

Create a GitHub Personal Access Token (PAT) for creating PRs:

1. Create a fine-grained PAT with Pull requests Read/Write permissions
2. Ensure it has access to the SDK repository
3. Set to no expiration (recommended)
4. In SDK repositories, navigate to Settings > Secrets and variables > Actions
5. Save the PAT as a Repository secret named `PR_CREATION_PAT`
6. In all `sdk_generation.yaml` workflows, add the token as a secret:

```yaml
secrets:
  github_access_token: ${{ secrets.GITHUB_TOKEN }}
  speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
  pr_creation_pat: ${{ secrets.PR_CREATION_PAT }}
```

### Running in Direct Mode

If the generation action runs in `direct` mode where SDK updates get immediately pushed to main, testing runs as part of the generation action. If tests fail, the generation action fails and won't push SDK changes to main.

---

## OpenAPI Examples in Tests

The definition of each operation determines what data is used in generated testing. Test generation automatically uses defined examples when available. In the absence of examples, test generation attempts to use realistic values based on `type`, `format`, and property name.

### Example Property

By default, a single test is created based on `example` properties found in operation `parameters`, `requestBody`, and `responses`.

Example:

```yaml
components:
  schemas:
    Pet:
      required:
        - name
        - photoUrls
      type: object
      properties:
        id:
          type: integer
          format: int64
          example: 10
        name:
          type: string
          example: doggie
        photoUrls:
          type: array
          items:
            type: string
```

This creates a test with:

```yaml
id: 10
name: doggie
photoUrls:
  - <value>
```

### Examples Property

Multiple tests for an operation can be defined using the `examples` property, which is a mapping of example name keys to example values. Ensure the same example name key is used across all necessary `parameters`, `requestBody`, and `responses` parts of the operation.

Example:

```yaml
paths:
  /pet:
    post:
      operationId: addPet
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Pet"
            examples:
              fido:
                summary: fido request
                value:
                  name: Fido
                  photoUrls:
                    - https://www.example.com/fido.jpg
                  status: available
              rover:
                summary: rover request
                value:
                  name: Rover
                  photoUrls:
                    - https://www.example.com/rover1.jpg
                  status: pending
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Pet"
              examples:
                fido:
                  value:
                    id: 1
                    name: Fido
                rover:
                  value:
                    id: 2
                    name: Rover
```

This creates two tests: one for `fido` and one for `rover`.

### Ignoring Data

Data properties can be explicitly ignored in testing via `x-speakeasy-test-ignore`:

```yaml
paths:
  /example:
    get:
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: string
                  other:
                    type: string
                    x-speakeasy-test-ignore: true
```

---

## Mock Server

By default, tests run against Speakeasy's mock server at `http://localhost:18080`. The mock server validates SDK functionality but does not guarantee API correctness.

### Disabling Mock Server

If all tests are configured to run against other server URLs, disable mock server generation in `.speakeasy/gen.yaml`:

```yaml
generation:
  mockServer:
    disabled: true
```

---

## Pre-defined TODO List

When setting up SDK contract testing, initialize the TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Enable test generation with speakeasy configure tests | Enabling test generation |
| 2 | Review generated .speakeasy/tests.arazzo.yaml | Reviewing generated tests |
| 3 | Identify operations to disable testing for | Identifying operations to disable |
| 4 | Add x-speakeasy-test: false to disabled operations | Disabling specific operations |
| 5 | Run speakeasy test locally | Running tests locally |
| 6 | Configure GitHub Actions workflow | Configuring GitHub Actions |
| 7 | Set up PR_CREATION_PAT or Speakeasy GitHub App | Setting up PR automation |
| 8 | Run full test suite in CI | Running tests in CI |

**Usage:**
```
TodoWrite([
  {content: "Enable test generation with speakeasy configure tests", status: "pending", activeForm: "Enabling test generation"},
  {content: "Review generated .speakeasy/tests.arazzo.yaml", status: "pending", activeForm: "Reviewing generated tests"},
  {content: "Identify operations to disable testing for", status: "pending", activeForm: "Identifying operations to disable"},
  {content: "Add x-speakeasy-test: false to disabled operations", status: "pending", activeForm: "Disabling specific operations"},
  {content: "Run speakeasy test locally", status: "pending", activeForm: "Running tests locally"},
  {content: "Configure GitHub Actions workflow", status: "pending", activeForm: "Configuring GitHub Actions"},
  {content: "Set up PR_CREATION_PAT or Speakeasy GitHub App", status: "pending", activeForm: "Setting up PR automation"},
  {content: "Run full test suite in CI", status: "pending", activeForm: "Running tests in CI"}
])
```

**Related documentation:**
- `./arazzo-testing.md` - Custom test workflows with Arazzo
- `./integration-testing.md` - Traditional SDK integration tests
- `../spec-first/overlays.md` - Using overlays to disable tests
- `../plans/sdk-generation.md` - Full SDK generation workflow
