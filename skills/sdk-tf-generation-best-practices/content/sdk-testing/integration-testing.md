---
short_description: "SDK integration testing patterns"
long_description: |
  Patterns for writing integration tests against live APIs for generated SDKs.
  Covers test infrastructure, environment configuration, resource lifecycle,
  labeling strategies, and CI/CD integration with real-world examples.
source:
  repo: "Kong/sdk-konnect-go"
  path: "test/integration/"
  ref: "main"
  last_reconciled: "2025-12-11"
---

# SDK Integration Testing

Integration tests verify that generated SDKs work correctly against live APIs. This guide covers patterns for building robust integration test suites.

## Test Infrastructure

### Directory Structure

```
test/
├── integration/
│   ├── sdk.go              # SDK factory with configuration
│   ├── envs.go             # Environment variable helpers
│   ├── funcs.go            # Naming and labeling utilities
│   ├── controlplane_test.go
│   ├── consumer_test.go
│   └── service_test.go
└── mocks/
    └── zz_generated.*.go   # Generated mocks (see go.md)
```

### SDK Factory Pattern

Create a centralized SDK factory that handles authentication and configuration:

```go
package integration

import (
    "testing"

    "github.com/stretchr/testify/require"

    sdk "github.com/yourorg/your-sdk"
    "github.com/yourorg/your-sdk/models/components"
)

// APIType distinguishes between API endpoints (if applicable)
type APIType byte

const (
    RegionalAPI APIType = iota
    GlobalAPI
)

// SDK returns a configured SDK instance for testing.
// Requires environment variables to be set.
func SDK(t *testing.T, apiType APIType, opts ...func(*sdk.SDK)) *sdk.SDK {
    token := RequireEnv(t, "API_TOKEN")
    url := RequireEnv(t, "API_URL")

    // Optionally transform URL based on API type
    if apiType == GlobalAPI {
        url = transformToGlobalURL(url)
    }

    client := sdk.New(
        sdk.WithSecurity(components.Security{
            BearerToken: sdk.String(token),
        }),
        sdk.WithServerURL(url),
    )

    // Apply any additional options
    for _, opt := range opts {
        opt(client)
    }

    require.NotNil(t, client)
    return client
}
```

### Environment Helpers

Centralize environment variable access with clear error messages:

```go
package integration

import (
    "os"
    "testing"

    "github.com/stretchr/testify/require"
)

const (
    TestRunIDEnv = "SDK_TEST_RUN_ID"
    APITokenEnv  = "API_TOKEN"
    APIURLEnv    = "API_URL"
)

// RequireEnv returns an environment variable or fails the test.
func RequireEnv(t *testing.T, key string) string {
    value := os.Getenv(key)
    require.NotEmptyf(t, value, "Environment variable %s is not set", key)
    return value
}

// TestRunID returns a unique identifier for this test run.
// Used for resource naming and cleanup.
func TestRunID(t *testing.T) string {
    return RequireEnv(t, TestRunIDEnv)
}
```

---

## Resource Lifecycle

### Cleanup with t.Cleanup()

Always register cleanup functions immediately after creating resources:

```go
func TestResourceCreateGetDelete(t *testing.T) {
    t.Parallel()

    sdk := SDK(t, RegionalAPI)
    ctx := context.Background()
    runID := TestRunID(t)

    // Create parent resource
    parent, err := sdk.Parents.Create(ctx, components.CreateParentRequest{
        Name:   NamePrefix(t) + "-" + runID,
        Labels: Labels(t),
    })
    require.NoError(t, err)

    // Register cleanup IMMEDIATELY after creation
    t.Cleanup(func() {
        _, err := sdk.Parents.Delete(ctx, parent.ID)
        require.NoError(t, err)
    })

    // Create child resource
    child, err := sdk.Children.Create(ctx, parent.ID, components.CreateChildRequest{
        Name: "child-resource",
    })
    require.NoError(t, err)

    // Child cleanup registered after parent cleanup
    // Go's t.Cleanup runs in LIFO order (child deleted before parent)
    t.Cleanup(func() {
        _, err := sdk.Children.Delete(ctx, parent.ID, *child.ID)
        require.NoError(t, err)
    })

    // Test assertions...
}
```

### Cleanup Order

Go's `t.Cleanup()` runs in LIFO (Last-In-First-Out) order:

```go
// Registration order:
t.Cleanup(deleteParent)   // Registered first
t.Cleanup(deleteChild)    // Registered second

// Execution order:
// 1. deleteChild runs first
// 2. deleteParent runs second
```

This matches typical resource dependency patterns.

---

## Naming and Labeling

### Unique Name Generation

Generate unique, identifiable names for test resources:

```go
package integration

import (
    "strings"
    "testing"
)

// NamePrefix returns a unique, traceable name for test resources.
// Format: sdk-{name}-test-integration-{TestName}
func NamePrefix(t *testing.T) string {
    name := "sdk-yourorg-test-integration-" + strings.ReplaceAll(t.Name(), "/", "_")

    // Many APIs have name length limits (e.g., 63 chars for Kubernetes)
    if len(name) > 63 {
        name = name[:63]
    }

    return strings.TrimSuffix(name, "_")
}
```

### Label-Based Resource Tracking

Use labels for identifying and cleaning up test resources:

```go
// Labels returns a consistent label set for test resources.
func Labels(t *testing.T) map[string]string {
    return map[string]string{
        "sdk-integration-test": "true",
        "test_name":            NamePrefix(t),
        "test_run_id":          TestRunID(t),
    }
}
```

Benefits:
- **Identification**: Easily identify test-created resources
- **Cleanup**: Query by labels to find orphaned resources
- **Debugging**: Trace resources back to specific test runs

### Tag-Based Filtering (Alternative)

Some APIs use tags instead of labels:

```go
func Tags(t *testing.T) []string {
    return []string{
        "sdk-integration-test",
        "test_name:" + NamePrefix(t),
        "test_run_id:" + TestRunID(t),
    }
}
```

---

## Test Patterns

### CRUD Test Pattern

Standard pattern for testing Create, Read, Update, Delete:

```go
func TestResourceCRUD(t *testing.T) {
    t.Parallel()

    sdk := SDK(t, RegionalAPI)
    ctx := context.Background()
    runID := TestRunID(t)

    // CREATE
    createReq := components.CreateResourceRequest{
        Name:   NamePrefix(t) + "-" + runID,
        Labels: Labels(t),
    }
    created, err := sdk.Resources.Create(ctx, createReq)
    require.NoError(t, err)
    t.Cleanup(func() {
        _, err := sdk.Resources.Delete(ctx, created.ID)
        require.NoError(t, err)
    })

    require.NotEmpty(t, created.ID)
    require.Equal(t, createReq.Name, created.Name)

    // READ
    fetched, err := sdk.Resources.Get(ctx, created.ID)
    require.NoError(t, err)
    require.Equal(t, created.ID, fetched.ID)
    require.Equal(t, created.Name, fetched.Name)

    // UPDATE (if supported)
    updateReq := components.UpdateResourceRequest{
        Name: createReq.Name + "-updated",
    }
    updated, err := sdk.Resources.Update(ctx, created.ID, updateReq)
    require.NoError(t, err)
    require.Equal(t, updateReq.Name, updated.Name)

    // DELETE is handled by t.Cleanup
}
```

### List with Filtering Test

Test list operations with various filter combinations:

```go
func TestResourceList(t *testing.T) {
    t.Parallel()

    sdk := SDK(t, RegionalAPI)

    testcases := []struct {
        name          string
        setup         func(ctx context.Context, t *testing.T)
        request       operations.ListResourcesRequest
        expectedError bool
        assert        func(t *testing.T, resp *operations.ListResourcesResponse)
    }{
        {
            name:    "no filter returns results",
            request: operations.ListResourcesRequest{},
            assert: func(t *testing.T, resp *operations.ListResourcesResponse) {
                require.NotNil(t, resp)
            },
        },
        {
            name: "filter by name returns matching resource",
            setup: func(ctx context.Context, t *testing.T) {
                // Create resource with known name
                req := components.CreateResourceRequest{
                    Name:   TestRunID(t) + "-filter-test",
                    Labels: Labels(t),
                }
                resp, err := sdk.Resources.Create(ctx, req)
                require.NoError(t, err)
                t.Cleanup(func() {
                    _, err := sdk.Resources.Delete(ctx, resp.ID)
                    require.NoError(t, err)
                })
            },
            request: operations.ListResourcesRequest{
                Filter: &components.FilterParameters{
                    Name: &components.NameFilter{
                        Eq: pkg.Ptr(TestRunID(t) + "-filter-test"),
                    },
                },
            },
            assert: func(t *testing.T, resp *operations.ListResourcesResponse) {
                require.NotNil(t, resp)
                require.Len(t, resp.Data, 1)
            },
        },
    }

    for _, tc := range testcases {
        t.Run(tc.name, func(t *testing.T) {
            ctx := context.Background()
            if tc.setup != nil {
                tc.setup(ctx, t)
            }

            resp, err := sdk.Resources.List(ctx, tc.request)
            if tc.expectedError {
                require.Error(t, err)
                return
            }

            require.NoError(t, err)
            if tc.assert != nil {
                tc.assert(t, resp)
            }
        })
    }
}
```

### Nested Resource Test

Test resources that depend on parent resources:

```go
func TestNestedResourceLifecycle(t *testing.T) {
    t.Parallel()

    sdk := SDK(t, RegionalAPI)
    ctx := context.Background()
    runID := TestRunID(t)

    // Create parent (e.g., ControlPlane)
    parent, err := sdk.ControlPlanes.Create(ctx, components.CreateControlPlaneRequest{
        Name:   NamePrefix(t) + "-" + runID,
        Labels: Labels(t),
    })
    require.NoError(t, err)
    t.Cleanup(func() {
        _, err := sdk.ControlPlanes.Delete(ctx, parent.ID)
        require.NoError(t, err)
    })

    // Create child (e.g., Consumer within ControlPlane)
    child, err := sdk.Consumers.Create(ctx, parent.ID, components.Consumer{
        Username: sdk.Pointer("test-user"),
        Tags:     Tags(t),
    })
    require.NoError(t, err)
    t.Cleanup(func() {
        _, err := sdk.Consumers.Delete(ctx, parent.ID, *child.ID)
        require.NoError(t, err)
    })

    // Verify child belongs to parent
    fetched, err := sdk.Consumers.Get(ctx, *child.ID, parent.ID)
    require.NoError(t, err)
    require.Equal(t, *child.ID, *fetched.ID)

    // List children within parent
    listed, err := sdk.Consumers.List(ctx, operations.ListConsumerRequest{
        ControlPlaneID: parent.ID,
        Tags:           sdk.String("sdk-integration-test,test_run_id:" + runID),
    })
    require.NoError(t, err)
    require.Len(t, listed.Data, 1)
}
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Integration Tests

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.21'

      - name: Run Integration Tests
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}
          API_URL: ${{ secrets.API_URL }}
          SDK_TEST_RUN_ID: ${{ github.run_id }}-${{ github.run_attempt }}
        run: |
          go test -v -race -timeout 30m ./test/integration/...
```

### Test Run Isolation

Use unique run IDs to isolate concurrent test runs:

```bash
# Generate unique run ID
export SDK_TEST_RUN_ID=$(openssl rand -hex 8)

# Or use CI-provided identifiers
export SDK_TEST_RUN_ID="${GITHUB_RUN_ID:-$(date +%s)}"

# Run tests
go test -v -race ./test/integration/...
```

### Scheduled Cleanup

For resources that might leak, implement scheduled cleanup:

```go
// cleanup_test.go - Run as a separate cleanup job
func TestCleanupOrphanedResources(t *testing.T) {
    if os.Getenv("RUN_CLEANUP") != "true" {
        t.Skip("Skipping cleanup (set RUN_CLEANUP=true to run)")
    }

    sdk := SDK(t, RegionalAPI)
    ctx := context.Background()

    // Find resources older than 24 hours with integration test labels
    cutoff := time.Now().Add(-24 * time.Hour)

    resources, err := sdk.Resources.List(ctx, operations.ListResourcesRequest{
        Filter: &components.FilterParameters{
            Labels: map[string]string{
                "sdk-integration-test": "true",
            },
        },
    })
    require.NoError(t, err)

    for _, r := range resources.Data {
        if r.CreatedAt.Before(cutoff) {
            t.Logf("Deleting orphaned resource: %s (created: %s)", r.ID, r.CreatedAt)
            _, err := sdk.Resources.Delete(ctx, r.ID)
            if err != nil {
                t.Logf("Failed to delete %s: %v", r.ID, err)
            }
        }
    }
}
```

---

## Example Projects as Integration Tests

SDK repositories can include example projects that serve dual purposes: documentation for users and compilation verification in CI. This pattern ensures examples stay up-to-date with SDK changes.

### Example Directory Structure

```
examples/
├── 01-basic-interaction/
│   ├── Program.cs           # C# example
│   └── BasicInteraction.csproj
├── 02-streaming/
│   ├── main.go              # Go example
│   └── go.mod
├── 03-function-calling/
│   ├── main.py              # Python example
│   └── pyproject.toml
├── README.md
└── run-all-examples.sh
```

### CI Validation Workflow

Validate all example projects compile on every PR. Example for C# (adapt build commands for Go/Python):

```yaml
# .github/workflows/examples_check.yaml
name: Check Examples

on:
  pull_request:
    types: [opened, reopened, synchronize]
  workflow_call:
    inputs:
      feature_branch:
        required: false
        type: string

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        ref: ${{ inputs.feature_branch || github.head_ref || github.ref }}

    - name: Build SDK and examples
      run: |
        dotnet build MyAPI.sln --configuration Release
        for csproj in examples/*/*.csproj; do
          dotnet build "$csproj" --configuration Release
        done
```

**Language-specific build commands:**
- **Go**: `go build -v ./...` in each example directory
- **Python**: `python -m py_compile "$dir/main.py"` after `pip install -e .`

### Chaining with SDK Generation

Run example validation after SDK regeneration:

```yaml
# .github/workflows/sdk_generation.yaml
jobs:
  generate:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/workflow-executor.yaml@v15
    with:
      mode: pr
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}

  check-examples:
    needs: generate
    uses: ./.github/workflows/examples_check.yaml
    with:
      feature_branch: ${{ github.event.inputs.feature_branch }}
```

### Benefits

- **Documentation stays current**: Broken examples fail CI
- **Catch regressions**: API changes that break examples are detected
- **User confidence**: Published examples are guaranteed to work
- **Low overhead**: Compilation checks are fast

> **Pattern Source:** Extracted from [speakeasy-sdks/gemini-api-csharp](https://github.com/speakeasy-sdks/gemini-api-csharp)

---

## Pre-defined TODO List

When setting up SDK integration tests, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Create test/integration directory structure | Creating test directory structure |
| 2 | Implement SDK factory (sdk.go) | Implementing SDK factory |
| 3 | Create environment helpers (envs.go) | Creating environment helpers |
| 4 | Add naming and labeling utilities (funcs.go) | Adding naming and labeling utilities |
| 5 | Write first CRUD test | Writing first CRUD test |
| 6 | Add list/filter tests | Adding list/filter tests |
| 7 | Test nested resource patterns | Testing nested resource patterns |
| 8 | Configure CI workflow | Configuring CI workflow |
| 9 | Add cleanup job for orphaned resources | Adding cleanup job |
| 10 | Run full integration test suite | Running full integration test suite |

**Usage:**
```
TodoWrite([
  {content: "Create test/integration directory structure", status: "pending", activeForm: "Creating test directory structure"},
  {content: "Implement SDK factory (sdk.go)", status: "pending", activeForm: "Implementing SDK factory"},
  {content: "Create environment helpers (envs.go)", status: "pending", activeForm: "Creating environment helpers"},
  {content: "Add naming and labeling utilities (funcs.go)", status: "pending", activeForm: "Adding naming and labeling utilities"},
  {content: "Write first CRUD test", status: "pending", activeForm: "Writing first CRUD test"},
  {content: "Add list/filter tests", status: "pending", activeForm: "Adding list/filter tests"},
  {content: "Test nested resource patterns", status: "pending", activeForm: "Testing nested resource patterns"},
  {content: "Configure CI workflow", status: "pending", activeForm: "Configuring CI workflow"},
  {content: "Add cleanup job for orphaned resources", status: "pending", activeForm: "Adding cleanup job"},
  {content: "Run full integration test suite", status: "pending", activeForm: "Running full integration test suite"}
])
```

**Related documentation:**
- `../sdk-languages/go.md` - Go SDK hooks, interfaces, and mocks
- `../plans/sdk-generation.md` - Full SDK generation workflow
