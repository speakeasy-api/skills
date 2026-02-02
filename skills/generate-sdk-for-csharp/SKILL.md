---
name: generate-sdk-for-csharp
description: >-
  Use when generating a C# SDK with Speakeasy. Covers gen.yaml configuration,
  async/await patterns, nullable reference types, NuGet publishing.
  Triggers on "C# SDK", "generate C#", "dotnet SDK", "NuGet publish",
  ".NET client library", "csharp SDK".
license: Apache-2.0
---

# Generate SDK for C#

Configure and generate idiomatic C# SDKs with Speakeasy, featuring async/await, nullable reference types, and .NET 6+ support.

## When to Use

- Generating a new C# SDK from an OpenAPI spec
- Configuring C#-specific gen.yaml options
- Setting up SDK hooks
- Publishing to NuGet
- User says: "C# SDK", ".NET SDK", "NuGet", "dotnet client"

## Quick Start

```bash
speakeasy quickstart --skip-interactive --output console \
  -s openapi.yaml -t csharp -n "MySDK" -p "MyOrg.MySDK"
```

## Essential gen.yaml Configuration

```yaml
csharp:
  version: 1.0.0
  packageName: MyOrg.MySDK
  dotnetVersion: "6.0"

  # Method signatures
  maxMethodParams: 4

  # Error handling
  responseFormat: flat
  clientServerStatusCodesAsErrors: true

  # Naming
  baseErrorName: MySDKException
  defaultErrorName: SDKException
```

## Package Structure

```
src/MyOrg.MySDK/
├── MySDK.cs              # Main SDK class
├── SDKConfig.cs          # Configuration
├── Hooks/
│   ├── HookTypes.cs      # Hook interfaces
│   ├── SDKHooks.cs       # Hook orchestrator
│   └── HookRegistration.cs  # Custom hooks (preserved)
├── Models/
│   ├── Components/       # Shared types
│   ├── Requests/         # Request types
│   └── Errors/           # Error types
└── Utils/
    └── Retry/            # Retry configuration
```

## Client Usage

```csharp
using MyOrg.MySDK;
using MyOrg.MySDK.Models.Components;

// Create client
var sdk = new MySDK(security: new Security {
    ApiKey = "your-api-key"
});

// Make API call
var response = await sdk.Resources.CreateAsync(new CreateRequest {
    Name = "my-resource"
});

if (response.Resource != null) {
    Console.WriteLine(response.Resource.Id);
}
```

## Async Patterns

All operations are async by default:

```csharp
// Async (recommended)
var result = await sdk.Users.ListAsync();

// With cancellation
var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
var result = await sdk.Users.ListAsync(cancellationToken: cts.Token);
```

## SDK Hooks

Register hooks in `Hooks/HookRegistration.cs`:

```csharp
public static class HookRegistration
{
    public static void RegisterHooks(SDKHooks hooks)
    {
        hooks.RegisterBeforeRequestHook(new CustomHeaderHook());
    }
}

public class CustomHeaderHook : IBeforeRequestHook
{
    public HttpRequestMessage BeforeRequest(
        BeforeRequestContext context,
        HttpRequestMessage request)
    {
        request.Headers.Add("X-Custom", "value");
        return request;
    }
}
```

## SSE Streaming

C# SDKs support Server-Sent Events with `EventStream<T>`:

```csharp
var stream = await sdk.Chat.CreateStreamAsync(request);

await foreach (var evt in stream)
{
    Console.Write(evt.Data.Content);
}
```

## NuGet Publishing

1. Configure package metadata in `.csproj`
2. Build: `dotnet pack -c Release`
3. Publish: `dotnet nuget push *.nupkg --source https://api.nuget.org/v3/index.json`

## Common Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `dotnetVersion` | 6.0 | Target .NET version |
| `packageName` | OpenAPI | NuGet package name |
| `baseErrorName` | SDKException | Base exception class |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Nullable warnings | Enable `#nullable enable` |
| Async deadlock | Use `await` not `.Result` |
| Missing NodaTime | Add `NodaTime` NuGet package |

## Related Skills

- `start-new-sdk-project` - Initial SDK setup
- `customize-sdk-hooks` - Hook implementation
- `setup-sdk-testing` - Testing patterns
