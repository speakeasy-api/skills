---
name: generate-sdk-for-ruby
description: >-
  Use when generating a Ruby SDK with Speakeasy. Covers gen.yaml configuration,
  Sorbet typing, Faraday HTTP client, RubyGems publishing.
  Triggers on "Ruby SDK", "generate Ruby", "RubyGems publish", "Sorbet typing",
  "Ruby client gem".
license: Apache-2.0
---

# Generate SDK for Ruby

Configure and generate idiomatic Ruby SDKs with Speakeasy, featuring optional Sorbet typing, Faraday HTTP client, and RubyGems publishing.

## When to Use

- Generating a new Ruby SDK from an OpenAPI spec
- Configuring Ruby-specific gen.yaml options
- Setting up Sorbet type checking
- Publishing to RubyGems
- User says: "Ruby SDK", "RubyGems", "Sorbet", "Ruby gem"

## Quick Start

```bash
speakeasy quickstart --skip-interactive --output console \
  -s openapi.yaml -t ruby -n "MySDK" -p "my-sdk"
```

## Essential gen.yaml Configuration

```yaml
ruby:
  version: 1.0.0
  packageName: my-sdk
  module: MySdk
  author: "Your Name"

  # Optional: Sorbet type checking
  typingStrategy: sorbet       # or "none"

  # Error handling
  baseErrorName: MySdkError
  defaultErrorName: APIError
```

## Package Structure

```
lib/
├── my_sdk.rb                # Main entry point
└── open_api_sdk/
    ├── sdk.rb               # SDK class
    ├── sdkconfiguration.rb
    ├── sdk_hooks/
    │   ├── hooks.rb         # Hook manager
    │   ├── types.rb         # Hook types
    │   └── registration.rb  # Custom hooks (preserved)
    ├── models/
    │   ├── operations/      # Request/response models
    │   ├── shared/          # Shared components
    │   └── errors/          # Error types
    └── utils/
sorbet/                      # Sorbet types (if enabled)
my_sdk.gemspec
```

## Client Usage

```ruby
require 'my_sdk'

# Create client
sdk = MySdk::SDK.new
sdk.config_security(
  MySdk::Shared::Security.new(api_key: 'your-api-key')
)

# Make API call
response = sdk.resources.create(
  MySdk::Operations::CreateRequest.new(name: 'my-resource')
)

puts response.resource.id if response.resource
```

## Sorbet Type Checking

Enable with `typingStrategy: sorbet`:

```ruby
# typed: strict
extend T::Sig

sig { params(request: Operations::CreateRequest).returns(Operations::CreateResponse) }
def create(request)
  # ...
end
```

Run type checking:
```bash
bundle exec srb tc
```

## SDK Hooks

Register hooks in `sdk_hooks/registration.rb`:

```ruby
module MySdk
  module SDKHooks
    def self.register_hooks(hooks)
      hooks.register_before_request_hook(CustomHeaderHook.new)
    end
  end

  class CustomHeaderHook
    def before_request(context, request)
      request['X-Custom'] = 'value'
      request
    end
  end
end
```

## RubyGems Publishing

1. Configure in gen.yaml and gemspec
2. Build: `gem build my_sdk.gemspec`
3. Publish: `gem push my_sdk-1.0.0.gem`

## Common Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `module` | OpenApiSdk | Ruby module namespace |
| `typingStrategy` | none | `sorbet` or `none` |
| `packageName` | openapi | Gem name |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Sorbet errors | Run `bundle exec tapioca gems` |
| Faraday timeout | Configure timeout in client setup |
| Gem build fails | Check gemspec metadata |

## Related Skills

- `start-new-sdk-project` - Initial SDK setup
- `customize-sdk-hooks` - Hook implementation
- `setup-sdk-testing` - Testing patterns
- `manage-openapi-overlays` - Spec customization
