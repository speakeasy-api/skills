---
short_description: "Go SDK generation guide"
long_description: |
  Comprehensive guide for generating Go SDKs with Speakeasy.
  Includes SDK hooks for customization, interface generation for testing,
  Kubernetes integration, and production patterns from real-world SDKs.
source:
  repo: "Kong/sdk-konnect-go"
  path: "internal/hooks/, test/, Makefile"
  ref: "main"
  last_reconciled: "2025-12-11"
---

# Go SDK Generation

## SDK Overview

Speakeasy Go SDKs are idiomatic Go libraries that follow Go community conventions and best practices.

Core features:
- Strongly typed with full Go generics support
- Minimal dependencies
- Context-aware with proper cancellation support
- Structured error handling
- Built-in retry support with configurable backoff
- Pagination helpers

## Go Package Structure

```
.
├── .speakeasy/
│   ├── gen.yaml          # Generation configuration
│   ├── gen.lock          # Version lock
│   └── workflow.yaml     # Build workflow
├── internal/
│   ├── hooks/            # SDK hooks (customizable)
│   └── utils/            # Internal utilities
├── models/
│   ├── components/       # Shared types
│   ├── operations/       # Request/response types
│   └── sdkerrors/        # Error types
├── pkg/                  # Public utilities (optional)
├── sdk.go                # Main SDK entry point
├── *.go                  # Operation files (one per tag)
└── go.mod
```

## SDK Hooks

SDK hooks allow you to intercept and modify requests/responses without modifying generated code. Hooks are the primary extension mechanism for Go SDKs.

### Hook Types

| Hook | Trigger | Use Case |
|------|---------|----------|
| `sdkInitHook` | SDK initialization | Modify base URL, HTTP client |
| `beforeRequestHook` | Before each request | Add headers, rewrite URLs, logging |
| `afterSuccessHook` | After successful response | Transform response, metrics |
| `afterErrorHook` | After error | Error transformation, alerting |

### Hook Infrastructure

The hook system is generated in `internal/hooks/hooks.go`:

```go
type Hooks struct {
    sdkInitHooks      []sdkInitHook
    beforeRequestHook []beforeRequestHook
    afterSuccessHook  []afterSuccessHook
    afterErrorHook    []afterErrorHook
}

type BeforeRequestContext struct {
    HookContext
}

type HookContext struct {
    SDK              any
    SDKConfiguration config.SDKConfiguration
    BaseURL          string
    Context          context.Context
    OperationID      string
    OAuth2Scopes     []string
    SecuritySource   func(context.Context) (interface{}, error)
}
```

### Registering Hooks

Register hooks in `internal/hooks/registration.go`:

```go
func initHooks(h *Hooks) {
    // Custom user agent
    h.registerBeforeRequestHook(&UserAgentPreRequestHook{})

    // URL rewriting for multi-region APIs
    h.registerBeforeRequestHook(&GlobalAPIURLRequestHook{})

    // Environment-controlled debug logging
    if os.Getenv("SDK_HTTP_DUMP_REQUEST") == "true" {
        h.registerBeforeRequestHook(&HTTPDumpRequestHook{})
    }

    if os.Getenv("SDK_HTTP_DUMP_RESPONSE") == "true" {
        h.registerAfterSuccessHook(&HTTPDumpResponseHook{})
    }
}
```

### Common Hook Patterns

**URL Rewriting for Multi-Region APIs:**

```go
type GlobalAPIURLRequestHook struct{}

func (h *GlobalAPIURLRequestHook) BeforeRequest(
    hookCtx BeforeRequestContext,
    req *http.Request,
) (*http.Request, error) {
    // Route specific operations to global API
    switch hookCtx.OperationID {
    case "get-users-me", "get-organizations-me":
        req.URL.Host = "global.api.example.com"
        req.Host = "global.api.example.com"
    }
    return req, nil
}
```

**Custom Headers:**

```go
type CustomHeaderHook struct {
    HeaderName  string
    HeaderValue string
}

func (h *CustomHeaderHook) BeforeRequest(
    hookCtx BeforeRequestContext,
    req *http.Request,
) (*http.Request, error) {
    req.Header.Set(h.HeaderName, h.HeaderValue)
    return req, nil
}
```

**Debug Logging:**

```go
type HTTPDumpRequestHook struct{}

func (h *HTTPDumpRequestHook) BeforeRequest(
    hookCtx BeforeRequestContext,
    req *http.Request,
) (*http.Request, error) {
    dump, _ := httputil.DumpRequestOut(req, true)
    log.Printf("Request:\n%s", dump)
    return req, nil
}
```

---

## Testing with Interfaces and Mocks

For production Go SDKs, generate interfaces and mocks to enable unit testing of code that uses the SDK.

### Overview

The pattern uses two tools:
- `ifacemaker` - Generates Go interfaces from SDK structs
- `mockery` - Generates mock implementations from interfaces

```
SDK struct (Consumers)
  → ifacemaker → Interface (ConsumersSDK)
    → mockery → Mock (MockConsumersSDK)
```

### Tool Setup

Add tools to your Makefile:

```makefile
IFACEMAKER_VERSION = v1.2.0
IFACEMAKER = $(PROJECT_DIR)/bin/ifacemaker

.PHONY: ifacemaker
ifacemaker:
    go install github.com/vburenin/ifacemaker@$(IFACEMAKER_VERSION)

MOCKERY_VERSION = v2.40.0
MOCKERY = $(PROJECT_DIR)/bin/mockery

.PHONY: mockery
mockery:
    go install github.com/vektra/mockery/v2@$(MOCKERY_VERSION)
```

### Interface Generation

Generate interfaces for SDK structs:

```makefile
TYPES_TO_MOCK := \
    Consumers Services Routes Plugins \
    ControlPlanes Users Teams

.PHONY: _generate.ifacemaker
_generate.ifacemaker:
    @$(eval LOWERCASE_STRUCT := $(shell echo $(STRUCT) | tr 'A-Z' 'a-z'))
    $(IFACEMAKER) \
        --file $(LOWERCASE_STRUCT).go \
        --struct $(STRUCT) \
        --iface $(STRUCT)SDK \
        --iface-comment "$(STRUCT)SDK is a generated interface." \
        --output $(LOWERCASE_STRUCT)_i.go \
        -p sdkpackage

.PHONY: generate.interfaces
generate.interfaces: ifacemaker
    @$(foreach s, $(TYPES_TO_MOCK), \
        $(MAKE) _generate.ifacemaker STRUCT=$(s);)
```

**Generated Interface Example (`consumers_i.go`):**

```go
// ConsumersSDK is a generated interface.
type ConsumersSDK interface {
    ListConsumer(ctx context.Context, request operations.ListConsumerRequest, opts ...operations.Option) (*operations.ListConsumerResponse, error)
    CreateConsumer(ctx context.Context, controlPlaneID string, consumer components.Consumer, opts ...operations.Option) (*operations.CreateConsumerResponse, error)
    DeleteConsumer(ctx context.Context, controlPlaneID string, consumerID string, opts ...operations.Option) (*operations.DeleteConsumerResponse, error)
    GetConsumer(ctx context.Context, consumerID string, controlPlaneID string, opts ...operations.Option) (*operations.GetConsumerResponse, error)
}
```

### Mock Generation

Configure mockery in `.mockery.yaml`:

```yaml
dir: 'test/mocks/'
structname: Mock{{ .InterfaceName }}
pkgname: mocks
template: testify
filename: 'zz_generated.{{base .InterfaceFile }}'
force-file-write: true
include-auto-generated: true
packages:
  github.com/yourorg/your-sdk:
    config:
      include-interface-regex: .*SDK$
```

Generate mocks:

```makefile
.PHONY: generate.mocks
generate.mocks: mockery
    GODEBUG=gotypesalias=0 $(MOCKERY)
```

### Using Mocks in Tests

```go
func TestMyService(t *testing.T) {
    // Create mock
    mockConsumers := mocks.NewMockConsumersSDK(t)

    // Set expectations
    mockConsumers.EXPECT().
        CreateConsumer(
            mock.Anything,
            "control-plane-id",
            mock.AnythingOfType("components.Consumer"),
        ).
        Return(&operations.CreateConsumerResponse{
            Consumer: &components.Consumer{
                ID:   "consumer-123",
                Name: "test-consumer",
            },
        }, nil)

    // Use mock in your code
    result, err := mockConsumers.CreateConsumer(
        context.Background(),
        "control-plane-id",
        components.Consumer{Name: "test-consumer"},
    )

    require.NoError(t, err)
    assert.Equal(t, "consumer-123", result.Consumer.ID)

    // Verify expectations were met
    mockConsumers.AssertExpectations(t)
}
```

---

## Kubernetes Integration

For SDKs used in Kubernetes operators, generate `DeepCopy()` methods using controller-gen.

### Setup

Add controller-gen to your Makefile:

```makefile
CONTROLLER_GEN_VERSION = v0.14.0
CONTROLLER_GEN = $(PROJECT_DIR)/bin/controller-gen

.PHONY: controller-gen
controller-gen:
    go install sigs.k8s.io/controller-tools/cmd/controller-gen@$(CONTROLLER_GEN_VERSION)
```

### DeepCopy Generation

The pattern injects kubebuilder markers, runs controller-gen, then restores original files:

```makefile
KUBEBUILDER_MARKER = +kubebuilder:object:generate=true

.PHONY: generate.deepcopy
generate.deepcopy: controller-gen
    # Inject markers into types that need DeepCopy
    $(SED) -i 's#\(type CreateRequest struct\)#// $(KUBEBUILDER_MARKER)\n\1#g' \
        models/components/createrequest.go
    $(SED) -i 's#\(type Route struct\)#// $(KUBEBUILDER_MARKER)\n\1#g' \
        models/components/route.go

    # Generate DeepCopy methods
    $(CONTROLLER_GEN) object paths=./models/components/
    go mod tidy

    # Restore original files (remove markers from source)
    git checkout -- models/components/*.go
```

### Usage in CRDs

After generation, SDK types can be embedded in Kubernetes CRDs:

```go
type MyResourceSpec struct {
    // SDK type with DeepCopy support
    Route components.Route `json:"route,omitempty"`
}
```

---

## Configuration Options

### gen.yaml Settings

```yaml
go:
  version: 0.15.0
  packageName: github.com/yourorg/your-sdk

  # Method parameters
  maxMethodParams: 2
  methodArguments: require-security-and-request

  # Response handling
  responseFormat: envelope
  clientServerStatusCodesAsErrors: true

  # Security
  flattenGlobalSecurity: true

  # Import paths
  imports:
    option: openapi
    paths:
      callbacks: models/callbacks
      errors: models/sdkerrors
      operations: models/operations
      shared: models/components
      webhooks: models/webhooks
```

| Setting | Default | Description |
|---------|---------|-------------|
| `maxMethodParams` | 0 | Max params before request object is used |
| `responseFormat` | flat | Response structure: `flat` or `envelope` |
| `clientServerStatusCodesAsErrors` | true | Treat 4xx/5xx as errors |
| `flattenGlobalSecurity` | true | Simplify security configuration |
| `methodArguments` | infer | How method args are generated |

---

## Complete SDK Generation Pipeline

A production Go SDK build pipeline:

```makefile
.PHONY: generate.sdk
generate.sdk: speakeasy
    # Generate SDK
    speakeasy run --skip-versioning --skip-testing --minimal
    git add --update .

    # Post-processing
    $(MAKE) generate.deepcopy
    $(MAKE) _generate.omitempty  # Fix any omitempty issues

    # Tidy dependencies
    go mod tidy

.PHONY: generate.all
generate.all: generate.sdk generate.interfaces generate.mocks

.PHONY: test
test: test.unit test.integration

.PHONY: test.unit
test.unit:
    go test -v -race ./internal/...

.PHONY: test.integration
test.integration:
    SDK_TEST_RUN_ID=$(shell openssl rand -hex 8) \
        go test -v -race ./test/integration/...
```

---

## Pre-defined TODO List

When generating a Go SDK, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Configure gen.yaml for Go target | Configuring gen.yaml for Go target |
| 2 | Set package name and module path | Setting package name and module path |
| 3 | Configure maxMethodParams | Configuring maxMethodParams |
| 4 | Generate SDK with speakeasy run | Generating SDK |
| 5 | Implement SDK hooks if needed | Implementing SDK hooks |
| 6 | Set up interface generation (ifacemaker) | Setting up interface generation |
| 7 | Configure mockery for mock generation | Configuring mockery |
| 8 | Generate interfaces and mocks | Generating interfaces and mocks |
| 9 | Set up integration test infrastructure | Setting up integration tests |
| 10 | Test SDK compilation | Testing SDK compilation |

**Usage:**
```
TodoWrite([
  {content: "Configure gen.yaml for Go target", status: "pending", activeForm: "Configuring gen.yaml for Go target"},
  {content: "Set package name and module path", status: "pending", activeForm: "Setting package name and module path"},
  {content: "Configure maxMethodParams", status: "pending", activeForm: "Configuring maxMethodParams"},
  {content: "Generate SDK with speakeasy run", status: "pending", activeForm: "Generating SDK"},
  {content: "Implement SDK hooks if needed", status: "pending", activeForm: "Implementing SDK hooks"},
  {content: "Set up interface generation (ifacemaker)", status: "pending", activeForm: "Setting up interface generation"},
  {content: "Configure mockery for mock generation", status: "pending", activeForm: "Configuring mockery"},
  {content: "Generate interfaces and mocks", status: "pending", activeForm: "Generating interfaces and mocks"},
  {content: "Set up integration test infrastructure", status: "pending", activeForm: "Setting up integration tests"},
  {content: "Test SDK compilation", status: "pending", activeForm: "Testing SDK compilation"}
])
```

**Nested workflows:**
- See `plans/sdk-generation.md` for the full SDK generation workflow
- See `sdk-testing/integration-testing.md` for integration test patterns
