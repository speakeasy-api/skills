# PHP SDK Configuration

Detailed gen.yaml configuration options for PHP SDKs.

## gen.yaml Configuration

```yaml
php:
  version: 1.0.0
  packageName: "myorg/my-sdk"
  namespace: "MyOrg\\MySDK"

  # Method signatures
  maxMethodParams: 4
  methodArguments: require-security-and-request
```

## Package Structure

```
my-sdk/
├── composer.json
├── src/
│   ├── SDK.php                    # Main SDK class
│   ├── Models/
│   │   ├── Operations/            # Request/response classes
│   │   ├── Shared/                # Shared models
│   │   └── Errors/                # Exception classes
│   ├── Hooks/                     # Custom hooks (preserved)
│   │   └── HookRegistration.php
│   └── Utils/                     # Internal utilities
└── docs/
```

## SDK Usage

```php
<?php

use MyOrg\MySDK\SDK;
use MyOrg\MySDK\Models\Shared\Security;

$sdk = SDK::builder()
    ->setSecurity(new Security(apiKey: 'your-api-key'))
    ->build();

$user = $sdk->users->get('123');
echo $user->name;
```

## Security Configuration

```php
// API Key
$sdk = SDK::builder()
    ->setSecurity(new Security(apiKey: 'your-api-key'))
    ->build();

// Bearer Token
$sdk = SDK::builder()
    ->setSecurity(new Security(bearerAuth: 'your-token'))
    ->build();

// OAuth2
$sdk = SDK::builder()
    ->setSecurity(new Security(oauth2: 'your-oauth-token'))
    ->build();
```

## Server Selection

```php
// Named server from spec
$sdk = SDK::builder()
    ->setServer(Server::Production)
    ->build();

// Custom URL
$sdk = SDK::builder()
    ->setServerURL('https://api.example.com')
    ->build();
```

## Error Handling

```php
use MyOrg\MySDK\Models\Errors\APIException;
use MyOrg\MySDK\Models\Errors\SDKException;

try {
    $user = $sdk->users->get('invalid-id');
} catch (APIException $e) {
    // Server returned error status
    echo "Status: " . $e->getStatusCode() . "\n";
    echo "Body: " . $e->getBody() . "\n";
} catch (SDKException $e) {
    // Network, timeout, or other SDK error
    echo "SDK error: " . $e->getMessage() . "\n";
}
```

## Retries Configuration

```php
use MyOrg\MySDK\Utils\RetryConfig;
use MyOrg\MySDK\Utils\BackoffStrategy;

$sdk = SDK::builder()
    ->setRetryConfig(new RetryConfig(
        strategy: 'backoff',
        backoff: new BackoffStrategy(
            initialInterval: 500,
            maxInterval: 60000,
            exponent: 1.5,
            maxElapsedTime: 300000
        ),
        retryConnectionErrors: true
    ))
    ->build();
```

## Timeouts

```php
// Global timeout (milliseconds)
$sdk = SDK::builder()
    ->setTimeoutMs(30000)
    ->build();

// Per-call override
$user = $sdk->users->create($request, timeoutMs: 60000);
```

## Pagination

```php
// Auto-iterate all pages
foreach ($sdk->users->list(limit: 50) as $user) {
    echo $user->name . "\n";
}

// Manual pagination
$page = $sdk->users->list(limit: 50);
while ($page !== null) {
    foreach ($page->users as $user) {
        echo $user->name . "\n";
    }
    $page = $page->next();
}
```

## Custom Hooks

Create hooks in `src/Hooks/HookRegistration.php`:

```php
<?php

namespace MyOrg\MySDK\Hooks;

use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;

class HookRegistration
{
    public static function initHooks(Hooks $hooks): void
    {
        $hooks->beforeRequest(function (RequestInterface $request): RequestInterface {
            return $request->withHeader('X-Custom-Header', 'value');
        });

        $hooks->afterResponse(function (
            ResponseInterface $response,
            RequestInterface $request
        ): ResponseInterface {
            error_log(sprintf(
                "%s %s: %d",
                $request->getMethod(),
                $request->getUri(),
                $response->getStatusCode()
            ));
            return $response;
        });

        $hooks->onError(function (\Throwable $error, RequestInterface $request): void {
            error_log("Error: " . $error->getMessage());
            throw $error;
        });
    }
}
```

## Laravel Integration

Register SDK in service provider:

```php
// app/Providers/AppServiceProvider.php
use MyOrg\MySDK\SDK;
use MyOrg\MySDK\Models\Shared\Security;

public function register(): void
{
    $this->app->singleton(SDK::class, function ($app) {
        return SDK::builder()
            ->setSecurity(new Security(
                apiKey: config('services.myapi.key')
            ))
            ->build();
    });
}

// In controller
class UserController extends Controller
{
    public function __construct(private SDK $sdk) {}

    public function show(string $id)
    {
        $user = $this->sdk->users->get($id);
        return response()->json($user);
    }
}
```

## Guzzle Configuration

For custom HTTP client configuration:

```php
use GuzzleHttp\Client;
use GuzzleHttp\HandlerStack;

$stack = HandlerStack::create();
$stack->push(/* custom middleware */);

$client = new Client([
    'handler' => $stack,
    'verify' => false, // Dev only - disable SSL verification
]);

$sdk = SDK::builder()
    ->setClient($client)
    ->build();
```

## Debugging

```php
// Enable debug logging
$sdk = SDK::builder()
    ->setDebug(true)
    ->build();

// Or with custom logger (PSR-3)
use Monolog\Logger;
use Monolog\Handler\StreamHandler;

$logger = new Logger('sdk');
$logger->pushHandler(new StreamHandler('php://stderr', Logger::DEBUG));

$sdk = SDK::builder()
    ->setLogger($logger)
    ->build();
```

## Publishing to Packagist

### Prerequisites

1. Create Packagist account
2. Link GitHub repository
3. Configure `composer.json`:

```json
{
    "name": "myorg/my-sdk",
    "description": "PHP SDK for MyAPI",
    "type": "library",
    "license": "MIT",
    "autoload": {
        "psr-4": {
            "MyOrg\\MySDK\\": "src/"
        }
    },
    "require": {
        "php": ">=8.1",
        "guzzlehttp/guzzle": "^7.0"
    }
}
```

### Publish

```bash
# Tag version
git tag v1.0.0
git push origin v1.0.0

# Packagist auto-updates via webhook
# Users install with:
composer require myorg/my-sdk
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Autoload not working | Run `composer dump-autoload` |
| SSL certificate errors | Configure Guzzle `verify` option |
| Memory exhaustion | Increase `memory_limit` or use pagination |
| Type errors | Ensure PHP 8.1+ for named arguments |
| Timeout errors | Increase `timeout` in Guzzle config |
