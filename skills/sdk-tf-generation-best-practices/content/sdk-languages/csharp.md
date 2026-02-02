---
short_description: "C# SDK generation guide"
long_description: |
  Comprehensive guide for generating C# SDKs with Speakeasy.
  Includes methodology, feature support, and language-specific configuration.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/docs/sdks/languages/csharp/"
  ref: "main"
  last_reconciled: "2025-12-11"
---

# C# SDK Generation

## SDK Overview

Speakeasy-generated C# SDKs provide a fully-typed, idiomatic .NET experience with modern async/await patterns, nullable reference types, and comprehensive error handling.

The core C# SDK features include:

- Full nullable reference type support (`#nullable enable`)
- Async/await patterns for all HTTP operations
- Server-Sent Events (SSE) streaming with `EventStream<T>`
- SDK hooks for custom request/response handling
- Retry support with configurable backoff strategies
- NodaTime integration for robust date/time handling
- Custom error hierarchies with branded exceptions
- Support for multiple .NET target frameworks

### C# Package Structure

```
src/
  {PackageName}/
    {SDKClassName}.cs
    SDKConfig.cs
    Hooks/
      HookTypes.cs
      SDKHooks.cs
      HookRegistration.cs    # Editable - preserved across regenerations
    Models/
      Components/
        ...
      Requests/
        ...
      Errors/
        {BaseErrorName}.cs
        {DefaultErrorName}.cs
        ResponseValidationException.cs
    Utils/
      SpeakeasyHttpClient.cs
      Retries/
        RetryConfig.cs
        BackoffStrategy.cs
      Sse/
        EventStream.cs
        SseStreamParser.cs
docs/
  ...
{PackageName}.csproj
{PackageName}.sln
README.md
```

## C# Type Safety

C# SDKs leverage .NET's strong type system with nullable reference types enabled by default. All generated models use proper C# conventions with XML documentation comments.

### Generated Models

Speakeasy generates C# classes with Newtonsoft.Json attributes for serialization:

```csharp
public class Drink
{
    /// <summary>
    /// The name of the drink.
    /// </summary>
    [JsonProperty("name")]
    public string Name { get; set; } = default!;

    /// <summary>
    /// The price of one unit of the drink in US cents.
    /// </summary>
    [JsonProperty("price")]
    public double Price { get; set; }

    /// <summary>
    /// The type of drink.
    /// </summary>
    [JsonProperty("type")]
    public DrinkType? Type { get; set; }

    /// <summary>
    /// The product code of the drink.
    /// </summary>
    [JsonProperty("productCode")]
    public string? ProductCode { get; set; }
}
```

### Nullable Reference Types

All C# SDKs enable nullable reference types:

```csharp
#nullable enable
```

This provides compile-time null safety and clear indication of which properties can be null.

## Server-Sent Events (SSE) Streaming

C# SDKs support SSE streaming through the `EventStream<T>` generic class, implementing `IDisposable` for proper resource cleanup.

### EventStream Usage

```csharp
using GoogleGenAI;
using GoogleGenAI.Models.Components;

var sdk = new GoogleGenAi(apiKey: "<YOUR_API_KEY_HERE>");

var result = await sdk.Interactions.CreateAsync(new InteractionInput
{
    Model = "gemini-2.5-flash",
    StringContent = "Tell me a story",
    Stream = true
});

// IMPORTANT: Always use a 'using' statement for proper resource cleanup
if (result.InteractionSseEvent != null)
{
    using (var eventStream = result.InteractionSseEvent)
    {
        InteractionSseEvent? eventData;
        // Next() returns null when stream ends
        while ((eventData = await eventStream.Next()) != null)
        {
            // Process each event
            Console.WriteLine(eventData.Data);
        }
    }
    // Dispose() called automatically here
}
```

### Stream Lifecycle

| Method | Return Value | Meaning |
|--------|--------------|---------|
| `Next()` | `T?` (non-null) | Event data available |
| `Next()` | `null` | Stream has ended |
| `Dispose()` | - | Release resources |

**Key Points:**
- Always wrap `EventStream<T>` in a `using` statement
- `Next()` is async - use `await`
- `null` return signals stream termination
- Supports sentinel values for explicit end-of-stream markers

## SDK Hooks System

C# SDK hooks provide lifecycle callbacks around HTTP operations. All hooks use async/await patterns.

### Hook Interfaces

| Interface | Signature | Purpose |
|-----------|-----------|---------|
| `ISDKInitHook` | `SDKConfig SDKInit(SDKConfig config)` | Modify SDK configuration at initialization |
| `IBeforeRequestHook` | `Task<HttpRequestMessage> BeforeRequestAsync(...)` | Modify request before sending |
| `IAfterSuccessHook` | `Task<HttpResponseMessage> AfterSuccessAsync(...)` | Process successful response |
| `IAfterErrorHook` | `Task<(HttpResponseMessage?, Exception?)> AfterErrorAsync(...)` | Handle error responses |

### HookContext Properties

All hooks receive a context object with:

```csharp
public class HookContext
{
    public SDKConfig SDKConfiguration { get; set; }
    public string BaseURL { get; set; }
    public string OperationID { get; set; }
    public List<string>? Oauth2Scopes { get; set; }
    public Func<object>? SecuritySource { get; set; }
}
```

### Hook Registration

Register hooks in `Hooks/HookRegistration.cs` (preserved across regenerations):

```csharp
namespace MyAPI.Hooks
{
    public static class HookRegistration
    {
        public static void InitHooks(IHooks hooks)
        {
            // Register your custom hooks here
            var tracingHook = new TracingHook();

            hooks.RegisterSDKInitHook(new ConfigurationHook());
            hooks.RegisterBeforeRequestHook(new CustomUserAgentHook());
            hooks.RegisterBeforeRequestHook(tracingHook);
            hooks.RegisterAfterSuccessHook(tracingHook);
            hooks.RegisterAfterErrorHook(tracingHook);
        }
    }
}
```

### Example: Custom User-Agent Hook

```csharp
public class CustomUserAgentHook : IBeforeRequestHook
{
    public Task<HttpRequestMessage> BeforeRequestAsync(BeforeRequestContext hookCtx, HttpRequestMessage request)
    {
        request.Headers.UserAgent.ParseAdd("myapi-csharp/" + request.Headers.UserAgent);
        return Task.FromResult(request);
    }
}
```

### FailEarlyException

Throw `FailEarlyException` to immediately halt the hook chain and stop request processing:

```csharp
public class ValidationHook : IBeforeRequestHook
{
    public Task<HttpRequestMessage> BeforeRequestAsync(
        BeforeRequestContext hookCtx,
        HttpRequestMessage request)
    {
        if (string.IsNullOrEmpty(request.Headers.Authorization?.ToString()))
        {
            // Immediately stop - don't call other hooks or send request
            throw new FailEarlyException();
        }
        return Task.FromResult(request);
    }
}
```

## Error Handling

C# SDKs generate a custom exception hierarchy with branded error classes.

### Exception Hierarchy

```
{BaseErrorName} (e.g., GoogleGenAiBaseException)
├── {DefaultErrorName} (e.g., GoogleGenAiDefaultException)
└── ResponseValidationException
```

### Base Exception Properties

```csharp
public class GoogleGenAiBaseException : Exception
{
    public override string Message { get; }
    public HttpRequestMessage Request { get; }
    public HttpResponseMessage Response { get; }
    public string Body { get; }
}
```

### Error Handling Example

```csharp
using GoogleGenAI;
using GoogleGenAI.Models.Errors;

var sdk = new GoogleGenAi(apiKey: "<YOUR_API_KEY_HERE>");

try
{
    var res = await sdk.Interactions.CreateAsync(new InteractionInput
    {
        Model = "gemini-2.5-flash",
        StringContent = "Hello world"
    });
    // Process response...
}
catch (GoogleGenAiBaseException ex)
{
    // All SDK exceptions inherit from this
    Console.WriteLine($"Status: {ex.Response.StatusCode}");
    Console.WriteLine($"Message: {ex.Message}");
    Console.WriteLine($"Body: {ex.Body}");
}
catch (HttpRequestException ex)
{
    // Network connectivity errors
    Console.WriteLine($"Network error: {ex.InnerException?.Message}");
}
```

## Retry Configuration

C# SDKs support automatic retries with configurable backoff strategies:

```csharp
var retryConfig = new RetryConfig(
    strategy: RetryConfig.RetryStrategy.BACKOFF,
    backoff: new BackoffStrategy(
        initialIntervalMs: 500,
        maxIntervalMs: 60000,
        maxElapsedTimeMs: 300000,
        exponent: 1.5
    ),
    retryConnectionErrors: true
);

var sdk = new GoogleGenAi(
    apiKey: "<YOUR_API_KEY_HERE>",
    retryConfig: retryConfig
);
```

### Retry Strategies

| Strategy | Behavior |
|----------|----------|
| `BACKOFF` | Exponential backoff with jitter |
| `NONE` | No retries (fail immediately) |

## Known Limitations

C# SDKs support all standard OpenAPI features. Currently no major limitations.

## Configuration Options

All C# SDK configuration is managed in the `gen.yaml` file under the `csharp` section.

### Version and General Configuration

```yaml
csharp:
  version: 1.0.0
  author: "Your Company"
  packageName: "MyAPI"
  dotnetVersion: net8.0
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| version | true | 0.0.1 | The current version of the SDK |
| packageName | true | - | The name of the NuGet package |
| author | false | "Speakeasy" | Author shown in package metadata |
| dotnetVersion | false | net8.0 | Target framework (e.g., `net6.0`, `net7.0`, `net8.0`) |

### SDK Class Naming

```yaml
generation:
  sdkClassName: MyApi
csharp:
  packageName: MyAPI
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| sdkClassName | false | SDK | The main SDK class name |
| packageName | true | - | Namespace and package name |

### Error Naming

```yaml
csharp:
  baseErrorName: MyApiException
  defaultErrorName: MyApiDefaultException
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| baseErrorName | false | SDKException | Base class for all SDK exceptions |
| defaultErrorName | false | SDKException | Default exception when no specific match |

### HTTP Client Configuration

```yaml
csharp:
  httpClientPrefix: Speakeasy
  clientServerStatusCodesAsErrors: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| httpClientPrefix | false | Speakeasy | Prefix for HTTP client class names |
| clientServerStatusCodesAsErrors | false | true | Treat 4xx/5xx as exceptions |

### Response Format

```yaml
csharp:
  responseFormat: envelope-http
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| responseFormat | false | flat | Response wrapper style: `flat`, `envelope`, `envelope-http` |

**Response Format Options:**

| Format | Description |
|--------|-------------|
| `flat` | Return deserialized response object directly |
| `envelope` | Wrap response with metadata |
| `envelope-http` | Include full `HttpResponseMessage` with response |

### NodaTime Date/Time Handling

```yaml
csharp:
  useNodatime: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| useNodatime | false | false | Use NodaTime instead of System.DateTime |

**Benefits of NodaTime:**
- Better timezone handling
- Clearer distinction between local and UTC times
- More robust date arithmetic
- Industry-standard for financial/scheduling applications

When enabled, adds `nodatime` NuGet package dependency.

### Security Configuration

```yaml
csharp:
  flattenGlobalSecurity: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| flattenGlobalSecurity | false | true | Inline security credentials in SDK constructor |

### Model Naming

```yaml
csharp:
  inputModelSuffix: input
  outputModelSuffix: output
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| inputModelSuffix | false | "" | Suffix for request model names |
| outputModelSuffix | false | "" | Suffix for response model names |

### Method Configuration

```yaml
csharp:
  maxMethodParams: 4
  flatteningOrder: parameters-first
  methodArguments: infer-optional-args
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| maxMethodParams | false | 9999 | Max parameters before using request object |
| flatteningOrder | false | parameters-first | Order of flattened parameters |
| methodArguments | false | require-security-and-request | Method argument generation strategy |

### Import Paths

```yaml
csharp:
  imports:
    option: openapi
    paths:
      callbacks: Models/Callbacks
      errors: Models/Errors
      operations: Models/Requests
      shared: Models/Components
      webhooks: Models/Webhooks
```

### Advanced Options

```yaml
csharp:
  enableCancellationToken: true
  enableSourceLink: true
  includeDebugSymbols: true
  disableNamespacePascalCasingApr2024: false
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| enableCancellationToken | false | false | Add CancellationToken parameters to async methods |
| enableSourceLink | false | false | Enable SourceLink for debugging |
| includeDebugSymbols | false | false | Include PDB files in package |
| disableNamespacePascalCasingApr2024 | false | false | Control namespace casing |

### Additional Dependencies

```yaml
csharp:
  additionalDependencies:
    - "Polly:8.0.0"
    - "Serilog:3.0.0"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| additionalDependencies | false | [] | Additional NuGet packages to include |

## Complete Configuration Example

```yaml
configVersion: 2.0.0
generation:
  sdkClassName: GoogleGenAi
  maintainOpenAPIOrder: true
  usageSnippets:
    optionalPropertyRendering: withExample
    sdkInitStyle: constructor
  fixes:
    nameResolutionDec2023: true
    nameResolutionFeb2025: true
    parameterOrderingFeb2024: true
    requestResponseComponentNamesFeb2024: true
    securityFeb2025: true
    sharedErrorComponentsApr2025: true
  auth:
    oAuth2ClientCredentialsEnabled: true
    oAuth2PasswordEnabled: true
    hoistGlobalSecurity: true
  tests:
    generateTests: false
    generateNewTests: true
csharp:
  version: 0.14.3
  author: Speakeasy
  baseErrorName: GoogleGenAiBaseException
  defaultErrorName: GoogleGenAiDefaultException
  dotnetVersion: net8.0
  flattenGlobalSecurity: true
  responseFormat: envelope-http
  useNodatime: true
  httpClientPrefix: Speakeasy
  clientServerStatusCodesAsErrors: true
  maxMethodParams: 4
  methodArguments: infer-optional-args
  flatteningOrder: parameters-first
  inputModelSuffix: input
  outputModelSuffix: output
  packageName: GoogleGenAI
  sourceDirectory: src
  imports:
    option: openapi
    paths:
      callbacks: Models/Callbacks
      errors: Models/Errors
      operations: Models/Requests
      shared: Models/Components
      webhooks: Models/Webhooks
```

## Example Projects Pattern

C# SDKs can include example projects for documentation and CI validation. See `sdk-testing/integration-testing.md` for the full pattern including CI workflows.

---

## Pre-defined TODO List

When configuring a C# SDK generation, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Review C# SDK feature requirements | Reviewing C# SDK feature requirements |
| 2 | Configure gen.yaml for C# target | Configuring gen.yaml for C# target |
| 3 | Set package name and version | Setting package name and version |
| 4 | Configure target .NET version | Configuring target .NET version |
| 5 | Set error class names (baseErrorName) | Setting error class names |
| 6 | Configure NodaTime if needed | Configuring NodaTime |
| 7 | Set response format (flat/envelope-http) | Setting response format |
| 8 | Test SDK compilation | Testing SDK compilation |
| 9 | Verify async methods work correctly | Verifying async methods |

**Usage:**
```
TodoWrite([
  {content: "Review C# SDK feature requirements", status: "pending", activeForm: "Reviewing C# SDK feature requirements"},
  {content: "Configure gen.yaml for C# target", status: "pending", activeForm: "Configuring gen.yaml for C# target"},
  {content: "Set package name and version", status: "pending", activeForm: "Setting package name and version"},
  {content: "Configure target .NET version", status: "pending", activeForm: "Configuring target .NET version"},
  {content: "Set error class names (baseErrorName)", status: "pending", activeForm: "Setting error class names"},
  {content: "Configure NodaTime if needed", status: "pending", activeForm: "Configuring NodaTime"},
  {content: "Set response format (flat/envelope-http)", status: "pending", activeForm: "Setting response format"},
  {content: "Test SDK compilation", status: "pending", activeForm: "Testing SDK compilation"},
  {content: "Verify async methods work correctly", status: "pending", activeForm: "Verifying async methods"}
])
```

**Nested workflows:**
- See `plans/sdk-generation.md` for the full SDK generation workflow
- See `spec-first/validation.md` for OpenAPI validation before generation
