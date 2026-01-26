---
short_description: Extract OpenAPI from Rails using RSwag
long_description: Rails applications use RSwag gem to generate OpenAPI from RSpec tests. This guide covers setup, test-based documentation, schema definitions, and customization.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/rails.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Rails OpenAPI Extraction

Rails uses `rswag` gem to generate OpenAPI documents from RSpec request tests.

## Installation

**Gemfile**:

```ruby
group :development, :test do
  gem 'rswag-specs'
end

gem 'rswag-api'
gem 'rswag-ui'
```

```bash
bundle install
rails generate rswag:api:install
rails generate rswag:ui:install
rails generate rswag:specs:install
```

## Configuration

**spec/swagger_helper.rb**:

```ruby
RSpec.configure do |config|
  config.openapi_root = Rails.root.join('swagger').to_s

  config.openapi_specs = {
    'v1/swagger.yaml' => {
      openapi: '3.0.1',
      info: {
        title: 'F1 Laps API',
        version: 'v1',
        description: 'API for accessing Formula 1 lap time data and analytics',
        contact: {
          name: 'API Support',
          email: 'support@f1laps.com'
        },
        license: {
          name: 'MIT',
          url: 'https://opensource.org/licenses/MIT'
        }
      },
      paths: {},
      components: {
        securitySchemes: {
          bearer_auth: {
            type: :http,
            scheme: :bearer,
            bearerFormat: 'JWT'
          }
        }
      },
      servers: [
        {
          url: 'http://{defaultHost}',
          variables: {
            defaultHost: {
              default: 'localhost:3000'
            }
          }
        }
      ]
    }
  }

  config.openapi_format = :yaml
end
```

## Request Spec Documentation

**spec/requests/api/v1/lap_times_spec.rb**:

```ruby
require 'swagger_helper'

RSpec.describe 'Lap Times API', type: :request do
  path '/api/v1/lap_times' do
    get 'List all lap times' do
      tags 'Lap Times'
      produces 'application/json'

      parameter name: :driver_id, in: :query, type: :integer, required: false, description: 'Filter by driver ID'
      parameter name: :circuit_id, in: :query, type: :integer, required: false, description: 'Filter by circuit ID'
      parameter name: :lap_min, in: :query, type: :integer, required: false, description: 'Minimum lap number'
      parameter name: :lap_max, in: :query, type: :integer, required: false, description: 'Maximum lap number'

      response '200', 'lap times found' do
        schema type: :array,
          items: {
            type: :object,
            properties: {
              id: { type: :integer },
              driver_id: { type: :integer },
              circuit_id: { type: :integer },
              time_ms: { type: :integer },
              lap_number: { type: :integer },
              created_at: { type: :string, format: 'date-time' },
              updated_at: { type: :string, format: 'date-time' }
            },
            required: ['id', 'driver_id', 'circuit_id', 'time_ms', 'lap_number']
          }

        run_test!
      end
    end

    post 'Create a lap time' do
      tags 'Lap Times'
      consumes 'application/json'
      produces 'application/json'

      parameter name: :lap_time, in: :body, schema: {
        type: :object,
        properties: {
          driver_id: { type: :integer },
          circuit_id: { type: :integer },
          time_ms: { type: :integer },
          lap_number: { type: :integer }
        },
        required: ['driver_id', 'circuit_id', 'time_ms', 'lap_number']
      }

      response '201', 'lap time created' do
        let(:lap_time) { { driver_id: 1, circuit_id: 1, time_ms: 80000, lap_number: 1 } }
        run_test!
      end

      response '422', 'invalid request' do
        let(:lap_time) { { driver_id: 1 } }
        run_test!
      end
    end
  end

  path '/api/v1/drivers/{driver_id}/lap_times' do
    get 'Get lap times for a specific driver' do
      tags 'Lap Times'
      produces 'application/json'

      parameter name: :driver_id, in: :path, type: :integer, required: true

      response '200', 'lap times found' do
        let(:driver_id) { 1 }
        schema type: :array,
          items: {
            type: :object,
            properties: {
              id: { type: :integer },
              circuit_id: { type: :integer },
              time_ms: { type: :integer },
              lap_number: { type: :integer },
              created_at: { type: :string, format: 'date-time' },
              updated_at: { type: :string, format: 'date-time' }
            }
          }
        run_test!
      end
    end
  end
end
```

## Reusable Schemas

**spec/swagger_helper.rb**:

```ruby
components: {
  schemas: {
    lap_time: {
      type: :object,
      properties: {
        driver_id: { type: :integer },
        circuit_id: { type: :integer },
        time_ms: { type: :integer },
        lap_number: { type: :integer }
      },
      required: ['driver_id', 'circuit_id', 'time_ms', 'lap_number']
    }
  }
}
```

Reference in specs:

```ruby
parameter name: :lap_time, in: :body, schema: { '$ref' => '#/components/schemas/lap_time' }
```

## Authentication

```ruby
path '/api/v1/protected_resource' do
  get 'Access protected resource' do
    tags 'Protected'
    security [bearer_auth: []]
    # ...
  end
end
```

## Generate OpenAPI Document

```bash
RAILS_ENV=test rake rswag:specs:swaggerize
```

This runs the specs and generates `swagger/v1/swagger.yaml`.

## Validation

```bash
speakeasy validate openapi -s swagger/v1/swagger.yaml
```

## SDK Generation

```bash
speakeasy quickstart --schema swagger/v1/swagger.yaml --target ruby --out-dir ./sdk
```

## Reference

- RSwag: https://github.com/rswag/rswag
- Rails: https://rubyonrails.org
- RSpec: https://rspec.info

---

## Pre-defined TODO List

When extracting OpenAPI from Rails, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Rails application exists | Verifying Rails application exists |
| 2 | Add rspec-rails to Gemfile if not present | Adding rspec-rails to Gemfile |
| 3 | Install rswag gem | Installing rswag gem |
| 4 | Run rswag install generator | Running rswag install generator |
| 5 | Create integration specs with swagger_doc | Creating integration specs |
| 6 | Generate OpenAPI document with rake rswag | Generating OpenAPI document |
| 7 | Validate spec with speakeasy validate | Validating spec with speakeasy validate |

**Usage:**
```
TodoWrite([
  {content: "Verify Rails application exists", status: "pending", activeForm: "Verifying Rails application exists"},
  {content: "Add rspec-rails to Gemfile if not present", status: "pending", activeForm: "Adding rspec-rails to Gemfile"},
  {content: "Install rswag gem", status: "pending", activeForm: "Installing rswag gem"},
  {content: "Run rswag install generator", status: "pending", activeForm: "Running rswag install generator"},
  {content: "Create integration specs with swagger_doc", status: "pending", activeForm: "Creating integration specs"},
  {content: "Generate OpenAPI document with rake rswag", status: "pending", activeForm: "Generating OpenAPI document"},
  {content: "Validate spec with speakeasy validate", status: "pending", activeForm: "Validating spec with speakeasy validate"}
])
```

**Nested workflows:**
- For validation issues, see `spec-first/validation.md`
- For SDK generation after extraction, see `plans/sdk-generation.md`

