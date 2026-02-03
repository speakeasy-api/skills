# Ruby SDK Configuration

Detailed gen.yaml configuration options for Ruby SDKs.

## gen.yaml Configuration

```yaml
ruby:
  version: 1.0.0
  packageName: "my_sdk"
  author: "MyOrg"

  # Method signatures
  maxMethodParams: 4
  methodArguments: require-security-and-request
```

## Package Structure

```
my_sdk/
├── my_sdk.gemspec
├── Gemfile
├── lib/
│   ├── my_sdk.rb              # Main entry point
│   ├── my_sdk/
│   │   ├── sdk.rb             # SDK class
│   │   ├── models/
│   │   │   ├── operations/    # Request/response classes
│   │   │   ├── shared/        # Shared models
│   │   │   └── errors.rb      # Exception classes
│   │   ├── hooks/             # Custom hooks (preserved)
│   │   │   └── registration.rb
│   │   └── utils/             # Internal utilities
└── docs/
```

## SDK Usage

```ruby
require 'my_sdk'

sdk = MySdk::SDK.new(
  security: MySdk::Shared::Security.new(
    api_key: 'your-api-key'
  )
)

user = sdk.users.get(id: '123')
puts user.name
```

## Security Configuration

```ruby
# API Key
sdk = MySdk::SDK.new(
  security: MySdk::Shared::Security.new(
    api_key: 'your-api-key'
  )
)

# Bearer Token
sdk = MySdk::SDK.new(
  security: MySdk::Shared::Security.new(
    bearer_auth: 'your-token'
  )
)

# OAuth2
sdk = MySdk::SDK.new(
  security: MySdk::Shared::Security.new(
    oauth2: 'your-oauth-token'
  )
)
```

## Server Selection

```ruby
# Named server from spec
sdk = MySdk::SDK.new(
  server: :production
)

# Custom URL
sdk = MySdk::SDK.new(
  server_url: 'https://api.example.com'
)
```

## Error Handling

```ruby
begin
  user = sdk.users.get(id: 'invalid-id')
rescue MySdk::Errors::APIError => e
  # Server returned error status
  puts "Status: #{e.status_code}"
  puts "Body: #{e.body}"
rescue MySdk::Errors::SDKError => e
  # Network, timeout, or other SDK error
  puts "SDK error: #{e.message}"
end
```

## Retries Configuration

```ruby
sdk = MySdk::SDK.new(
  retry_config: MySdk::Utils::RetryConfig.new(
    strategy: 'backoff',
    backoff: MySdk::Utils::BackoffStrategy.new(
      initial_interval: 500,
      max_interval: 60_000,
      exponent: 1.5,
      max_elapsed_time: 300_000
    ),
    retry_connection_errors: true
  )
)
```

## Timeouts

```ruby
# Global timeout (milliseconds)
sdk = MySdk::SDK.new(
  timeout_ms: 30_000
)

# Per-call override
user = sdk.users.create(request, timeout_ms: 60_000)
```

## Pagination

```ruby
# Auto-iterate all pages
sdk.users.list(limit: 50).each do |user|
  puts user.name
end

# Manual pagination
page = sdk.users.list(limit: 50)
while page
  page.users.each do |user|
    puts user.name
  end
  page = page.next
end
```

## Custom Hooks

Create hooks in `lib/my_sdk/hooks/registration.rb`:

```ruby
module MySdk
  module Hooks
    class Registration
      def self.init_hooks(hooks)
        hooks.before_request do |request|
          request.headers['X-Custom-Header'] = 'value'
          request
        end

        hooks.after_response do |response, request|
          puts "#{request.method} #{request.uri}: #{response.status}"
          response
        end

        hooks.on_error do |error, request|
          warn "Error: #{error.message}"
          raise error
        end
      end
    end
  end
end
```

## Rails Integration

Configure in initializer:

```ruby
# config/initializers/my_sdk.rb
Rails.application.config.my_sdk = MySdk::SDK.new(
  security: MySdk::Shared::Security.new(
    api_key: Rails.application.credentials.my_api_key
  )
)

# Helper method
module MySdkHelper
  def my_sdk
    Rails.application.config.my_sdk
  end
end

# In controller
class UsersController < ApplicationController
  include MySdkHelper

  def show
    @user = my_sdk.users.get(id: params[:id])
  end
end
```

## Faraday Configuration

For custom HTTP configuration:

```ruby
require 'faraday'

connection = Faraday.new do |f|
  f.request :json
  f.response :json
  f.adapter Faraday.default_adapter

  # Custom middleware
  f.use MyCustomMiddleware

  # SSL configuration (dev only)
  f.ssl.verify = false
end

sdk = MySdk::SDK.new(
  client: connection
)
```

## Debugging

```ruby
require 'logger'

# Enable debug logging
sdk = MySdk::SDK.new(
  debug: true
)

# Or with custom logger
logger = Logger.new($stderr)
logger.level = Logger::DEBUG

sdk = MySdk::SDK.new(
  logger: logger
)
```

## Sorbet Type Checking

Generated SDKs include Sorbet type signatures:

```ruby
# typed: strict

require 'my_sdk'

# Type-safe usage
T.let(sdk.users.get(id: '123'), MySdk::Models::User)

# Run type checker
# bundle exec srb tc
```

## Publishing to RubyGems

### Prerequisites

1. Create RubyGems account
2. Configure `my_sdk.gemspec`:

```ruby
Gem::Specification.new do |spec|
  spec.name          = 'my_sdk'
  spec.version       = '1.0.0'
  spec.authors       = ['MyOrg']
  spec.email         = ['dev@myorg.com']
  spec.summary       = 'Ruby SDK for MyAPI'
  spec.homepage      = 'https://github.com/myorg/my-sdk-ruby'
  spec.license       = 'MIT'

  spec.files         = Dir['lib/**/*']
  spec.require_paths = ['lib']

  spec.required_ruby_version = '>= 3.0'

  spec.add_dependency 'faraday', '~> 2.0'
  spec.add_dependency 'sorbet-runtime', '~> 0.5'
end
```

### Publish

```bash
# Build gem
gem build my_sdk.gemspec

# Push to RubyGems
gem push my_sdk-1.0.0.gem

# Users install with:
gem install my_sdk
# or in Gemfile:
gem 'my_sdk', '~> 1.0'
```

## Common Issues

| Issue | Solution |
|-------|----------|
| LoadError | Check `require` path matches gem structure |
| SSL errors | Configure Faraday SSL options |
| Encoding issues | Ensure UTF-8: `Encoding.default_external = 'UTF-8'` |
| Bundle errors | Run `bundle install` and `bundle exec` |
| Sorbet errors | Run `bundle exec srb tc` to check types |
