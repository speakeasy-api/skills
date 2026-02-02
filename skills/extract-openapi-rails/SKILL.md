---
name: extract-openapi-rails
description: >-
  Use when extracting OpenAPI from Ruby on Rails using rswag.
  Triggers on "Rails OpenAPI", "rswag", "Rails SDK", "Rails swagger".
license: Apache-2.0
---

# extract-openapi-rails

Extract an OpenAPI specification from Ruby on Rails using rswag.

## When to Use

- User has a Rails application with rswag
- User wants to generate an SDK from Rails
- User says: "Rails OpenAPI", "rswag", "Rails SDK"

## Installation

Add to **Gemfile:**

```ruby
gem 'rswag-api'
gem 'rswag-ui'
gem 'rswag-specs'
```

```bash
bundle install
rails g rswag:install
```

## Extraction

```bash
rails rswag:specs:swaggerize
```

Output is written to `swagger/v1/swagger.yaml` by default.

## Configuration

**config/initializers/rswag_api.rb:**

```ruby
Rswag::Api.configure do |c|
  c.swagger_root = Rails.root.join('swagger')
end
```

## Writing Specs

```ruby
# spec/requests/api/v1/books_spec.rb
require 'swagger_helper'

RSpec.describe 'Books API' do
  path '/api/v1/books' do
    get 'List books' do
      tags 'Books'
      produces 'application/json'

      response '200', 'books found' do
        schema type: :array, items: { '$ref' => '#/components/schemas/Book' }
        run_test!
      end
    end
  end
end
```

## Adding Speakeasy Extensions

Add extensions in the swagger_helper or modify the generated spec:

```ruby
# spec/swagger_helper.rb
RSpec.configure do |config|
  config.swagger_docs = {
    'v1/swagger.yaml' => {
      openapi: '3.0.1',
      info: { title: 'API V1', version: 'v1' },
      'x-speakeasy-retries': {
        strategy: 'backoff',
        statusCodes: ['5XX']
      }
    }
  }
end
```

## Post-Extraction

```bash
speakeasy lint openapi -s swagger/v1/swagger.yaml
speakeasy quickstart -s swagger/v1/swagger.yaml -t ruby -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
