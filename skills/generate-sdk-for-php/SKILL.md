---
name: generate-sdk-for-php
description: >-
  Use when generating a PHP SDK with Speakeasy. Covers gen.yaml configuration,
  Guzzle HTTP client, builder pattern, Packagist publishing.
  Triggers on "PHP SDK", "generate PHP", "Packagist publish", "Composer package",
  "PHP client library", "Laravel SDK".
license: Apache-2.0
---

# Generate SDK for PHP

Configure and generate idiomatic PHP SDKs with Speakeasy, featuring PHP 8.2+, Guzzle HTTP client, builder patterns, and Packagist publishing.

## When to Use

- Generating a new PHP SDK from an OpenAPI spec
- Configuring PHP-specific gen.yaml options
- Setting up SDK hooks
- Publishing to Packagist
- User says: "PHP SDK", "Packagist", "Composer", "PHP client"

## Quick Start

```bash
speakeasy quickstart --skip-interactive --output console \
  -s openapi.yaml -t php -n "MySDK" -p "myorg/my-sdk"
```

## Essential gen.yaml Configuration

```yaml
php:
  version: 1.0.0
  packageName: myorg/my-sdk
  namespace: MyOrg\MySDK

  # Method signatures
  maxMethodParams: 4

  # Error handling
  responseFormat: flat
  clientServerStatusCodesAsErrors: true
```

## Package Structure

```
src/
├── MySDK.php              # Main SDK class
├── MySDKBuilder.php       # Builder pattern
├── SDKConfiguration.php
├── Hooks/
│   ├── SDKHooks.php       # Hook orchestrator
│   └── HookRegistration.php  # Custom hooks (preserved)
├── Models/
│   ├── Components/        # Shared models
│   ├── Operations/        # Request/response types
│   └── Errors/            # Error classes
└── Utils/
    └── Retry/             # Retry configuration
composer.json
phpunit.xml
phpstan.neon
```

## Client Usage

```php
<?php
declare(strict_types=1);

require 'vendor/autoload.php';

use MyOrg\MySDK;

// Create client with builder
$sdk = MySDK\MySDK::builder()
    ->setSecurity('your-api-key')
    ->build();

// Make API call
$response = $sdk->resources->create(
    new MySDK\Models\Operations\CreateRequest(
        name: 'my-resource'
    )
);

if ($response->resource !== null) {
    echo $response->resource->id;
}
```

## Custom Guzzle Client

```php
$client = new \GuzzleHttp\Client([
    'timeout' => 30,
    'connect_timeout' => 10,
]);

$sdk = MySDK\MySDK::builder()
    ->setClient($client)
    ->setSecurity('your-api-key')
    ->build();
```

## Security Callback (Token Refresh)

```php
$sdk = MySDK\MySDK::builder()
    ->setSecuritySource(function() {
        return getTokenFromCache() ?? refreshToken();
    })
    ->build();
```

## SDK Hooks

Register hooks in `Hooks/HookRegistration.php`:

```php
<?php
namespace MyOrg\MySDK\Hooks;

class HookRegistration
{
    public static function registerHooks(SDKHooks $hooks): void
    {
        $hooks->registerBeforeRequestHook(new CustomHeaderHook());
    }
}

class CustomHeaderHook implements BeforeRequestHook
{
    public function beforeRequest(
        BeforeRequestContext $context,
        \Psr\Http\Message\RequestInterface $request
    ): \Psr\Http\Message\RequestInterface {
        return $request->withHeader('X-Custom', 'value');
    }
}
```

## Packagist Publishing

1. Configure `composer.json`:
```json
{
  "name": "myorg/my-sdk",
  "description": "PHP SDK for My API",
  "type": "library",
  "require": {
    "php": ">=8.2"
  }
}
```

2. Register on Packagist.org with GitHub repo
3. Tag releases: `git tag v1.0.0 && git push --tags`

## Common Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `namespace` | OpenAPI | PHP namespace |
| `packageName` | openapi/sdk | Composer package |
| `maxMethodParams` | 0 | Max params before request object |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| PHP version error | Requires PHP 8.2+ |
| Guzzle timeout | Increase timeout in client config |
| PHPStan errors | Run `vendor/bin/phpstan analyse` |

## Related Skills

- `start-new-sdk-project` - Initial SDK setup
- `customize-sdk-hooks` - Hook implementation
- `setup-sdk-testing` - Testing patterns
