---
name: generate-sdk-for-go
description: >-
  Use when generating a Go SDK with Speakeasy. Covers gen.yaml configuration,
  SDK hooks, interface generation for testing, mock generation, Kubernetes integration.
  Triggers on "Go SDK", "generate Go", "golang client", "Go interfaces",
  "mockery", "ifacemaker", "Kubernetes operator SDK".
license: Apache-2.0
---

# Generate SDK for Go

Configure and generate idiomatic Go SDKs with Speakeasy, featuring hooks, interface generation for testing, and Kubernetes operator integration.

## When to Use

- Generating a new Go SDK from an OpenAPI spec
- Configuring Go-specific gen.yaml options
- Setting up SDK hooks for custom behavior
- Generating interfaces and mocks for testing
- Integrating with Kubernetes operators
- User says: "Go SDK", "golang client", "Go interfaces", "mockery"

## Quick Start

```bash
speakeasy quickstart --skip-interactive --output console \
  -s openapi.yaml -t go -n "MySDK" -p "github.com/myorg/my-sdk"
```

## Essential gen.yaml Configuration

```yaml
go:
  version: 0.1.0
  packageName: github.com/myorg/my-sdk

  # Method signatures
  maxMethodParams: 2
  methodArguments: require-security-and-request

  # Response handling
  responseFormat: envelope
  clientServerStatusCodesAsErrors: true

  # Security
  flattenGlobalSecurity: true
```

## Package Structure

```
├── internal/hooks/     # SDK hooks (customizable)
├── models/
│   ├── components/     # Shared types
│   ├── operations/     # Request/response types
│   └── sdkerrors/      # Error types
├── sdk.go              # Main entry point
└── *.go                # Operation files (per tag)
```

## SDK Hooks

Register hooks in `internal/hooks/registration.go`:

```go
func initHooks(h *Hooks) {
    h.registerBeforeRequestHook(&CustomHeaderHook{})
}

type CustomHeaderHook struct{}

func (h *CustomHeaderHook) BeforeRequest(
    ctx BeforeRequestContext, req *http.Request,
) (*http.Request, error) {
    req.Header.Set("X-Custom", "value")
    return req, nil
}
```

## Interface Generation for Testing

Generate interfaces with ifacemaker, then mocks with mockery:

```makefile
# Install tools
go install github.com/vburenin/ifacemaker@latest
go install github.com/vektra/mockery/v2@latest

# Generate interface
ifacemaker --file consumers.go --struct Consumers \
  --iface ConsumersSDK --output consumers_i.go

# Generate mock (configure in .mockery.yaml)
mockery
```

**Generated interface:**
```go
type ConsumersSDK interface {
    List(ctx context.Context, req ListRequest) (*ListResponse, error)
    Create(ctx context.Context, consumer Consumer) (*CreateResponse, error)
}
```

**Using mocks in tests:**
```go
func TestMyService(t *testing.T) {
    mock := mocks.NewMockConsumersSDK(t)
    mock.EXPECT().Create(mock.Anything, mock.AnythingOfType("Consumer")).
        Return(&CreateResponse{ID: "123"}, nil)

    // Use mock in your code
    result, err := mock.Create(ctx, Consumer{Name: "test"})
    require.NoError(t, err)
}
```

## Kubernetes Integration

Generate DeepCopy methods for CRD embedding:

```makefile
# Install controller-gen
go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest

# Add kubebuilder markers and generate
sed -i 's/type Route struct/\/\/ +kubebuilder:object:generate=true\ntype Route struct/' \
    models/components/route.go
controller-gen object paths=./models/components/
```

## Common Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `maxMethodParams` | 0 | Max params before request object |
| `responseFormat` | flat | `flat` or `envelope` |
| `methodArguments` | infer | How args are generated |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Interface not generated | Ensure struct is exported (capitalized) |
| Mock expectations fail | Check mock.Anything vs specific values |
| DeepCopy missing | Run controller-gen with markers |

## Related Skills

- `start-new-sdk-project` - Initial SDK setup
- `customize-sdk-hooks` - Detailed hook patterns
- `setup-sdk-testing` - Integration testing
