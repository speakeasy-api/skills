---
short_description: Configure SDK authentication with global and per-operation security
long_description: |
  Guide for configuring SDK authentication using OpenAPI security schemes.
  Covers global security, per-operation security overrides, environment variable
  integration, and security hoisting patterns for optimal developer experience.
source:
  - url: "https://speakeasy.com/docs/authentication-configuration"
    last_reconciled: "2025-12-11"
related:
  - "../plans/sdk-generation.md"
  - "./hooks.md"
  - "../sdk-languages/typescript.md"
  - "../sdk-languages/python.md"
  - "../sdk-languages/go.md"
---

# SDK Authentication Configuration

Configure SDK authentication using OpenAPI security schemes. Speakeasy SDKs support both global and per-operation security configurations.

## Global Security

Global security allows configuring the SDK once and reusing the security configuration for all subsequent calls.

### Defining Global Security

Define security at the root of the OpenAPI document:

```yaml
paths:
  /drinks:
    get:
      operationId: listDrinks
      summary: Get a list of drinks
      tags:
        - drinks
components:
  securitySchemes:
    api_key:
      type: apiKey
      name: api_key
      in: header
security:
  - api_key: []
```

### SDK Usage with Global Security

**CHOOSE ONE based on language:**

**TypeScript:**

```typescript
import { SDK } from "speakeasy";

const sdk = new SDK({
  apiKey: "<YOUR_API_KEY_HERE>",
});

const result = await sdk.drinks.listDrinks();
console.log(result);
```

**Python:**

```python
import sdk

s = sdk.SDK(
    api_key="<YOUR_API_KEY_HERE>",
)

res = s.drinks.list_drinks()
if res.drinks is not None:
    # Handle response
    pass
```

**Go:**

```go
package main

import (
    "context"
    "log"
    "speakeasy"
)

func main() {
    s := speakeasy.New(
        speakeasy.WithSecurity("<YOUR_API_KEY_HERE>"),
    )

    ctx := context.Background()
    res, err := s.Drinks.ListDrinks(ctx)
    if err != nil {
        log.Fatal(err)
    }
    if res.Drinks != nil {
        // Handle response
    }
}
```

**Java:**

```java
import dev.speakeasyapi.speakeasy.SDK;
import dev.speakeasyapi.speakeasy.models.operations.ListDrinksResponse;

public class Application {
    public static void main(String[] args) {
        try {
            SDK sdk = SDK.builder()
                .apiKey("<YOUR_API_KEY_HERE>")
                .build();

            ListDrinksResponse res = sdk.drinks().listDrinks()
                .call();

            if (res.drinks().isPresent()) {
                // Handle response
            }
        } catch (Exception e) {
            // Handle exception
        }
    }
}
```

**C#:**

```csharp
using Speakeasy;
using Speakeasy.Models.Components;

var sdk = new SDK(
    security: new Security() { ApiKey = "<YOUR_API_KEY_HERE>" }
);

try
{
    var res = await sdk.Drinks.ListDrinksAsync();

    if (res.Drinks != null)
    {
        // Handle response
    }
}
catch (Exception ex)
{
    // Handle exception
}
```

**PHP:**

```php
declare(strict_types=1);

require 'vendor/autoload.php';

use OpenAPI\OpenAPI;

$sdk = OpenAPI\SDK::builder()
    ->setSecurity(
        new OpenAPI\Security(
            apiKey: "<YOUR_API_KEY_HERE>"
        )
    )
    ->build();

try {
    $response = $sdk->drinks->listDrinks();

    if ($response->drinks !== null) {
        // Handle response
    }
} catch (Exception $e) {
    // Handle exception
}
```

**Ruby:**

```ruby
require 'openapi'

s = ::OpenApiSDK::SDK.new(
  security: ::OpenApiSDK::Models::Shared::Security.new(
    api_key: "<YOUR_API_KEY_HERE>"
  )
)

begin
  res = s.drinks.list_drinks

  unless res.drinks.nil?
    # Handle response
  end
rescue APIError
  # Handle exception
end
```

---

## Per-Operation Security

Per-operation security overrides global authentication settings for specific endpoints.

> **Note:** Security hoisting is enabled by default. When global security is not defined, Speakeasy automatically hoists the most commonly occurring operation-level security to be considered global. To opt out, set `auth.hoistGlobalSecurity: false` in your `gen.yaml`.

### Use Cases

- Operations that do not require authentication
- Operations that are part of an authentication flow (e.g., obtaining access tokens)
- Operations requiring different authentication schemes

### Defining Per-Operation Security

```yaml
paths:
  /drinks:
    get:
      operationId: listDrinks
      summary: Get a list of drinks
      security:
        - apiKey: []
      tags:
        - drinks
components:
  securitySchemes:
    api_key:
      type: apiKey
      name: api_key
      in: header
security:
  - {}
```

### SDK Usage with Per-Operation Security

**CHOOSE ONE based on language:**

**TypeScript:**

```typescript
import { SDK } from "speakeasy";

const sdk = new SDK();
const operationSecurity = "<YOUR_API_KEY_HERE>";

const result = await sdk.drinks.listDrinks(operationSecurity);
console.log(result);
```

**Python:**

```python
import sdk

s = sdk.SDK()
res = s.drinks.list_drinks("<YOUR_API_KEY_HERE>")

if res.drinks is not None:
    # Handle response
    pass
```

**Go:**

```go
package main

import (
    "context"
    "log"
    "speakeasy"
    "speakeasy/models/operations"
)

func main() {
    s := speakeasy.New()

    operationSecurity := operations.ListDrinksSecurity{
        APIKey: "<YOUR_API_KEY_HERE>",
    }

    ctx := context.Background()
    res, err := s.Drinks.ListDrinks(ctx, operationSecurity)
    if err != nil {
        log.Fatal(err)
    }
    if res.Drinks != nil {
        // Handle response
    }
}
```

**Java:**

```java
import dev.speakeasyapi.speakeasy.SDK;
import dev.speakeasyapi.speakeasy.models.operations.*;

public class Application {
    public static void main(String[] args) {
        try {
            SDK sdk = SDK.builder()
                .build();

            ListDrinksResponse res = sdk.drinks().listDrinks()
                .security(ListDrinksSecurity.builder()
                    .apiKey("<YOUR_API_KEY_HERE>")
                    .build())
                .call();

            if (res.drinks().isPresent()) {
                // Handle response
            }
        } catch (Exception e) {
            // Handle exception
        }
    }
}
```

**C#:**

```csharp
using Speakeasy;
using Speakeasy.Models.Components;

var sdk = new SDK(
    security: new Security() { ApiKey = "<YOUR_API_KEY_HERE>" }
);

try
{
    var res = await sdk.Drinks.ListDrinksAsync();

    if (res.Drinks != null)
    {
        // Handle response
    }
}
catch (Exception ex)
{
    // Handle exception
}
```

**PHP:**

```php
declare(strict_types=1);

require 'vendor/autoload.php';

use OpenAPI\OpenAPI;

$sdk = OpenAPI\SDK::builder()->build();

$requestSecurity = new ListDrinksSecurity(
    apiKey: '<YOUR_API_KEY_HERE>',
);

try {
    $response = $sdk->drinks->listDrinks(
        security: $requestSecurity,
    );
    // Handle response
} catch (Exception $e) {
    // Handle exception
}
```

**Ruby:**

```ruby
require 'openapi'

Models = ::OpenApiSDK::Models

s = ::OpenApiSDK::SDK.new

begin
  res = s.drinks.list_drinks(
    security: Models::Shared::ListDrinksSecurity.new(
      api_key: '<YOUR_API_KEY_HERE>',
    ),
  )

  unless res.drinks.nil?
    # Handle response
  end
rescue Models::Errors::APIError => e
  # Handle exception
  raise e
end
```

---

## Environment Variables

Speakeasy SDKs support environment variable-based configuration for global parameters and security options.

### Enabling Environment Variable Support

Configure the `envVarPrefix` in your `gen.yaml` file:

```yaml
typescript:
  envVarPrefix: SDK
```

```yaml
python:
  envVarPrefix: SDK
```

```yaml
go:
  envVarPrefix: SDK
```

### Environment Variable Naming

Global parameters and security fields are automatically mapped to environment variables:

**Format:** `{PREFIX}_{FIELD_NAME}`

**Examples:**
- `SDK_API_KEY` for an `apiKey` security field
- `SDK_SERVER_URL` for server URL override
- `SDK_TIMEOUT` for timeout configuration

### SDK Usage with Environment Variables

**TypeScript:**

```typescript
// Reads from SDK_API_KEY environment variable
const SDK = new SDK({
  apiKey: process.env["SDK_API_KEY"] ?? "",
});
```

**Python:**

```python
import os

# Reads from SDK_API_KEY environment variable
s = sdk.SDK(
    api_key=os.getenv("SDK_API_KEY", ""),
)
```

**Go:**

```go
import "os"

// Reads from SDK_API_KEY environment variable
s := sdk.New(
    sdk.WithSecurity(os.Getenv("SDK_API_KEY")),
)
```

> **Note:** Adding `envVarPrefix` may alter the structure of security options. Required global security becomes optional to allow setting it via environment variables.

---

## Security Scheme Types

Speakeasy supports all standard OpenAPI security schemes:

### API Key Authentication

```yaml
components:
  securitySchemes:
    api_key_header:
      type: apiKey
      name: X-API-Key
      in: header
    api_key_query:
      type: apiKey
      name: apiKey
      in: query
    api_key_cookie:
      type: apiKey
      name: session
      in: cookie
```

### HTTP Authentication

```yaml
components:
  securitySchemes:
    basic_auth:
      type: http
      scheme: basic
    bearer_auth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    digest_auth:
      type: http
      scheme: digest
```

### OAuth 2.0

```yaml
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.example.com/oauth/authorize
          tokenUrl: https://api.example.com/oauth/token
          scopes:
            read: Read access
            write: Write access
```

### OpenID Connect

```yaml
components:
  securitySchemes:
    openId:
      type: openIdConnect
      openIdConnectUrl: https://api.example.com/.well-known/openid-configuration
```

---

## Advanced Patterns

### Multiple Security Schemes (AND Logic)

Require multiple authentication methods:

```yaml
security:
  - api_key: []
    oauth2: [read]
```

The SDK requires both `api_key` AND `oauth2` authentication.

### Alternative Security Schemes (OR Logic)

Allow multiple authentication options:

```yaml
security:
  - api_key: []
  - oauth2: [read]
```

The SDK allows either `api_key` OR `oauth2` authentication.

### No Authentication (Empty Security)

Explicitly mark operations as not requiring authentication:

```yaml
security:
  - {}
```

### Security Hoisting Configuration

Control security hoisting behavior in `gen.yaml`:

```yaml
generation:
  auth:
    hoistGlobalSecurity: false  # Disable automatic security hoisting
```

---

## Best Practices

1. **Use global security**: Define global security for consistency across SDK operations
2. **Environment variables**: Always support environment variable configuration for production use
3. **Per-operation overrides**: Only use per-operation security for exceptions (public endpoints, auth flows)
4. **Security scheme naming**: Use descriptive names like `bearerAuth`, `apiKeyAuth`, not generic names
5. **OAuth scopes**: Define granular scopes for better access control
6. **Documentation**: Document required environment variables in README
7. **Sensitive data**: Never hardcode credentials; always use environment variables or SDK configuration
8. **Testing**: Test both global and per-operation security patterns

---

## Pre-defined TODO List

When configuring SDK authentication, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Define security schemes in OpenAPI components | Defining security schemes |
| 2 | Configure global security or per-operation security | Configuring security scope |
| 3 | Set envVarPrefix in gen.yaml | Setting environment variable prefix |
| 4 | Test SDK initialization with credentials | Testing SDK initialization |
| 5 | Test per-operation security overrides if applicable | Testing per-operation security |
| 6 | Test environment variable integration | Testing environment variables |
| 7 | Document authentication configuration in README | Documenting authentication |
| 8 | Verify security hoisting behavior | Verifying security hoisting |

**Usage:**
```
TodoWrite([
  {content: "Define security schemes in OpenAPI components", status: "pending", activeForm: "Defining security schemes"},
  {content: "Configure global security or per-operation security", status: "pending", activeForm: "Configuring security scope"},
  {content: "Set envVarPrefix in gen.yaml", status: "pending", activeForm: "Setting environment variable prefix"},
  {content: "Test SDK initialization with credentials", status: "pending", activeForm: "Testing SDK initialization"},
  {content: "Test per-operation security overrides if applicable", status: "pending", activeForm: "Testing per-operation security"},
  {content: "Test environment variable integration", status: "pending", activeForm: "Testing environment variables"},
  {content: "Document authentication configuration in README", status: "pending", activeForm: "Documenting authentication"},
  {content: "Verify security hoisting behavior", status: "pending", activeForm: "Verifying security hoisting"}
])
```
