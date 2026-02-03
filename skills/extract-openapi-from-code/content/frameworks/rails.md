# Ruby on Rails OpenAPI Extraction

Detailed guide for extracting OpenAPI specs from Rails applications using rswag.

## Installation

Add to Gemfile:

```ruby
gem 'rswag-api'
gem 'rswag-ui'
gem 'rswag-specs'
```

```bash
bundle install
rails g rswag:install
```

## Configuration

### Swagger Configuration

```ruby
# config/initializers/rswag_api.rb
Rswag::Api.configure do |c|
  c.openapi_root = Rails.root.to_s + '/swagger'
end

# config/initializers/rswag_ui.rb
Rswag::Ui.configure do |c|
  c.openapi_endpoint '/api-docs/v1/swagger.yaml', 'API V1 Docs'
end
```

### Swagger Helper

```ruby
# spec/swagger_helper.rb
require 'rails_helper'

RSpec.configure do |config|
  config.openapi_root = Rails.root.to_s + '/swagger'

  config.openapi_specs = {
    'v1/swagger.yaml' => {
      openapi: '3.0.1',
      info: {
        title: 'My API',
        version: 'v1',
        description: 'API description with **markdown** support'
      },
      servers: [
        { url: 'https://api.example.com', description: 'Production' },
        { url: 'https://staging.example.com', description: 'Staging' }
      ],
      components: {
        securitySchemes: {
          'bearer-auth': {
            type: :http,
            scheme: :bearer,
            bearerFormat: 'JWT'
          },
          'api-key': {
            type: :apiKey,
            name: 'X-API-Key',
            in: :header
          }
        }
      }
    }
  }

  config.openapi_format = :yaml
end
```

## Extraction

```bash
# Generate OpenAPI spec from tests
rails rswag:specs:swaggerize

# Or run specific specs
RAILS_ENV=test bundle exec rspec spec/requests --format Rswag::Specs::SwaggerFormatter

# Output location
cat swagger/v1/swagger.yaml
```

## Request Specs

### Basic CRUD

```ruby
# spec/requests/burgers_spec.rb
require 'swagger_helper'

RSpec.describe 'Burgers API', type: :request do
  path '/burgers' do
    get 'List burgers' do
      tags 'burgers'
      operationId 'listBurgers'
      description 'Returns a paginated list of all burgers'
      produces 'application/json'

      parameter name: :limit,
                in: :query,
                type: :integer,
                required: false,
                description: 'Page size',
                schema: { default: 20, minimum: 1, maximum: 100 }

      parameter name: :offset,
                in: :query,
                type: :integer,
                required: false,
                description: 'Page offset',
                schema: { default: 0, minimum: 0 }

      response '200', 'Success' do
        schema type: :array,
               items: { '$ref' => '#/components/schemas/Burger' }

        run_test!
      end
    end

    post 'Create burger' do
      tags 'burgers'
      operationId 'createBurger'
      consumes 'application/json'
      produces 'application/json'

      parameter name: :burger, in: :body, schema: {
        type: :object,
        properties: {
          name: { type: :string, maxLength: 100, description: 'Burger name' },
          price: { type: :number, minimum: 0.01, description: 'Price in USD' },
          description: { type: :string, description: 'Optional description' }
        },
        required: %w[name price],
        example: {
          name: 'Classic Burger',
          price: 9.99,
          description: 'A delicious classic burger'
        }
      }

      response '201', 'Burger created' do
        schema '$ref' => '#/components/schemas/Burger'
        run_test!
      end

      response '422', 'Validation error' do
        schema '$ref' => '#/components/schemas/Error'
        run_test!
      end
    end
  end

  path '/burgers/{id}' do
    parameter name: :id, in: :path, type: :string, description: 'Burger ID'

    get 'Get burger' do
      tags 'burgers'
      operationId 'getBurger'
      produces 'application/json'

      response '200', 'Burger found' do
        schema '$ref' => '#/components/schemas/Burger'

        let(:id) { Burger.create!(name: 'Test', price: 9.99).id }
        run_test!
      end

      response '404', 'Burger not found' do
        schema '$ref' => '#/components/schemas/Error'

        let(:id) { 'invalid' }
        run_test!
      end
    end

    put 'Update burger' do
      tags 'burgers'
      operationId 'updateBurger'
      consumes 'application/json'
      produces 'application/json'

      parameter name: :burger, in: :body, schema: {
        type: :object,
        properties: {
          name: { type: :string, maxLength: 100 },
          price: { type: :number, minimum: 0.01 },
          description: { type: :string }
        }
      }

      response '200', 'Burger updated' do
        schema '$ref' => '#/components/schemas/Burger'

        let(:id) { Burger.create!(name: 'Test', price: 9.99).id }
        let(:burger) { { name: 'Updated Burger' } }
        run_test!
      end
    end

    delete 'Delete burger' do
      tags 'burgers'
      operationId 'deleteBurger'

      response '204', 'Burger deleted' do
        let(:id) { Burger.create!(name: 'Test', price: 9.99).id }
        run_test!
      end
    end
  end
end
```

### Component Schemas

```ruby
# spec/swagger_helper.rb
config.openapi_specs = {
  'v1/swagger.yaml' => {
    openapi: '3.0.1',
    info: { title: 'My API', version: 'v1' },
    components: {
      schemas: {
        Burger: {
          type: :object,
          properties: {
            id: { type: :string, description: 'Unique identifier' },
            name: { type: :string, maxLength: 100, description: 'Burger name' },
            price: { type: :number, minimum: 0.01, description: 'Price in USD' },
            description: { type: :string, nullable: true, description: 'Optional description' },
            created_at: { type: :string, format: 'date-time' },
            updated_at: { type: :string, format: 'date-time' }
          },
          required: %w[id name price]
        },
        Error: {
          type: :object,
          properties: {
            message: { type: :string, description: 'Error message' },
            code: { type: :string, description: 'Error code' }
          },
          required: %w[message]
        },
        PaginatedBurgers: {
          type: :object,
          properties: {
            data: {
              type: :array,
              items: { '$ref' => '#/components/schemas/Burger' }
            },
            meta: {
              type: :object,
              properties: {
                total: { type: :integer },
                page: { type: :integer },
                per_page: { type: :integer },
                total_pages: { type: :integer }
              }
            }
          }
        }
      }
    }
  }
}
```

## Speakeasy Extensions

### Per-Operation

```ruby
get 'List burgers' do
  tags 'burgers'
  operationId 'listBurgers'

  # Speakeasy extensions
  extension 'x-speakeasy-group', 'burgers'
  extension 'x-speakeasy-name-override', 'list'
  extension 'x-speakeasy-retries', {
    strategy: 'backoff',
    backoff: {
      initialInterval: 500,
      maxInterval: 60000,
      exponent: 1.5
    },
    statusCodes: ['5XX', '429']
  }

  # ...
end
```

### Pagination

```ruby
get 'List burgers' do
  tags 'burgers'
  operationId 'listBurgers'

  extension 'x-speakeasy-pagination', {
    type: 'offsetLimit',
    inputs: [
      { name: 'offset', in: 'parameters', type: 'offset' },
      { name: 'limit', in: 'parameters', type: 'limit' }
    ],
    outputs: {
      results: '$.data',
      numPages: '$.meta.total_pages'
    }
  }

  parameter name: :offset, in: :query, type: :integer, required: false
  parameter name: :limit, in: :query, type: :integer, required: false

  # ...
end
```

### Global Extensions

```ruby
# spec/swagger_helper.rb
config.openapi_specs = {
  'v1/swagger.yaml' => {
    openapi: '3.0.1',
    info: { title: 'My API', version: 'v1' },
    'x-speakeasy-retries': {
      strategy: 'backoff',
      backoff: {
        initialInterval: 500,
        maxInterval: 60000,
        exponent: 1.5
      },
      statusCodes: ['5XX', '429'],
      retryConnectionErrors: true
    }
  }
}
```

## Authentication

### Security Requirements

```ruby
# Protected endpoint
get 'List resources' do
  tags 'resources'
  operationId 'listResources'
  security [{ 'bearer-auth': [] }]

  # ...
end

# API key auth
get 'API resource' do
  tags 'resources'
  operationId 'getApiResource'
  security [{ 'api-key': [] }]

  # ...
end

# Multiple auth options
get 'Flexible auth resource' do
  tags 'resources'
  operationId 'getFlexibleResource'
  security [{ 'bearer-auth': [] }, { 'api-key': [] }]

  # ...
end

# Public endpoint (no auth)
get 'Public resource' do
  tags 'resources'
  operationId 'getPublicResource'
  security []

  # ...
end
```

## Tags

```ruby
# spec/swagger_helper.rb
config.openapi_specs = {
  'v1/swagger.yaml' => {
    openapi: '3.0.1',
    info: { title: 'My API', version: 'v1' },
    tags: [
      {
        name: 'burgers',
        description: 'Burger operations',
        externalDocs: {
          description: 'Learn more',
          url: 'https://example.com/docs/burgers'
        }
      },
      {
        name: 'orders',
        description: 'Order management'
      }
    ]
  }
}
```

## File Upload

```ruby
post 'Upload image' do
  tags 'files'
  operationId 'uploadImage'
  consumes 'multipart/form-data'
  produces 'application/json'

  parameter name: :file,
            in: :formData,
            type: :file,
            required: true,
            description: 'Image file to upload'

  parameter name: :caption,
            in: :formData,
            type: :string,
            required: false,
            description: 'Optional caption'

  response '200', 'File uploaded' do
    schema type: :object,
           properties: {
             url: { type: :string, format: 'uri' },
             filename: { type: :string }
           }
    run_test!
  end
end
```

## Request Examples

```ruby
post 'Create burger' do
  tags 'burgers'
  operationId 'createBurger'
  consumes 'application/json'

  parameter name: :burger, in: :body, schema: {
    type: :object,
    properties: {
      name: { type: :string },
      price: { type: :number },
      description: { type: :string }
    },
    required: %w[name price]
  }

  request_body_example value: {
    name: 'Classic Burger',
    price: 9.99,
    description: 'A delicious classic burger'
  }, name: 'classic', summary: 'Classic burger example'

  request_body_example value: {
    name: 'Veggie Burger',
    price: 11.99
  }, name: 'veggie', summary: 'Veggie burger example'

  # ...
end
```

## Webhooks

```ruby
# spec/swagger_helper.rb
config.openapi_specs = {
  'v1/swagger.yaml' => {
    openapi: '3.0.1',
    info: { title: 'My API', version: 'v1' },
    webhooks: {
      'order-status-changed': {
        post: {
          operationId: 'onOrderStatusChanged',
          summary: 'Order status changed',
          description: 'Triggered when an order status changes',
          requestBody: {
            content: {
              'application/json': {
                schema: {
                  type: :object,
                  properties: {
                    order_id: { type: :string },
                    status: { type: :string, enum: %w[pending processing shipped delivered] },
                    timestamp: { type: :string, format: 'date-time' }
                  }
                }
              }
            }
          },
          responses: {
            '200': { description: 'Webhook received' }
          }
        }
      }
    }
  }
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Specs not generating | Run `rails rswag:specs:swaggerize` after adding tests |
| Missing schemas | Define in `components.schemas` in swagger_helper |
| Tests failing | Ensure factories/fixtures create valid test data |
| Wrong content type | Use correct `consumes`/`produces` declarations |
| Security not applied | Add `security` to individual operations |
