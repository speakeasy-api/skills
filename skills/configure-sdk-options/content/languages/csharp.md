# C# SDK Configuration

Detailed gen.yaml configuration options for C# SDKs.

## gen.yaml Configuration

```yaml
csharp:
  version: 1.0.0
  packageName: MyOrg.MySDK
  dotnetVersion: "6.0"              # 6.0, 7.0, or 8.0
  baseErrorName: MySDKException     # Custom exception base class
```

## Package Structure

```
MySDK/
├── MyOrg.MySDK.csproj
├── SDK.cs                    # Main SDK class
├── Models/
│   ├── Operations/           # Request/response
│   ├── Shared/               # Shared models
│   └── Errors/               # Exception classes
├── Hooks/                    # Custom hooks (preserved)
│   └── HookRegistration.cs
└── docs/
```

## SDK Usage

```csharp
using MyOrg.MySDK;
using MyOrg.MySDK.Models.Shared;

var sdk = new SDK(security: new Security {
    ApiKey = "your-api-key"
});

// All operations are async
var user = await sdk.Users.GetAsync("123");
Console.WriteLine(user.Name);
```

## Security Configuration

```csharp
// API Key
var sdk = new SDK(security: new Security {
    ApiKey = "your-api-key"
});

// Bearer Token
var sdk = new SDK(security: new Security {
    BearerAuth = "your-token"
});

// OAuth2
var sdk = new SDK(security: new Security {
    OAuth2 = "your-oauth-token"
});
```

## Server Selection

```csharp
// Named server
var sdk = new SDK(server: Server.Production);

// Custom URL
var sdk = new SDK(serverUrl: "https://api.example.com");
```

## Async/Await Pattern

All SDK operations use async/await:

```csharp
// Single operation
var user = await sdk.Users.GetAsync("123");

// Multiple concurrent operations
var tasks = new[] {
    sdk.Users.GetAsync("1"),
    sdk.Users.GetAsync("2"),
    sdk.Users.GetAsync("3")
};
var users = await Task.WhenAll(tasks);

// With cancellation
var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
var user = await sdk.Users.GetAsync("123", cancellationToken: cts.Token);
```

## Error Handling

```csharp
using MyOrg.MySDK.Models.Errors;

try {
    var user = await sdk.Users.GetAsync("invalid-id");
}
catch (APIException e) {
    // Server returned error status
    Console.WriteLine($"Status: {e.StatusCode}");
    Console.WriteLine($"Body: {e.Body}");
}
catch (SDKException e) {
    // Network, timeout, or other SDK error
    Console.WriteLine($"SDK error: {e.Message}");
}
```

## Retries Configuration

```csharp
using MyOrg.MySDK.Utils;

var sdk = new SDK(
    retryConfig: new RetryConfig {
        Strategy = RetryStrategy.Backoff,
        Backoff = new BackoffStrategy {
            InitialInterval = 500,
            MaxInterval = 60000,
            Exponent = 1.5,
            MaxElapsedTime = 300000
        },
        RetryConnectionErrors = true
    }
);
```

## Timeouts

```csharp
// Global timeout
var sdk = new SDK(timeoutMs: 30000);

// Per-call timeout via CancellationToken
var cts = new CancellationTokenSource(TimeSpan.FromSeconds(60));
var user = await sdk.Users.CreateAsync(request, cancellationToken: cts.Token);
```

## Pagination

```csharp
// Auto-iterate all pages
await foreach (var user in sdk.Users.ListAsync(limit: 50)) {
    Console.WriteLine(user.Name);
}

// Manual pagination
var page = await sdk.Users.ListAsync(limit: 50);
while (page != null) {
    foreach (var user in page.Users) {
        Console.WriteLine(user.Name);
    }
    page = await page.NextAsync();
}
```

## Streaming (SSE)

```csharp
// Server-Sent Events
await foreach (var evt in sdk.Chat.CompleteAsync(new ChatRequest {
    Message = "Hello"
})) {
    Console.WriteLine(evt.Content);
}
```

## Custom Hooks

Create hooks in `Hooks/HookRegistration.cs`:

```csharp
using System.Net.Http;

namespace MyOrg.MySDK.Hooks;

public static class HookRegistration
{
    public static void InitHooks(Hooks hooks)
    {
        hooks.BeforeRequest += (request) => {
            request.Headers.Add("X-Custom-Header", "value");
            return request;
        };

        hooks.AfterResponse += (response, request) => {
            Console.WriteLine($"{request.Method} {request.RequestUri}: {response.StatusCode}");
            return response;
        };

        hooks.OnError += (error, request) => {
            Console.Error.WriteLine($"Error: {error.Message}");
            throw error;
        };
    }
}
```

## Dependency Injection

Register SDK with ASP.NET Core DI:

```csharp
// Program.cs
builder.Services.AddSingleton<SDK>(sp => new SDK(
    security: new Security {
        ApiKey = builder.Configuration["ApiKey"]
    }
));

// Controller
public class UsersController : ControllerBase
{
    private readonly SDK _sdk;

    public UsersController(SDK sdk) => _sdk = sdk;

    [HttpGet("{id}")]
    public async Task<IActionResult> Get(string id)
    {
        var user = await _sdk.Users.GetAsync(id);
        return Ok(user);
    }
}
```

## Debugging

```csharp
using Microsoft.Extensions.Logging;

var loggerFactory = LoggerFactory.Create(builder => {
    builder.AddConsole().SetMinimumLevel(LogLevel.Debug);
});

var sdk = new SDK(logger: loggerFactory.CreateLogger<SDK>());
```

## Publishing to NuGet

```bash
# Build release package
dotnet pack -c Release

# Publish
dotnet nuget push bin/Release/MyOrg.MySDK.1.0.0.nupkg \
    --api-key YOUR_API_KEY \
    --source https://api.nuget.org/v3/index.json
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Async deadlock | Use `await`, never `.Result` or `.Wait()` |
| SSL errors | Configure `HttpClientHandler.ServerCertificateCustomValidationCallback` |
| Serialization | Check `System.Text.Json` property names |
| Memory usage | Dispose SDK when done: `using var sdk = new SDK()` |
| .NET version mismatch | Check `TargetFramework` in `.csproj` |
