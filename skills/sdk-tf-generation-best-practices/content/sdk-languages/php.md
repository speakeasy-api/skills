---
short_description: "PHP SDK generation guide"
long_description: |
  Comprehensive guide for generating PHP SDKs with Speakeasy.
  Includes methodology, feature support, configuration options, and language-specific patterns.
source:
  repo: "dubinc/dub-php"
  path: "/"
  ref: "e8583f1"
  last_reconciled: "2025-12-11"
related:
  - "../plans/sdk-generation.md"
  - "../sdk-customization/hooks.md"
---

# PHP SDK Generation

Speakeasy-generated PHP SDKs are designed to be idiomatic, type-safe, and production-ready. They use modern PHP 8.2+ features including typed properties, attributes for serialization, and named arguments.

## SDK Overview

The core PHP SDK features include:

- **PHP 8.2+ Required**: Modern PHP with strict typing
- **Guzzle HTTP Client**: Industry-standard HTTP library
- **Builder Pattern**: Fluent SDK instantiation
- **PHP Attributes for Serialization**: Type-safe model serialization
- **Typed Errors**: Exception hierarchy with status-specific classes
- **Pagination Support**: Generator-based pagination for list operations
- **Retry Support**: Configurable retry strategies
- **Hook System**: Lifecycle hooks for customization

### PHP Package Structure

```
src/
├── {SDKClassName}.php          # Main SDK class
├── {SDKClassName}Builder.php   # Builder for SDK instantiation
├── SDKConfiguration.php        # Configuration container
├── Hooks/                      # Hook system
│   ├── SDKHooks.php            # Hook orchestrator
│   ├── HookRegistration.php    # CUSTOM: Your hooks
│   └── [hook interfaces]
├── Utils/                      # Utility classes
│   └── Retry/                  # Retry configuration
└── Models/
    ├── Components/             # Shared models
    ├── Operations/             # Request/response types
    └── Errors/                 # Error classes
docs/
├── sdks/                       # Method documentation
└── Models/                     # Model documentation
composer.json
phpunit.xml
phpstan.neon
```

## SDK Instantiation

PHP SDKs use a builder pattern for configuration:

```php
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use Dub;

// Basic instantiation with API key
$sdk = Dub\Dub::builder()
    ->setSecurity('YOUR_API_KEY')
    ->build();

// With custom server URL
$sdk = Dub\Dub::builder()
    ->setSecurity('YOUR_API_KEY')
    ->setServerUrl('https://api.example.com')
    ->build();

// With custom Guzzle client
$client = new \GuzzleHttp\Client([
    'timeout' => 30,
    'connect_timeout' => 10,
]);

$sdk = Dub\Dub::builder()
    ->setClient($client)
    ->setSecurity('YOUR_API_KEY')
    ->build();

// With security callback (for token refresh)
$sdk = Dub\Dub::builder()
    ->setSecuritySource(function() {
        return getTokenFromCache() ?? refreshToken();
    })
    ->build();
```

## Making API Calls

### Basic Request

```php
use Dub\Models\Operations;

$request = new Operations\CreateLinkRequestBody(
    url: 'https://google.com',
    externalId: '123456',
);

$response = $sdk->links->create(
    request: $request
);

if ($response->linkSchema !== null) {
    echo "Created link: " . $response->linkSchema->shortLink;
}
```

### With Optional Parameters

```php
$request = new Operations\CreateLinkRequestBody(
    url: 'https://google.com',
    externalId: '123456',
    tagIds: ['tag_123', 'tag_456'],
    trackConversion: true,
    archived: false,
);

$response = $sdk->links->create(request: $request);
```

### Individual Parameters (when maxMethodParams allows)

```php
// For methods with few parameters
$response = $sdk->links->get(
    linkId: 'clux0rgak00011...',
    externalId: '123456'
);
```

## Pagination

PHP SDKs use PHP Generators for pagination, allowing efficient iteration without loading all results into memory:

```php
use Dub\Models\Operations;

$request = new Operations\GetLinksRequest(
    pageSize: 50,
);

// Returns a Generator
$responses = $sdk->links->list(request: $request);

// Iterate through all pages automatically
foreach ($responses as $response) {
    if ($response->statusCode === 200) {
        foreach ($response->linkSchemas as $link) {
            echo $link->shortLink . "\n";
        }
    }
}
```

## Error Handling

PHP SDKs generate a typed exception hierarchy:

```php
use Dub\Models\Errors;

try {
    $response = $sdk->links->create(request: $request);
} catch (Errors\BadRequestThrowable $e) {
    // 400 Bad Request
    echo "Bad request: " . $e->getMessage();
} catch (Errors\UnauthorizedThrowable $e) {
    // 401 Unauthorized
    echo "Authentication failed";
} catch (Errors\ForbiddenThrowable $e) {
    // 403 Forbidden
    echo "Access denied";
} catch (Errors\NotFoundThrowable $e) {
    // 404 Not Found
    echo "Resource not found";
} catch (Errors\RateLimitExceededThrowable $e) {
    // 429 Rate Limited
    echo "Rate limited, retry later";
} catch (Errors\SDKException $e) {
    // Catch-all for other errors
    echo "Error: " . $e->getMessage();
}
```

### Error Class Properties

Each error class provides:

| Property | Type | Description |
|----------|------|-------------|
| `$message` | `string` | Human-readable error message |
| `$statusCode` | `int` | HTTP status code |
| `$rawResponse` | `?ResponseInterface` | Full Guzzle response |
| `$body` | `string` | Raw response body |

## Model Serialization

PHP SDKs use PHP 8 attributes for serialization via `speakeasy/serializer`:

```php
class LinkSchema
{
    #[\Speakeasy\Serializer\Annotation\SerializedName('id')]
    public string $id;

    #[\Speakeasy\Serializer\Annotation\SerializedName('shortLink')]
    public string $shortLink;

    #[\Speakeasy\Serializer\Annotation\SerializedName('webhookIds')]
    #[\Speakeasy\Serializer\Annotation\Type('array<string>')]
    public array $webhookIds;

    #[\Speakeasy\Serializer\Annotation\SerializedName('tags')]
    #[\Speakeasy\Serializer\Annotation\Type('array<\Dub\Models\Components\Tag>|null')]
    public ?array $tags;

    #[\Speakeasy\Serializer\Annotation\SerializedName('archived')]
    #[\Speakeasy\Serializer\Annotation\SkipWhenNull]
    public ?bool $archived = null;
}
```

### Serialization Attributes

| Attribute | Purpose |
|-----------|---------|
| `SerializedName('name')` | JSON property name |
| `Type('array<Type>')` | Complex type declaration |
| `SkipWhenNull` | Omit from JSON if null |

## PHP Hooks

PHP SDKs support lifecycle hooks for customization. The `HookRegistration.php` file is preserved during regeneration.

### Hook Types

| Hook Type | When Called | Use Cases |
|-----------|-------------|-----------|
| `SDKInitHook` | During SDK initialization | Configure defaults |
| `BeforeRequestHook` | Before HTTP request | Add headers, logging |
| `AfterSuccessHook` | After successful response | Transform response, warnings |
| `AfterErrorHook` | After error response | Error handling, retries |

### Hook Registration

```php
// src/Hooks/HookRegistration.php
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

class HookRegistration
{
    public static function initHooks(Hooks $hooks): void
    {
        // Register custom hooks
        $hooks->registerBeforeRequestHook(new CustomUserAgentHook());
        $hooks->registerAfterSuccessHook(new LoggingHook());
        $hooks->registerAfterErrorHook(new ErrorReportingHook());
    }
}
```

### Example: Custom User-Agent Hook

```php
// src/Hooks/CustomUserAgentHook.php
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

use Psr\Http\Message\RequestInterface;

class CustomUserAgentHook implements BeforeRequestHook
{
    public function beforeRequest(
        BeforeRequestContext $context,
        RequestInterface $request
    ): RequestInterface {
        return $request->withHeader(
            'User-Agent',
            'my-sdk-php/1.0.0 ' . $request->getHeaderLine('User-Agent')
        );
    }
}
```

### Example: Logging Hook

```php
// src/Hooks/LoggingHook.php
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

use Psr\Http\Message\ResponseInterface;
use Psr\Log\LoggerInterface;

class LoggingHook implements AfterSuccessHook
{
    public function __construct(
        private LoggerInterface $logger
    ) {}

    public function afterSuccess(
        AfterSuccessContext $context,
        ResponseInterface $response
    ): ResponseInterface {
        $this->logger->info('API call completed', [
            'status' => $response->getStatusCode(),
            'operation' => $context->operationId,
        ]);
        return $response;
    }
}
```

## Feature Support

### Authentication

| Name | Support | Notes |
|------|---------|-------|
| HTTP Basic | ✅ | |
| API Key (bearer, header, cookie, query) | ✅ | |
| OAuth implicit flow | ✅ | |
| OAuth refresh token flow | ✅ | Via security callbacks |
| OAuth client credentials flow | ✅ | Via hooks |
| mTLS | ❌ | |

### Server Configuration

| Name | Support | Notes |
|------|---------|-------|
| URL Templating | ✅ | Server variables |
| Multiple servers | ✅ | `x-speakeasy-server-id` |
| Custom server URL | ✅ | `setServerUrl()` |

### Data Types

| Name | Support | Notes |
|------|---------|-------|
| Numbers | ✅ | `float`, `int` |
| Strings | ✅ | |
| Date/DateTime | ✅ | ISO 8601 strings |
| Boolean | ✅ | |
| Binary | ✅ | |
| Enums | ✅ | String-backed enums |
| Arrays | ✅ | |
| Maps | ✅ | |
| Objects | ✅ | |
| Any | ✅ | `mixed` type |
| Null | ✅ | Nullable types |
| Union Types | ✅ | PHP 8 union types |

### Parameters

| Name | Support | Notes |
|------|---------|-------|
| Path parameters | ✅ | |
| Query parameters | ✅ | |
| Header parameters | ✅ | |
| Request body | ✅ | JSON, form data |

### Responses

| Name | Support | Notes |
|------|---------|-------|
| JSON | ✅ | |
| Plain text | ✅ | |
| Binary | ✅ | |
| Pagination | ✅ | Generator-based |
| Custom errors | ✅ | Throwable classes |

## Configuration Options

All PHP SDK configuration is managed in `gen.yaml` under the `php` section.

### Version and Package

```yaml
php:
  version: 1.0.0
  namespace: MySDK
  packageName: myorg/my-sdk
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `version` | Yes | `0.0.1` | SDK version |
| `namespace` | Yes | - | PHP namespace (e.g., `Dub`) |
| `packageName` | Yes | - | Composer package name (e.g., `dub/dub-php`) |

### Error Naming

```yaml
php:
  baseErrorName: MyAPIError
  defaultErrorName: SDKException
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `baseErrorName` | No | `SDKError` | Base error class name for branding |
| `defaultErrorName` | No | `SDKException` | Default exception for unhandled errors |

This creates a branded error hierarchy:

```
MyAPIError (base)
├── BadRequest (400)
├── Unauthorized (401)
├── Forbidden (403)
├── NotFound (404)
├── Conflict (409)
├── RateLimitExceeded (429)
└── InternalServerError (500)
```

### Method Arguments

```yaml
php:
  maxMethodParams: 4
  methodArguments: infer-optional-args
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `maxMethodParams` | No | `9999` | Max parameters before using request object |
| `methodArguments` | No | `require-security-and-request` | How method arguments are generated |

**`methodArguments` options:**

| Value | Behavior |
|-------|----------|
| `require-security-and-request` | All params required |
| `infer-optional-args` | Infer optionality from OpenAPI spec |

### Model Suffixes

```yaml
php:
  inputModelSuffix: input
  outputModelSuffix: output
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `inputModelSuffix` | No | `""` | Suffix for request models |
| `outputModelSuffix` | No | `""` | Suffix for response models |

### Security Configuration

```yaml
php:
  flattenGlobalSecurity: true
  clientServerStatusCodesAsErrors: true
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `flattenGlobalSecurity` | No | `true` | Inline security in SDK constructor |
| `clientServerStatusCodesAsErrors` | No | `true` | Treat 4XX/5XX as errors |

### Import Paths

```yaml
php:
  imports:
    option: openapi
    paths:
      callbacks: Models/Callbacks
      errors: Models/Errors
      operations: Models/Operations
      shared: Models/Components
      webhooks: Models/Webhooks
```

### Laravel Integration

```yaml
php:
  laravelServiceProvider:
    enabled: true
    svcName: myapi
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `laravelServiceProvider.enabled` | No | `false` | Generate Laravel service provider |
| `laravelServiceProvider.svcName` | No | `openapi` | Service name in Laravel container |

When enabled, generates a Laravel service provider for dependency injection:

```php
// In Laravel config/app.php
'providers' => [
    MySDK\MySDKServiceProvider::class,
],

// Then inject the SDK
public function __construct(MySDK\SDK $sdk)
{
    $this->sdk = $sdk;
}
```

### Additional Dependencies

```yaml
php:
  additionalDependencies:
    autoload: {}
    autoload-dev: {}
    require:
      psr/log: "^3.0"
    require-dev:
      phpunit/phpunit: "^10"
```

## Publishing to Packagist

Configure Packagist publishing in `workflow.yaml`:

```yaml
targets:
  php-sdk:
    target: php
    source: my-api
    publish:
      packagist:
        username: myorg
        token: $packagist_token
```

### GitHub Workflow for Publishing

```yaml
# .github/workflows/sdk_publish.yaml
name: Publish
permissions:
  checks: write
  contents: write
  pull-requests: write
  statuses: write
on:
  push:
    branches:
      - main
    paths:
      - RELEASES.md
jobs:
  publish:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/sdk-publish.yaml@v15
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      packagist_username: ${{ secrets.PACKAGIST_USERNAME }}
      packagist_token: ${{ secrets.PACKAGIST_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
```

### Packagist Setup

1. Create account at [packagist.org](https://packagist.org)
2. Generate API token in Packagist settings
3. Add secrets to GitHub repository:
   - `PACKAGIST_USERNAME`: Your Packagist username
   - `PACKAGIST_TOKEN`: Your Packagist API token

## Development Dependencies

Generated PHP SDKs include standard development tooling:

```json
{
  "require-dev": {
    "laravel/pint": ">=1.21.2",
    "phpstan/phpstan": ">=2.1.0",
    "phpunit/phpunit": ">=10",
    "roave/security-advisories": "dev-latest"
  }
}
```

### Running Quality Tools

```bash
# Install dependencies
composer install

# Run tests
composer test
# Or: ./vendor/bin/phpunit --testdox

# Run static analysis
composer stan
# Or: ./vendor/bin/phpstan analyse

# Run code formatter
./vendor/bin/pint
```

## Test Generation

Enable test generation in `gen.yaml`:

```yaml
generation:
  tests:
    generateTests: true
    generateNewTests: false
    skipResponseBodyAssertions: false
```

| Option | Default | Description |
|--------|---------|-------------|
| `generateTests` | `false` | Enable test generation |
| `generateNewTests` | `true` | Generate tests for new operations |
| `skipResponseBodyAssertions` | `false` | Skip response body assertions |

**Recommended for production:** `generateTests: true`, `generateNewTests: false`

This updates existing tests while preserving manual test additions.

## Code Samples Overlay

PHP SDKs can generate code samples for documentation:

```yaml
# workflow.yaml
targets:
  php-sdk:
    target: php
    source: my-api
    codeSamples:
      output: codeSamples.yaml
      registry:
        location: registry.speakeasyapi.dev/myorg/myapi/code-samples-php
```

The `codeSamples.yaml` overlay adds `x-codeSamples` to your OpenAPI spec with PHP examples.

## Complete gen.yaml Example

```yaml
configVersion: 2.0.0
generation:
  sdkClassName: MyAPI
  maintainOpenAPIOrder: true
  usageSnippets:
    optionalPropertyRendering: withExample
    sdkInitStyle: constructor
  auth:
    oAuth2ClientCredentialsEnabled: true
    hoistGlobalSecurity: true
  tests:
    generateTests: true
    generateNewTests: false
php:
  version: 1.0.0
  namespace: MyOrg\MyAPI
  packageName: myorg/my-api-sdk
  baseErrorName: MyAPIError
  defaultErrorName: SDKException
  maxMethodParams: 4
  methodArguments: infer-optional-args
  flattenGlobalSecurity: true
  clientServerStatusCodesAsErrors: true
  inputModelSuffix: input
  outputModelSuffix: output
  imports:
    option: openapi
    paths:
      errors: Models/Errors
      operations: Models/Operations
      shared: Models/Components
  laravelServiceProvider:
    enabled: false
```

---

## Pre-defined TODO List

When configuring a PHP SDK generation, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Review PHP SDK feature requirements | Reviewing PHP SDK feature requirements |
| 2 | Configure gen.yaml for PHP target | Configuring gen.yaml for PHP target |
| 3 | Set namespace and packageName | Setting namespace and packageName |
| 4 | Configure error class naming | Configuring error class naming |
| 5 | Set maxMethodParams and methodArguments | Setting maxMethodParams and methodArguments |
| 6 | Configure authentication settings | Configuring authentication settings |
| 7 | Set up Packagist publishing (if needed) | Setting up Packagist publishing |
| 8 | Run speakeasy generate | Running speakeasy generate |
| 9 | Verify SDK compiles with composer install | Verifying SDK compilation |
| 10 | Run phpstan for static analysis | Running phpstan analysis |

**Usage:**
```
TodoWrite([
  {content: "Review PHP SDK feature requirements", status: "pending", activeForm: "Reviewing PHP SDK feature requirements"},
  {content: "Configure gen.yaml for PHP target", status: "pending", activeForm: "Configuring gen.yaml for PHP target"},
  {content: "Set namespace and packageName", status: "pending", activeForm: "Setting namespace and packageName"},
  {content: "Configure error class naming", status: "pending", activeForm: "Configuring error class naming"},
  {content: "Set maxMethodParams and methodArguments", status: "pending", activeForm: "Setting maxMethodParams and methodArguments"},
  {content: "Configure authentication settings", status: "pending", activeForm: "Configuring authentication settings"},
  {content: "Set up Packagist publishing (if needed)", status: "pending", activeForm: "Setting up Packagist publishing"},
  {content: "Run speakeasy generate", status: "pending", activeForm: "Running speakeasy generate"},
  {content: "Verify SDK compiles with composer install", status: "pending", activeForm: "Verifying SDK compilation"},
  {content: "Run phpstan for static analysis", status: "pending", activeForm: "Running phpstan analysis"}
])
```

**Nested workflows:**
- See `plans/sdk-generation.md` for the full SDK generation workflow
- See `sdk-customization/hooks.md` for hook implementation patterns
- See `spec-first/validation.md` for OpenAPI validation before generation
