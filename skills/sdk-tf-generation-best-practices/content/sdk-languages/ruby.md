---
short_description: "Ruby SDK generation guide"
long_description: |
  Comprehensive guide for generating Ruby SDKs with Speakeasy.
  Includes Sorbet typing, RubyGems publishing, Faraday HTTP client,
  hooks implementation, and Ruby-specific configuration options.
source:
  repo: "dubinc/dub-ruby"
  path: ".speakeasy/gen.yaml"
  ref: "main"
  last_reconciled: "2025-12-11"
related:
  - "../plans/sdk-generation.md"
  - "../sdk-customization/hooks.md"
---

# Ruby SDK Generation

## SDK Overview

The Speakeasy Ruby SDK creates idiomatic Ruby libraries with:

- Optional Sorbet type checking for static type safety
- Faraday HTTP client for flexible HTTP handling
- RubyGems publishing support
- Ruby 3.2+ compatibility
- Comprehensive error handling with custom error types

## Ruby Package Structure

```
my-sdk/
├── .speakeasy/
│   ├── gen.yaml              # Generation configuration
│   ├── gen.lock              # Version lock
│   └── workflow.yaml         # Workflow configuration
├── lib/
│   ├── my_sdk.rb             # Main entry point
│   └── open_api_sdk/
│       ├── sdk.rb            # Main SDK class
│       ├── sdkconfiguration.rb
│       ├── sdk_hooks/        # Hooks infrastructure
│       │   ├── hooks.rb      # Hook manager (generated)
│       │   ├── types.rb      # Hook types (generated)
│       │   └── registration.rb # Hook registration (customizable)
│       ├── models/
│       │   ├── operations/   # Request/response models
│       │   ├── shared/       # Shared components
│       │   └── errors/       # Error types
│       └── utils/            # Utility modules
├── sorbet/                   # Sorbet type definitions (if enabled)
│   ├── config
│   ├── rbi/
│   └── tapioca/
├── docs/                     # Generated documentation
├── my_sdk.gemspec            # Gem specification
├── Gemfile
├── Gemfile.lock
├── README.md
└── RELEASES.md
```

## Configuration Options

All Ruby SDK configuration is managed in the `gen.yaml` file under the `ruby` section.

### Basic Configuration

```yaml
ruby:
  version: 1.0.0
  packageName: my-sdk
  module: MySdk
  author: My Company
  description: Ruby Client SDK for My API
```

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| version | true | 0.0.1 | The current version of the SDK |
| packageName | true | openapi | The name of the RubyGems package |
| module | true | OpenApiSdk | The Ruby module namespace |
| author | true | Speakeasy | The author name for the gemspec |
| description | false | - | Description for the gemspec |

### Type Checking Configuration

```yaml
ruby:
  typingStrategy: sorbet
```

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| typingStrategy | `sorbet`, `none` | none | Enable Sorbet static type checking |

### Error Handling Configuration

```yaml
ruby:
  baseErrorName: MySdkError
  defaultErrorName: APIError
  clientServerStatusCodesAsErrors: true
```

| Option | Default | Description |
|--------|---------|-------------|
| baseErrorName | SDKError | Base class name for all SDK errors |
| defaultErrorName | APIError | Default error class for unspecified errors |
| clientServerStatusCodesAsErrors | true | Treat 4XX/5XX as errors |

### Import Paths

```yaml
ruby:
  imports:
    option: openapi
    paths:
      callbacks: models/callbacks
      errors: models/errors
      operations: models/operations
      shared: models/shared
      webhooks: models/webhooks
```

### Additional Dependencies

```yaml
ruby:
  additionalDependencies:
    runtime:
      redis: ">= 4.0"
    development:
      rspec: "~> 3.0"
```

---

## Sorbet Type Checking

Ruby SDKs support Sorbet for static type checking, providing TypeScript-like type safety for Ruby.

### Enable Sorbet

```yaml
# gen.yaml
ruby:
  typingStrategy: sorbet
```

### Generated Sorbet Files

When Sorbet is enabled, the SDK generates:

| File/Directory | Purpose |
|----------------|---------|
| `# typed: true` header | All `.rb` files include Sorbet directive |
| `sorbet/config` | Sorbet configuration |
| `sorbet/rbi/` | Type definitions for gems |
| `sorbet/tapioca/` | Tapioca configuration |
| `extra.rbi` | Additional type stubs |

### Sorbet Signatures in Generated Code

```ruby
# typed: true
# frozen_string_literal: true

module OpenApiSDK
  class Links
    extend T::Sig

    sig { params(client: Faraday::Connection, config: SDKConfiguration).void }
    def initialize(client, config)
      @client = client
      @config = config
    end

    sig do
      params(
        request: Models::Operations::CreateLinkRequestBody,
        timeout_ms: T.nilable(Integer)
      ).returns(Models::Operations::CreateLinkResponse)
    end
    def create(request:, timeout_ms: nil)
      # Implementation
    end
  end
end
```

### Using Sorbet with Your SDK

```bash
# Install Sorbet
gem install sorbet sorbet-runtime tapioca

# Type check the SDK
srb tc

# Generate RBI files for dependencies
tapioca gem
tapioca dsl
```

### Sorbet Strictness Levels

The SDK uses `# typed: true` which enforces:
- Method signatures are checked
- Type errors are reported
- Nil safety is enforced

For stricter checking in your application:
```ruby
# typed: strict  # Requires signatures on all methods
# typed: strong  # No untyped code allowed
```

---

## SDK Hooks

Ruby SDKs include a hooks system for customizing request/response behavior.

### Hook Types

| Hook | Method Signature | Purpose |
|------|------------------|---------|
| SDK Init | `sdk_init(config:)` | Modify SDK configuration at initialization |
| Before Request | `before_request(hook_ctx:, request:)` | Modify Faraday request before sending |
| After Success | `after_success(hook_ctx:, response:)` | Process successful responses |
| After Error | `after_error(error:, hook_ctx:, response:)` | Handle error responses |

### Hook Context

All hooks receive a context object with:

```ruby
class HookContext
  attr_accessor :config        # SDKConfiguration
  attr_accessor :base_url      # String
  attr_accessor :oauth2_scopes # T.nilable(T::Array[String])
  attr_accessor :operation_id  # String
  attr_accessor :security_source
end
```

### Implementing a Hook

Create a new hook class that extends `AbstractSDKHook`:

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
        request.headers['User-Agent'] = "my-sdk-ruby/#{VERSION}"
        request
      end
    end
  end
end
```

### Registering Hooks

Edit the `registration.rb` file (preserved during regeneration):

```ruby
# lib/open_api_sdk/sdk_hooks/registration.rb
# typed: true
# frozen_string_literal: true

require_relative './types'
require_relative './custom_user_agent_hook'
require_relative './logging_hook'

module OpenApiSDK
  module SDKHooks
    class Registration
      extend T::Sig

      sig { params(hooks: Hooks).void }
      def self.init_hooks(hooks)
        # Register user-agent hook
        user_agent_hook = CustomUserAgentHook.new
        hooks.register_before_request_hook(user_agent_hook)

        # Register logging hook
        logging_hook = LoggingHook.new
        hooks.register_before_request_hook(logging_hook)
        hooks.register_after_success_hook(logging_hook)
        hooks.register_after_error_hook(logging_hook)
      end
    end
  end
end
```

### Common Hook Patterns

#### Logging Hook

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
        @logger.level = Logger::INFO
      end

      sig do
        override.params(
          hook_ctx: BeforeRequestHookContext,
          request: Faraday::Request
        ).returns(Faraday::Request)
      end
      def before_request(hook_ctx:, request:)
        @logger.info("#{request.method.upcase} #{request.path} [#{hook_ctx.operation_id}]")
        request
      end

      sig do
        override.params(
          hook_ctx: AfterSuccessHookContext,
          response: Faraday::Response
        ).returns(Faraday::Response)
      end
      def after_success(hook_ctx:, response:)
        @logger.info("Response: #{response.status} [#{hook_ctx.operation_id}]")
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
        @logger.error("Error in #{hook_ctx.operation_id}: #{error&.message}")
        response
      end
    end
  end
end
```

#### Rate Limit Hook

```ruby
# lib/open_api_sdk/sdk_hooks/rate_limit_hook.rb
# typed: true
# frozen_string_literal: true

module OpenApiSDK
  module SDKHooks
    class RateLimitHook < AbstractSDKHook
      extend T::Sig

      sig do
        override.params(
          hook_ctx: AfterSuccessHookContext,
          response: Faraday::Response
        ).returns(Faraday::Response)
      end
      def after_success(hook_ctx:, response:)
        remaining = response.headers['x-ratelimit-remaining']
        if remaining && remaining.to_i < 10
          warn "Rate limit warning: #{remaining} requests remaining"
        end
        response
      end
    end
  end
end
```

---

## RubyGems Publishing

### Configure Publishing in workflow.yaml

```yaml
workflowVersion: 1.0.0
speakeasyVersion: latest

sources:
  my-api:
    inputs:
      - location: https://api.example.com/openapi.yaml

targets:
  ruby-sdk:
    target: ruby
    source: my-api
    publish:
      rubygems:
        token: $rubygems_auth_token
```

### GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `RUBYGEMS_AUTH_TOKEN` | RubyGems API token for publishing |
| `SPEAKEASY_API_KEY` | Speakeasy API key |

### Getting a RubyGems Token

1. Log in to https://rubygems.org
2. Go to Settings > API Keys
3. Create a new key with "Push rubygem" scope
4. Add as `RUBYGEMS_AUTH_TOKEN` secret in GitHub

### Publishing Workflow

The generated `sdk_publish.yaml` workflow:

```yaml
name: Publish
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
      rubygems_auth_token: ${{ secrets.RUBYGEMS_AUTH_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
```

### Gemspec Configuration

The generated gemspec includes:

```ruby
Gem::Specification.new do |s|
  s.name        = 'my-sdk'
  s.version     = '1.0.0'
  s.platform    = Gem::Platform::RUBY
  s.licenses    = ['Apache-2.0']
  s.summary     = 'Ruby SDK for My API'
  s.homepage    = 'https://github.com/myorg/my-sdk-ruby'
  s.authors     = ['My Company']

  s.files         = Dir['{lib,test}/**/*']
  s.require_paths = ['lib']
  s.required_ruby_version = '>= 3.2'

  # Runtime dependencies
  s.add_dependency('faraday')
  s.add_dependency('faraday-multipart')
  s.add_dependency('faraday-retry', '~> 2.2.1')
  s.add_dependency('sorbet-runtime')  # If Sorbet enabled

  # Development dependencies
  s.add_development_dependency('minitest')
  s.add_development_dependency('rake')
  s.add_development_dependency('rubocop')
  s.add_development_dependency('sorbet')  # If Sorbet enabled
  s.add_development_dependency('tapioca')  # If Sorbet enabled
end
```

---

## Dependencies

Ruby SDKs include these core dependencies:

| Gem | Purpose |
|-----|---------|
| `faraday` | HTTP client with middleware support |
| `faraday-multipart` | Multipart form uploads |
| `faraday-retry` | Automatic request retries |
| `base64` | Base64 encoding/decoding |

When Sorbet is enabled:

| Gem | Purpose |
|-----|---------|
| `sorbet-runtime` | Runtime type checking |
| `sorbet` | Static type checker (dev) |
| `tapioca` | RBI file generation (dev) |

---

## Usage Examples

### Basic Usage

```ruby
require 'my_sdk'

# Initialize the SDK
client = OpenApiSDK::MySdk.new(
  security: OpenApiSDK::Models::Shared::Security.new(
    token: ENV['API_TOKEN']
  )
)

# Make API calls
response = client.resources.list

# Handle the response
response.items.each do |item|
  puts item.name
end
```

### With Custom Server URL

```ruby
client = OpenApiSDK::MySdk.new(
  server_url: 'https://staging-api.example.com',
  security: OpenApiSDK::Models::Shared::Security.new(
    token: ENV['API_TOKEN']
  )
)
```

### Error Handling

```ruby
begin
  response = client.resources.create(
    request: OpenApiSDK::Models::Operations::CreateResourceRequest.new(
      name: 'My Resource'
    )
  )
rescue OpenApiSDK::Models::Errors::BadRequest => e
  puts "Bad request: #{e.message}"
rescue OpenApiSDK::Models::Errors::Unauthorized => e
  puts "Unauthorized: #{e.message}"
rescue OpenApiSDK::Models::Errors::APIError => e
  puts "API error: #{e.message}"
end
```

### With Timeout

```ruby
response = client.resources.list(timeout_ms: 5000)
```

---

## Feature Support

### Authentication

| Type | Support |
|------|---------|
| HTTP Basic | Supported |
| API Key (bearer, header, query) | Supported |
| OAuth 2.0 Client Credentials | Supported |
| OAuth 2.0 Password Flow | Configurable |

### Data Types

| Type | Support |
|------|---------|
| Strings, Numbers, Booleans | Supported |
| Arrays, Objects | Supported |
| Date/DateTime | Supported |
| Enums | Supported |
| Union Types (oneOf) | Supported |
| Nullable Fields | Supported |

### Request Features

| Feature | Support |
|---------|---------|
| JSON bodies | Supported |
| Form data | Supported |
| Multipart uploads | Supported |
| Query parameters | Supported |
| Path parameters | Supported |
| Headers | Supported |
| Retries | Supported |

### Response Features

| Feature | Support |
|---------|---------|
| JSON responses | Supported |
| Binary responses | Supported |
| Pagination | Supported |
| Custom errors | Supported |

---

## Pre-defined TODO List

When configuring a Ruby SDK generation, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Review Ruby SDK feature requirements | Reviewing Ruby SDK feature requirements |
| 2 | Configure gen.yaml for Ruby target | Configuring gen.yaml for Ruby target |
| 3 | Set package name and version | Setting package name and version |
| 4 | Decide on Sorbet typing strategy | Deciding on Sorbet typing strategy |
| 5 | Configure error handling options | Configuring error handling options |
| 6 | Set up RubyGems publishing credentials | Setting up RubyGems publishing credentials |
| 7 | Test SDK with `bundle install` and `srb tc` | Testing SDK compilation |

**Usage:**
```
TodoWrite([
  {content: "Review Ruby SDK feature requirements", status: "pending", activeForm: "Reviewing Ruby SDK feature requirements"},
  {content: "Configure gen.yaml for Ruby target", status: "pending", activeForm: "Configuring gen.yaml for Ruby target"},
  {content: "Set package name and version", status: "pending", activeForm: "Setting package name and version"},
  {content: "Decide on Sorbet typing strategy", status: "pending", activeForm: "Deciding on Sorbet typing strategy"},
  {content: "Configure error handling options", status: "pending", activeForm: "Configuring error handling options"},
  {content: "Set up RubyGems publishing credentials", status: "pending", activeForm: "Setting up RubyGems publishing credentials"},
  {content: "Test SDK with bundle install and srb tc", status: "pending", activeForm: "Testing SDK compilation"}
])
```

**Nested workflows:**
- See `plans/sdk-generation.md` for the full SDK generation workflow
- See `sdk-customization/hooks.md` for hook implementation patterns
- See `spec-first/validation.md` for OpenAPI validation before generation
