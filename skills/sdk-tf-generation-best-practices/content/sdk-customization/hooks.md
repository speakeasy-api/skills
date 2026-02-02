---
short_description: Implement cross-cutting concerns with SDK hooks
long_description: |
  Guide for implementing SDK hooks to add custom behavior like user-agent
  headers, deprecation warnings, telemetry, and request/response transformation.
  Includes registration patterns and common hook implementations.
source:
  - repo: "mistralai/client-ts"
    path: "src/hooks/"
    ref: "main"
    last_reconciled: "2025-12-11"
  - repo: "speakeasy-sdks/visa-payments-typescript-sdk"
    path: "src/hooks/"
    ref: "main"
    last_reconciled: "2025-12-11"
    notes: "Custom HTTP signature authentication via BeforeRequestHook"
related:
  - "../sdk-languages/typescript.md"
  - "../sdk-languages/php.md"
  - "../sdk-languages/ruby.md"
  - "./multi-target-sdks.md"
---

# SDK Hooks

Hooks allow you to intercept and modify SDK behavior without changing generated code. Use hooks for cross-cutting concerns like authentication, logging, telemetry, and error handling.

## Hook Types

| Hook Type | When Called | Common Use Cases |
|-----------|-------------|------------------|
| `SDKInitHook` | During SDK initialization | Configure defaults, validate config |
| `BeforeCreateRequestHook` | Before request object creation | Modify request input data |
| `BeforeRequestHook` | Before request is sent | Add headers, logging, telemetry |
| `AfterSuccessHook` | After successful response | Transform response, emit warnings |
| `AfterErrorHook` | After error response | Error transformation, retry logic |

## Hook Architecture

### TypeScript Hook Types

```typescript
// src/hooks/types.ts (generated)
export type Awaitable<T> = T | Promise<T>;

export interface SDKInitHook {
  sdkInit(opts: SDKInitOptions): SDKInitOptions;
}

export interface BeforeCreateRequestHook {
  beforeCreateRequest(
    hookCtx: BeforeCreateRequestContext,
    input: RequestInput
  ): RequestInput;
}

export interface BeforeRequestHook {
  beforeRequest(
    hookCtx: BeforeRequestContext,
    request: Request
  ): Awaitable<Request>;
}

export interface AfterSuccessHook {
  afterSuccess(
    hookCtx: AfterSuccessContext,
    response: Response
  ): Awaitable<Response>;
}

export interface AfterErrorHook {
  afterError(
    hookCtx: AfterErrorContext,
    response: Response | null,
    error: unknown
  ): Awaitable<{ response: Response | null; error: unknown }>;
}

export type Hook =
  | SDKInitHook
  | BeforeCreateRequestHook
  | BeforeRequestHook
  | AfterSuccessHook
  | AfterErrorHook;
```

## Registration Pattern

### Hook Registration File

The `registration.ts` file is the entry point for all custom hooks. This file is preserved during regeneration:

```typescript
// src/hooks/registration.ts
import { Hooks } from "./types";
import { CustomUserAgentHook } from "./custom_user_agent";
import { DeprecationWarningHook } from "./deprecation_warning";
import { TelemetryHook } from "./telemetry";

/*
 * This file is generated once and then treated as user-owned (safe to modify).
 * Register hooks by calling hooks.register*Hook methods.
 * Hooks are registered per SDK instance and valid for the SDK's lifetime.
 */

export function initHooks(hooks: Hooks) {
    // Add user-agent header to all requests
    const customUserAgentHook = new CustomUserAgentHook();
    hooks.registerBeforeRequestHook(customUserAgentHook);

    // Warn on deprecated API responses
    const deprecationWarningHook = new DeprecationWarningHook();
    hooks.registerAfterSuccessHook(deprecationWarningHook);

    // Optional: Add telemetry
    // const telemetryHook = new TelemetryHook();
    // hooks.registerBeforeRequestHook(telemetryHook);
    // hooks.registerAfterSuccessHook(telemetryHook);
}
```

## Common Hook Patterns

### Custom User-Agent Header

Set a consistent user-agent string for API analytics and debugging:

```typescript
// src/hooks/custom_user_agent.ts
import { SDK_METADATA } from "../lib/config";
import { BeforeRequestContext, BeforeRequestHook, Awaitable } from "./types";

export class CustomUserAgentHook implements BeforeRequestHook {
  beforeRequest(
    _: BeforeRequestContext,
    request: Request
  ): Awaitable<Request> {
    const version = SDK_METADATA.sdkVersion;
    const ua = `mysdk-typescript/${version}`;

    // Set the user-agent header
    request.headers.set("user-agent", ua);

    // Chrome restricts setting user-agent in some contexts
    // Use a fallback header if the primary fails
    if (!request.headers.get("user-agent")) {
      request.headers.set("x-sdk-user-agent", ua);
    }

    return request;
  }
}
```

### Deprecation Warning Hook

Read custom headers from API responses to surface deprecation warnings:

```typescript
// src/hooks/deprecation_warning.ts
import { AfterSuccessContext, AfterSuccessHook, Awaitable } from './types';

const HEADER_MODEL_DEPRECATION_TIMESTAMP = "x-model-deprecation-timestamp";

export class DeprecationWarningHook implements AfterSuccessHook {
    afterSuccess(
        _: AfterSuccessContext,
        response: Response
    ): Awaitable<Response> {
        if (response.headers.has(HEADER_MODEL_DEPRECATION_TIMESTAMP)) {
            // Clone response to read body without consuming it
            response.clone().json().then((body) => {
                const deprecationDate = response.headers.get(
                    HEADER_MODEL_DEPRECATION_TIMESTAMP
                );
                console.warn(
                    `WARNING: The resource "${body.model || body.id}" is deprecated ` +
                    `and will be removed on ${deprecationDate}. ` +
                    `Please refer to the migration guide for alternatives.`
                );
            }).catch(() => {
                // Silently fail if body isn't JSON
            });
        }
        return response;
    }
}
```

### Request Telemetry Hook

Track request metrics for observability:

```typescript
// src/hooks/telemetry.ts
import {
  BeforeRequestContext,
  BeforeRequestHook,
  AfterSuccessContext,
  AfterSuccessHook,
  AfterErrorContext,
  AfterErrorHook,
  Awaitable,
} from "./types";

interface RequestMetrics {
  startTime: number;
  operationId: string;
  method: string;
  url: string;
}

// Store metrics per request (use WeakMap to avoid memory leaks)
const requestMetrics = new WeakMap<Request, RequestMetrics>();

export class TelemetryHook
  implements BeforeRequestHook, AfterSuccessHook, AfterErrorHook
{
  beforeRequest(
    hookCtx: BeforeRequestContext,
    request: Request
  ): Awaitable<Request> {
    requestMetrics.set(request, {
      startTime: Date.now(),
      operationId: hookCtx.operationID,
      method: request.method,
      url: request.url,
    });

    // Add correlation ID header
    const correlationId = crypto.randomUUID();
    request.headers.set("x-correlation-id", correlationId);

    return request;
  }

  afterSuccess(
    _: AfterSuccessContext,
    response: Response
  ): Awaitable<Response> {
    // Note: We can't access the original request here directly
    // Consider passing metrics through context if needed
    return response;
  }

  afterError(
    _: AfterErrorContext,
    response: Response | null,
    error: unknown
  ): Awaitable<{ response: Response | null; error: unknown }> {
    // Log error for telemetry
    console.error("SDK request failed:", error);
    return { response, error };
  }
}
```

### Rate Limit Handler Hook

Handle rate limiting gracefully:

```typescript
// src/hooks/rate_limit.ts
import { AfterSuccessContext, AfterSuccessHook, Awaitable } from "./types";

export class RateLimitHook implements AfterSuccessHook {
  afterSuccess(
    _: AfterSuccessContext,
    response: Response
  ): Awaitable<Response> {
    // Check for rate limit headers
    const remaining = response.headers.get("x-ratelimit-remaining");
    const resetTime = response.headers.get("x-ratelimit-reset");

    if (remaining !== null && parseInt(remaining) < 10) {
      console.warn(
        `Rate limit warning: Only ${remaining} requests remaining. ` +
        `Resets at ${resetTime ? new Date(parseInt(resetTime) * 1000).toISOString() : 'unknown'}`
      );
    }

    return response;
  }
}
```

### Custom Security Hook (HTTP Signature Authentication)

For APIs requiring complex authentication schemes (HMAC signatures, multi-part credentials), use a `BeforeRequestHook` combined with a custom security scheme in your OpenAPI spec.

**Step 1: Define custom security scheme via overlay**

```yaml
# .speakeasy/overlays/custom-security-overlay.yaml
overlay: 1.0.0
info:
  title: Custom Security Scheme
  version: 0.0.0
actions:
  - target: $["components"]
    update:
      "securitySchemes":
        "myCustomScheme":
          "type": "http"
          "scheme": "custom"
          "x-speakeasy-custom-security-scheme":
            "schema":
              "type": "object"
              "properties":
                "keyId":
                  "type": "string"
                  "description": "API Key ID"
                "keySecret":
                  "type": "string"
                  "description": "API Secret for HMAC signing"
                "merchantId":
                  "type": "string"
                  "description": "Merchant/Organization ID"
              "required": []
  - target: $
    update:
      "security": [{"myCustomScheme": []}]
```

**Step 2: Configure environment variable mapping in gen.yaml**

```yaml
# gen.yaml
typescript:
  envVarPrefix: MYAPI
  flattenGlobalSecurity: true
```

This generates support for `MYAPI_KEY_ID`, `MYAPI_KEY_SECRET`, and `MYAPI_MERCHANT_ID` environment variables.

**Step 3: Implement the signature hook**

```typescript
// src/hooks/customSecurity.ts
import { BeforeRequestHook, BeforeRequestContext } from "./types.js";
import { extractSecurity } from "../lib/security.js";
import * as models from "../models/index.js";

type SignatureConfig = {
  keyId: string;
  secretKey: string;
  headersToSign: string[];
  headerValues: Record<string, string>;
};

async function computeHttpSignature(config: SignatureConfig): Promise<string> {
  // Build the signing base from ordered headers
  const signingBase = config.headersToSign
    .map(name => `${name.toLowerCase()}: ${config.headerValues[name]}`)
    .join("\n");

  // Decode base64 secret key
  const keyBytes = Uint8Array.from(atob(config.secretKey), c => c.charCodeAt(0));

  // Use Web Crypto API for HMAC-SHA256
  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    keyBytes,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const sigBuffer = await crypto.subtle.sign(
    "HMAC",
    cryptoKey,
    new TextEncoder().encode(signingBase)
  );

  // Base64 encode the signature
  const signature = btoa(String.fromCharCode(...new Uint8Array(sigBuffer)));

  // Return formatted signature header
  return `keyid="${config.keyId}", algorithm="HmacSHA256", ` +
    `headers="${config.headersToSign.join(" ")}", signature="${signature}"`;
}

export const customSecurityHook: BeforeRequestHook = {
  beforeRequest: async (hookCtx: BeforeRequestContext, request: Request) => {
    // Extract security credentials from context
    const security = await extractSecurity<models.Security>(
      hookCtx.securitySource
    );

    const merchantId = security?.merchantId ?? "";
    const keyId = security?.keyId ?? "";
    const secretKey = security?.keySecret ?? "";

    // Skip if credentials are missing
    if (!merchantId || !keyId || !secretKey) return request;

    // Clone request to safely mutate headers
    request = request.clone();
    const url = new URL(request.url);
    const utcDate = new Date().toUTCString();

    // Build signature configuration
    const config: SignatureConfig = {
      keyId,
      secretKey,
      headersToSign: ["host", "date", "request-target", "x-merchant-id"],
      headerValues: {
        host: url.hostname,
        date: utcDate,
        "request-target": `${request.method.toLowerCase()} ${url.pathname}`,
        "x-merchant-id": merchantId,
      },
    };

    // Add request body digest for POST/PUT/PATCH
    if (request.method !== "GET" && request.method !== "DELETE" && request.body) {
      const bodyClone = request.clone();
      const bodyText = await bodyClone.text();
      const hashBuffer = await crypto.subtle.digest(
        "SHA-256",
        new TextEncoder().encode(bodyText)
      );
      const digest = btoa(String.fromCharCode(...Array.from(new Uint8Array(hashBuffer))));

      config.headerValues["digest"] = `SHA-256=${digest}`;
      config.headersToSign = ["host", "date", "request-target", "digest", "x-merchant-id"];
    }

    // Compute and set signature
    const signature = await computeHttpSignature(config);
    request.headers.set("Signature", signature);

    // Set additional required headers
    for (const h of ["date", "x-merchant-id", "host", "digest"]) {
      if (config.headerValues[h]) {
        request.headers.set(h, config.headerValues[h]);
      }
    }

    return request;
  },
};
```

**Step 4: Register the hook**

```typescript
// src/hooks/registration.ts
import { Hooks } from "./types.js";
import { customSecurityHook } from "./customSecurity.js";

export function initHooks(hooks: Hooks) {
  hooks.registerBeforeRequestHook(customSecurityHook);
}
```

**Step 5: Usage**

```typescript
import { SDK } from "my-sdk";

// Via environment variables (MYAPI_KEY_ID, MYAPI_KEY_SECRET, MYAPI_MERCHANT_ID)
const sdk = new SDK();

// Or via constructor
const sdk = new SDK({
  security: {
    keyId: "your-key-id",
    keySecret: "base64-encoded-secret",
    merchantId: "your-merchant-id",
  },
});

// All requests will now include HTTP signature headers
const result = await sdk.payments.create({ amount: 100 });
```

> **Note:** This pattern uses the Web Crypto API (`crypto.subtle`) which is available in Node.js 18+, Deno, Bun, and modern browsers. For older Node.js versions, add `crypto-js` as a dependency.

### Custom Error Transformation Hook

Transform errors into application-specific types:

```typescript
// src/hooks/error_transform.ts
import { AfterErrorContext, AfterErrorHook, Awaitable } from "./types";

export class CustomError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number,
    public readonly errorCode: string,
    public readonly requestId?: string
  ) {
    super(message);
    this.name = "CustomError";
  }
}

export class ErrorTransformHook implements AfterErrorHook {
  afterError(
    hookCtx: AfterErrorContext,
    response: Response | null,
    error: unknown
  ): Awaitable<{ response: Response | null; error: unknown }> {
    if (response && !response.ok) {
      const requestId = response.headers.get("x-request-id") || undefined;

      // Transform to custom error type
      const customError = new CustomError(
        `API request failed: ${response.statusText}`,
        response.status,
        `${hookCtx.operationID}_ERROR`,
        requestId
      );

      return { response, error: customError };
    }

    return { response, error };
  }
}
```

## Directory Structure

```
src/
├── hooks/
│   ├── index.ts              # Exports (generated)
│   ├── types.ts              # Hook interfaces (generated)
│   ├── hooks.ts              # Hook manager class (generated)
│   ├── registration.ts       # CUSTOM: Your hook registrations
│   ├── custom_user_agent.ts  # CUSTOM: User-agent hook
│   ├── deprecation_warning.ts # CUSTOM: Deprecation hook
│   ├── telemetry.ts          # CUSTOM: Telemetry hook
│   └── rate_limit.ts         # CUSTOM: Rate limit hook
└── ...
```

## Testing Hooks

### Unit Test Example

```typescript
// tests/hooks/deprecation_warning.test.ts
import { DeprecationWarningHook } from "../../src/hooks/deprecation_warning";

describe("DeprecationWarningHook", () => {
  let hook: DeprecationWarningHook;
  let consoleSpy: jest.SpyInstance;

  beforeEach(() => {
    hook = new DeprecationWarningHook();
    consoleSpy = jest.spyOn(console, "warn").mockImplementation();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  it("should warn when deprecation header is present", async () => {
    const response = new Response(JSON.stringify({ model: "old-model" }), {
      headers: {
        "x-model-deprecation-timestamp": "2025-06-01",
      },
    });

    await hook.afterSuccess({} as any, response);

    // Wait for async JSON parsing
    await new Promise((resolve) => setTimeout(resolve, 10));

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining("WARNING")
    );
  });

  it("should not warn when no deprecation header", async () => {
    const response = new Response(JSON.stringify({ model: "new-model" }));

    await hook.afterSuccess({} as any, response);

    expect(consoleSpy).not.toHaveBeenCalled();
  });
});
```

## Best Practices

1. **Keep hooks focused**: Each hook should do one thing well
2. **Don't block on async operations**: Use fire-and-forget for telemetry, logging
3. **Handle errors gracefully**: Hooks should never break SDK functionality
4. **Clone responses before reading**: Use `response.clone()` to avoid consuming the body
5. **Use WeakMap for request-scoped data**: Prevents memory leaks
6. **Test hooks independently**: Mock the hook context and responses
7. **Document custom headers**: Note any headers your hooks read or write

## Common Pitfalls

### Consuming Response Body

```typescript
// WRONG: Consumes the body, breaks downstream code
afterSuccess(_, response) {
  const data = await response.json(); // Body is now consumed!
  return response;
}

// CORRECT: Clone before reading
afterSuccess(_, response) {
  response.clone().json().then((data) => {
    // Process data
  });
  return response;
}
```

### Blocking Operations

```typescript
// WRONG: Blocks the request with slow operation
beforeRequest(_, request) {
  await this.telemetryService.trackSync(request); // Slow!
  return request;
}

// CORRECT: Fire-and-forget for non-critical operations
beforeRequest(_, request) {
  this.telemetryService.trackAsync(request).catch(() => {});
  return request;
}
```

---

## Ruby Hooks

Ruby SDKs use Sorbet-typed hooks with Faraday request/response objects.

### Ruby Hook Types

```ruby
# lib/open_api_sdk/sdk_hooks/types.rb (generated)
module OpenApiSDK
  module SDKHooks
    module AbstractBeforeRequestHook
      sig do
        params(
          hook_ctx: BeforeRequestHookContext,
          request: Faraday::Request
        ).returns(Faraday::Request)
      end
      def before_request(hook_ctx:, request:)
        raise NotImplementedError
      end
    end

    module AbstractAfterSuccessHook
      sig do
        params(
          hook_ctx: AfterSuccessHookContext,
          response: Faraday::Response
        ).returns(Faraday::Response)
      end
      def after_success(hook_ctx:, response:)
        raise NotImplementedError
      end
    end
  end
end
```

### Ruby Directory Structure

```
lib/open_api_sdk/
└── sdk_hooks/
    ├── hooks.rb              # Hook manager (generated)
    ├── types.rb              # Hook interfaces (generated)
    ├── registration.rb       # CUSTOM: Your registrations
    ├── custom_user_agent.rb  # CUSTOM: User-agent hook
    └── logging_hook.rb       # CUSTOM: Logging hook
```

### Ruby Hook Implementation

```ruby
# lib/open_api_sdk/sdk_hooks/custom_user_agent_hook.rb
# typed: true
# frozen_string_literal: true

require_relative './types'

module OpenApiSDK
  module SDKHooks
    class CustomUserAgentHook < AbstractSDKHook
      extend T::Sig

      sig do
        override.params(
          hook_ctx: BeforeRequestHookContext,
          request: Faraday::Request
        ).returns(Faraday::Request)
      end
      def before_request(hook_ctx:, request:)
        request.headers['User-Agent'] = "my-sdk-ruby/1.0.0"
        request
      end
    end
  end
end
```

### Ruby Hook Registration

```ruby
# lib/open_api_sdk/sdk_hooks/registration.rb
# typed: true
# frozen_string_literal: true

require_relative './types'
require_relative './custom_user_agent_hook'

module OpenApiSDK
  module SDKHooks
    class Registration
      extend T::Sig

      sig { params(hooks: Hooks).void }
      def self.init_hooks(hooks)
        hooks.register_before_request_hook(CustomUserAgentHook.new)
      end
    end
  end
end
```

### Ruby Logging Hook Example

```ruby
# lib/open_api_sdk/sdk_hooks/logging_hook.rb
# typed: true
# frozen_string_literal: true

require 'logger'

module OpenApiSDK
  module SDKHooks
    class LoggingHook < AbstractSDKHook
      extend T::Sig

      sig { void }
      def initialize
        @logger = Logger.new($stdout)
      end

      sig do
        override.params(
          hook_ctx: BeforeRequestHookContext,
          request: Faraday::Request
        ).returns(Faraday::Request)
      end
      def before_request(hook_ctx:, request:)
        @logger.info("#{request.method.upcase} #{request.path}")
        request
      end

      sig do
        override.params(
          hook_ctx: AfterSuccessHookContext,
          response: Faraday::Response
        ).returns(Faraday::Response)
      end
      def after_success(hook_ctx:, response:)
        @logger.info("Response: #{response.status}")
        response
      end

      sig do
        override.params(
          error: T.nilable(StandardError),
          hook_ctx: AfterErrorHookContext,
          response: T.nilable(Faraday::Response)
        ).returns(T.nilable(Faraday::Response))
      end
      def after_error(error:, hook_ctx:, response:)
        @logger.error("Error: #{error&.message}")
        response
      end
    end
  end
end
```

> **See also:** `sdk-languages/ruby.md` for complete Ruby SDK documentation

---

## PHP Hooks

PHP SDKs use Guzzle PSR-7 request/response objects with a class-based hook system.

### PHP Hook Types

```php
// src/Hooks/Types.php (generated)
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;

interface BeforeRequestHook
{
    public function beforeRequest(
        BeforeRequestContext $context,
        RequestInterface $request
    ): RequestInterface;
}

interface AfterSuccessHook
{
    public function afterSuccess(
        AfterSuccessContext $context,
        ResponseInterface $response
    ): ResponseInterface;
}

interface AfterErrorHook
{
    public function afterError(
        AfterErrorContext $context,
        ?ResponseInterface $response,
        ?\Throwable $error
    ): AfterErrorResult;
}
```

### PHP Directory Structure

```
src/
└── Hooks/
    ├── SDKHooks.php          # Hook manager (generated)
    ├── Types.php             # Hook interfaces (generated)
    ├── HookRegistration.php  # CUSTOM: Your registrations
    ├── CustomUserAgentHook.php  # CUSTOM: User-agent hook
    └── LoggingHook.php       # CUSTOM: Logging hook
```

### PHP Hook Registration

```php
// src/Hooks/HookRegistration.php
<?php

/**
 * Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT.
 */

declare(strict_types=1);

namespace MySDK\Hooks;

class HookRegistration
{
    public static function initHooks(Hooks $hooks): void
    {
        // Register custom hooks
        $hooks->registerBeforeRequestHook(new CustomUserAgentHook());
        $hooks->registerAfterSuccessHook(new DeprecationWarningHook());
        $hooks->registerAfterErrorHook(new ErrorLoggingHook());
    }
}
```

### PHP Custom User-Agent Hook

```php
// src/Hooks/CustomUserAgentHook.php
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

use Psr\Http\Message\RequestInterface;

class CustomUserAgentHook implements BeforeRequestHook
{
    private const SDK_VERSION = '1.0.0';

    public function beforeRequest(
        BeforeRequestContext $context,
        RequestInterface $request
    ): RequestInterface {
        $currentUA = $request->getHeaderLine('User-Agent');
        $customUA = 'my-sdk-php/' . self::SDK_VERSION;

        // Prepend custom user-agent
        return $request->withHeader(
            'User-Agent',
            $customUA . ' ' . $currentUA
        );
    }
}
```

### PHP Deprecation Warning Hook

```php
// src/Hooks/DeprecationWarningHook.php
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

use Psr\Http\Message\ResponseInterface;

class DeprecationWarningHook implements AfterSuccessHook
{
    private const DEPRECATION_HEADER = 'x-model-deprecation-timestamp';

    public function afterSuccess(
        AfterSuccessContext $context,
        ResponseInterface $response
    ): ResponseInterface {
        if ($response->hasHeader(self::DEPRECATION_HEADER)) {
            $deprecationDate = $response->getHeaderLine(self::DEPRECATION_HEADER);

            // Decode response to get model name
            $body = json_decode((string) $response->getBody(), true);
            $model = $body['model'] ?? $body['id'] ?? 'unknown';

            trigger_error(
                sprintf(
                    'WARNING: The resource "%s" is deprecated and will be removed on %s.',
                    $model,
                    $deprecationDate
                ),
                E_USER_WARNING
            );

            // Rewind the body stream for downstream consumers
            $response->getBody()->rewind();
        }

        return $response;
    }
}
```

### PHP Telemetry Hook

```php
// src/Hooks/TelemetryHook.php
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;
use Psr\Log\LoggerInterface;

class TelemetryHook implements BeforeRequestHook, AfterSuccessHook, AfterErrorHook
{
    private array $requestStartTimes = [];

    public function __construct(
        private LoggerInterface $logger
    ) {}

    public function beforeRequest(
        BeforeRequestContext $context,
        RequestInterface $request
    ): RequestInterface {
        // Add correlation ID
        $correlationId = bin2hex(random_bytes(8));
        $request = $request->withHeader('X-Correlation-ID', $correlationId);

        // Track start time
        $this->requestStartTimes[$correlationId] = microtime(true);

        $this->logger->info('API request started', [
            'operation' => $context->operationId,
            'method' => $request->getMethod(),
            'uri' => (string) $request->getUri(),
            'correlation_id' => $correlationId,
        ]);

        return $request;
    }

    public function afterSuccess(
        AfterSuccessContext $context,
        ResponseInterface $response
    ): ResponseInterface {
        $correlationId = $response->getHeaderLine('X-Correlation-ID');
        $duration = $this->calculateDuration($correlationId);

        $this->logger->info('API request completed', [
            'operation' => $context->operationId,
            'status' => $response->getStatusCode(),
            'duration_ms' => $duration,
            'correlation_id' => $correlationId,
        ]);

        return $response;
    }

    public function afterError(
        AfterErrorContext $context,
        ?ResponseInterface $response,
        ?\Throwable $error
    ): AfterErrorResult {
        $this->logger->error('API request failed', [
            'operation' => $context->operationId,
            'status' => $response?->getStatusCode(),
            'error' => $error?->getMessage(),
        ]);

        return new AfterErrorResult($response, $error);
    }

    private function calculateDuration(string $correlationId): ?float
    {
        if (!isset($this->requestStartTimes[$correlationId])) {
            return null;
        }

        $duration = (microtime(true) - $this->requestStartTimes[$correlationId]) * 1000;
        unset($this->requestStartTimes[$correlationId]);

        return round($duration, 2);
    }
}
```

### PHP Rate Limit Hook

```php
// src/Hooks/RateLimitHook.php
<?php

declare(strict_types=1);

namespace MySDK\Hooks;

use Psr\Http\Message\ResponseInterface;

class RateLimitHook implements AfterSuccessHook
{
    private const HEADER_REMAINING = 'x-ratelimit-remaining';
    private const HEADER_RESET = 'x-ratelimit-reset';
    private const WARNING_THRESHOLD = 10;

    public function afterSuccess(
        AfterSuccessContext $context,
        ResponseInterface $response
    ): ResponseInterface {
        if ($response->hasHeader(self::HEADER_REMAINING)) {
            $remaining = (int) $response->getHeaderLine(self::HEADER_REMAINING);

            if ($remaining < self::WARNING_THRESHOLD) {
                $resetTime = $response->hasHeader(self::HEADER_RESET)
                    ? date('Y-m-d H:i:s', (int) $response->getHeaderLine(self::HEADER_RESET))
                    : 'unknown';

                trigger_error(
                    sprintf(
                        'Rate limit warning: Only %d requests remaining. Resets at %s',
                        $remaining,
                        $resetTime
                    ),
                    E_USER_NOTICE
                );
            }
        }

        return $response;
    }
}
```

> **See also:** `sdk-languages/php.md` for complete PHP SDK documentation

---

## Pre-defined TODO List

When implementing SDK hooks, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Identify cross-cutting concerns needed | Identifying cross-cutting concerns |
| 2 | Create registration.ts file | Creating registration.ts |
| 3 | Implement BeforeRequestHook if needed | Implementing BeforeRequestHook |
| 4 | Implement AfterSuccessHook if needed | Implementing AfterSuccessHook |
| 5 | Implement AfterErrorHook if needed | Implementing AfterErrorHook |
| 6 | Register hooks in registration.ts | Registering hooks |
| 7 | Write unit tests for hooks | Writing unit tests for hooks |
| 8 | Test hooks with real SDK calls | Testing hooks with SDK calls |
| 9 | Submit feedback if documentation was unclear or incomplete | Submitting feedback |

**Usage:**
```
TodoWrite([
  {content: "Identify cross-cutting concerns needed", status: "pending", activeForm: "Identifying cross-cutting concerns"},
  {content: "Create registration.ts file", status: "pending", activeForm: "Creating registration.ts"},
  {content: "Implement BeforeRequestHook if needed", status: "pending", activeForm: "Implementing BeforeRequestHook"},
  {content: "Implement AfterSuccessHook if needed", status: "pending", activeForm: "Implementing AfterSuccessHook"},
  {content: "Implement AfterErrorHook if needed", status: "pending", activeForm: "Implementing AfterErrorHook"},
  {content: "Register hooks in registration.ts", status: "pending", activeForm: "Registering hooks"},
  {content: "Write unit tests for hooks", status: "pending", activeForm: "Writing unit tests for hooks"},
  {content: "Test hooks with real SDK calls", status: "pending", activeForm: "Testing hooks with SDK calls"},
  {content: "Submit feedback if documentation was unclear or incomplete", status: "pending", activeForm: "Submitting feedback"}
])
```

> **Feedback:** If a hook pattern did not work for your language, an interface was missing, or you needed a hook type not documented here, run:
> ```bash
> speakeasy agent feedback -m "Description of the issue" --context-path "sdk-customization/hooks.md"
> ```
