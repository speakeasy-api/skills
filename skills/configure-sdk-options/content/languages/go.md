# Go SDK Configuration

Detailed gen.yaml configuration options for Go SDKs.

## gen.yaml Configuration

```yaml
go:
  version: 0.1.0
  packageName: github.com/myorg/my-sdk

  # Method signatures
  maxMethodParams: 2
  methodArguments: require-security-and-request

  # Response format
  responseFormat: envelope          # envelope or flat

  # Security flattening
  flattenGlobalSecurity: true
```

## Package Structure

```
github.com/myorg/my-sdk/
├── go.mod
├── go.sum
├── sdk.go                # Main SDK struct
├── models/
│   ├── operations/       # Request/response types
│   ├── shared/           # Shared types
│   └── errors/           # Error types
├── internal/
│   ├── hooks/            # Custom hooks (preserved)
│   │   └── registration.go
│   └── utils/            # Internal utilities
└── docs/                 # Generated documentation
```

## Method Arguments Options

### `require-security-and-request`

All operations require context, security, and request:

```go
result, err := sdk.Users.Create(ctx, security, request)
```

### `infer-optional-args` (Default)

Context required, security/request optional based on operation:

```go
// If operation has no security or body
result, err := sdk.Users.List(ctx)

// If operation requires both
result, err := sdk.Users.Create(ctx, security, request)
```

## Response Format Options

### `responseFormat: envelope`

Full response envelope with metadata:

```go
result, err := sdk.Users.Get(ctx, "123")
if err != nil {
    return err
}

// Access response metadata
fmt.Println(result.StatusCode)
fmt.Println(result.Headers)

// Access data
user := result.User
fmt.Println(user.Name)
```

### `responseFormat: flat`

Direct model access (simpler, less metadata):

```go
user, err := sdk.Users.Get(ctx, "123")
if err != nil {
    return err
}

fmt.Println(user.Name)
```

## Security Flattening

### `flattenGlobalSecurity: true`

Security configured at SDK level:

```go
sdk := mysdk.New(
    mysdk.WithSecurity(shared.Security{
        APIKey: "your-api-key",
    }),
)

// No security param needed
result, err := sdk.Users.List(ctx)
```

### `flattenGlobalSecurity: false`

Security passed per-operation:

```go
sdk := mysdk.New()

security := operations.ListUsersSecurity{
    APIKey: "your-api-key",
}
result, err := sdk.Users.List(ctx, security)
```

## SDK Initialization

```go
import (
    "context"
    mysdk "github.com/myorg/my-sdk"
    "github.com/myorg/my-sdk/models/shared"
)

func main() {
    // With functional options
    sdk := mysdk.New(
        mysdk.WithSecurity(shared.Security{
            APIKey: os.Getenv("API_KEY"),
        }),
        mysdk.WithServer("production"),
        mysdk.WithServerURL("https://api.example.com"),
        mysdk.WithTimeoutMs(30000),
    )

    ctx := context.Background()
    result, err := sdk.Users.List(ctx)
}
```

## Error Handling

```go
import (
    "errors"
    sdkerrors "github.com/myorg/my-sdk/models/errors"
)

result, err := sdk.Users.Get(ctx, "invalid-id")
if err != nil {
    var apiErr *sdkerrors.APIError
    if errors.As(err, &apiErr) {
        // Server returned error status
        fmt.Printf("Status: %d\n", apiErr.StatusCode)
        fmt.Printf("Body: %s\n", apiErr.Body)
        return
    }

    var sdkErr *sdkerrors.SDKError
    if errors.As(err, &sdkErr) {
        // Network, timeout, or other SDK error
        fmt.Printf("SDK error: %s\n", sdkErr.Message)
        return
    }

    // Unknown error
    return err
}
```

## Retries Configuration

```go
import (
    "github.com/myorg/my-sdk/retry"
)

sdk := mysdk.New(
    mysdk.WithRetryConfig(retry.Config{
        Strategy: "backoff",
        Backoff: &retry.BackoffStrategy{
            InitialInterval: 500,
            MaxInterval:     60000,
            Exponent:        1.5,
            MaxElapsedTime:  300000,
        },
        RetryConnectionErrors: true,
    }),
)

// Per-call override
result, err := sdk.Users.Create(ctx, request,
    operations.WithRetries(retry.Config{
        Strategy: "none",  // Disable retries for this call
    }),
)
```

## Pagination

For paginated endpoints:

```go
// Manual iteration
page, err := sdk.Users.List(ctx, operations.ListUsersRequest{
    Limit: mysdk.Int(50),
})
if err != nil {
    return err
}

for page != nil {
    for _, user := range page.Users {
        fmt.Println(user.Name)
    }

    page, err = page.Next()
    if err != nil {
        return err
    }
}
```

## Interface Generation for Testing

Generate interfaces using ifacemaker:

```bash
# Install tools
go install github.com/vburenin/ifacemaker@latest
go install github.com/vektra/mockery/v2@latest

# Generate interface from struct
ifacemaker \
  --file users.go \
  --struct Users \
  --iface UsersSDK \
  --output users_interface.go

# Generate mocks
mockery
```

Usage in tests:

```go
// users_interface.go (generated)
type UsersSDK interface {
    List(ctx context.Context) (*ListUsersResponse, error)
    Create(ctx context.Context, req CreateUserRequest) (*User, error)
    Get(ctx context.Context, id string) (*User, error)
}

// service.go
type UserService struct {
    sdk UsersSDK  // Interface, not concrete type
}

// service_test.go
func TestUserService(t *testing.T) {
    mock := mocks.NewUsersSDK(t)
    mock.On("Get", mock.Anything, "123").Return(&User{Name: "Alice"}, nil)

    svc := &UserService{sdk: mock}
    // ... test
}
```

## Kubernetes Operator Integration

For Kubernetes operators using kubebuilder:

```go
// Add kubebuilder markers to generated types
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
type User struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec              UserSpec   `json:"spec,omitempty"`
    Status            UserStatus `json:"status,omitempty"`
}

// Run controller-gen
//go:generate controller-gen object paths="./..."
```

## Custom Hooks

Create hooks in `internal/hooks/registration.go`:

```go
package hooks

import (
    "net/http"
)

func InitHooks(hooks *Hooks) {
    hooks.BeforeRequest(func(req *http.Request) (*http.Request, error) {
        req.Header.Set("X-Custom-Header", "value")
        return req, nil
    })

    hooks.AfterResponse(func(resp *http.Response, req *http.Request) (*http.Response, error) {
        log.Printf("%s %s: %d", req.Method, req.URL, resp.StatusCode)
        return resp, nil
    })

    hooks.OnError(func(err error, req *http.Request) error {
        log.Printf("Error: %v", err)
        return err
    })
}
```

## Debugging

```go
import (
    "log"
    "os"
)

sdk := mysdk.New(
    mysdk.WithDebugLogger(log.New(os.Stderr, "[SDK] ", log.LstdFlags)),
)
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Interface not generated | Ensure struct is exported (capitalized) |
| Context canceled errors | Check timeout settings, increase if needed |
| Import cycle | Use interfaces, move shared types to separate package |
| go mod tidy fails | Run `go mod download` first |
| SSL certificate errors | Configure custom `http.Client` with `InsecureSkipVerify` (dev only) |

## Publishing

Go modules are published by pushing tags:

```bash
# Tag version
git tag v1.0.0
git push origin v1.0.0

# Users install with
go get github.com/myorg/my-sdk@v1.0.0
```

Ensure `go.mod` has correct module path:
```go
module github.com/myorg/my-sdk

go 1.21
```
