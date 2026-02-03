# Laravel OpenAPI Extraction

Detailed guide for extracting OpenAPI specs from Laravel applications using L5-Swagger or Scramble.

## Option 1: Scramble (Recommended)

Modern, automatic OpenAPI generation for Laravel.

### Installation

```bash
composer require dedoc/scramble
```

### Configuration

```php
// config/scramble.php (publish with: php artisan vendor:publish --tag=scramble-config)
return [
    'api_path' => 'api',
    'api_domain' => null,

    'info' => [
        'title' => 'My API',
        'version' => '1.0.0',
        'description' => 'API description with **markdown** support',
    ],

    'servers' => [
        ['url' => 'https://api.example.com', 'description' => 'Production'],
        ['url' => 'https://staging.example.com', 'description' => 'Staging'],
    ],
];
```

### Extraction

```bash
# Generate spec file
php artisan scramble:export --path=openapi.json

# Or access at runtime
curl http://localhost:8000/docs/api.json > openapi.json
```

### Controller Documentation

```php
<?php

namespace App\Http\Controllers;

use App\Http\Requests\CreateBurgerRequest;
use App\Http\Requests\UpdateBurgerRequest;
use App\Http\Resources\BurgerResource;
use App\Http\Resources\BurgerCollection;
use App\Models\Burger;
use Illuminate\Http\Request;

/**
 * @tags burgers
 */
class BurgerController extends Controller
{
    /**
     * List burgers
     *
     * Returns a paginated list of all burgers.
     *
     * @operationId listBurgers
     */
    public function index(Request $request): BurgerCollection
    {
        $burgers = Burger::query()
            ->paginate($request->input('limit', 20));

        return new BurgerCollection($burgers);
    }

    /**
     * Get burger
     *
     * Returns a single burger by ID.
     *
     * @operationId getBurger
     */
    public function show(Burger $burger): BurgerResource
    {
        return new BurgerResource($burger);
    }

    /**
     * Create burger
     *
     * @operationId createBurger
     * @response 201
     */
    public function store(CreateBurgerRequest $request): BurgerResource
    {
        $burger = Burger::create($request->validated());
        return new BurgerResource($burger);
    }

    /**
     * Update burger
     *
     * @operationId updateBurger
     */
    public function update(UpdateBurgerRequest $request, Burger $burger): BurgerResource
    {
        $burger->update($request->validated());
        return new BurgerResource($burger);
    }

    /**
     * Delete burger
     *
     * @operationId deleteBurger
     * @response 204
     */
    public function destroy(Burger $burger): \Illuminate\Http\Response
    {
        $burger->delete();
        return response()->noContent();
    }
}
```

### Form Requests (Auto-documented)

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CreateBurgerRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'name' => ['required', 'string', 'max:100'],
            'price' => ['required', 'numeric', 'min:0.01'],
            'description' => ['nullable', 'string', 'max:500'],
        ];
    }

    /**
     * @return array<string, string>
     */
    public function bodyParameters(): array
    {
        return [
            'name' => [
                'description' => 'Burger name',
                'example' => 'Classic Burger',
            ],
            'price' => [
                'description' => 'Price in USD',
                'example' => 9.99,
            ],
            'description' => [
                'description' => 'Optional description',
                'example' => 'A delicious classic burger',
            ],
        ];
    }
}
```

### API Resources (Auto-documented)

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @property string $id
 * @property string $name
 * @property float $price
 * @property string|null $description
 * @property \Carbon\Carbon $created_at
 */
class BurgerResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            /** @var string Unique identifier */
            'id' => $this->id,
            /** @var string Burger name */
            'name' => $this->name,
            /** @var float Price in USD */
            'price' => $this->price,
            /** @var string|null Optional description */
            'description' => $this->description,
            /** @var string ISO 8601 timestamp */
            'created_at' => $this->created_at->toIso8601String(),
        ];
    }
}
```

## Option 2: L5-Swagger

Annotation-based approach using OpenAPI attributes.

### Installation

```bash
composer require darkaonline/l5-swagger
php artisan vendor:publish --provider "L5Swagger\L5SwaggerServiceProvider"
```

### Configuration

```php
// config/l5-swagger.php
return [
    'documentations' => [
        'default' => [
            'api' => [
                'title' => 'My API',
            ],
            'routes' => [
                'api' => 'api/documentation',
            ],
            'paths' => [
                'docs_json' => 'api-docs.json',
                'docs_yaml' => 'api-docs.yaml',
                'annotations' => [
                    base_path('app/Http/Controllers'),
                    base_path('app/OpenApi'),
                ],
            ],
        ],
    ],
    'defaults' => [
        'routes' => [
            'docs' => 'docs',
            'oauth2_callback' => 'api/oauth2-callback',
        ],
    ],
];
```

### OpenAPI Info

```php
<?php
// app/OpenApi/OpenApiSpec.php

namespace App\OpenApi;

use OpenApi\Attributes as OA;

#[OA\Info(
    version: '1.0.0',
    title: 'My API',
    description: 'API description with **markdown** support'
)]
#[OA\Server(url: 'https://api.example.com', description: 'Production')]
#[OA\Server(url: 'https://staging.example.com', description: 'Staging')]
#[OA\Tag(name: 'burgers', description: 'Burger operations')]
#[OA\Tag(name: 'orders', description: 'Order management')]
class OpenApiSpec {}
```

### Controller with Attributes

```php
<?php

namespace App\Http\Controllers;

use OpenApi\Attributes as OA;

class BurgerController extends Controller
{
    #[OA\Get(
        path: '/burgers',
        operationId: 'listBurgers',
        summary: 'List burgers',
        description: 'Returns a paginated list of all burgers',
        tags: ['burgers']
    )]
    #[OA\Parameter(
        name: 'limit',
        in: 'query',
        description: 'Page size',
        required: false,
        schema: new OA\Schema(type: 'integer', default: 20, minimum: 1, maximum: 100)
    )]
    #[OA\Parameter(
        name: 'offset',
        in: 'query',
        description: 'Page offset',
        required: false,
        schema: new OA\Schema(type: 'integer', default: 0, minimum: 0)
    )]
    #[OA\Response(
        response: 200,
        description: 'List of burgers',
        content: new OA\JsonContent(
            type: 'array',
            items: new OA\Items(ref: '#/components/schemas/Burger')
        )
    )]
    public function index(Request $request)
    {
        // ...
    }

    #[OA\Get(
        path: '/burgers/{id}',
        operationId: 'getBurger',
        summary: 'Get burger',
        tags: ['burgers']
    )]
    #[OA\Parameter(
        name: 'id',
        in: 'path',
        description: 'Burger ID',
        required: true,
        schema: new OA\Schema(type: 'string')
    )]
    #[OA\Response(
        response: 200,
        description: 'Burger found',
        content: new OA\JsonContent(ref: '#/components/schemas/Burger')
    )]
    #[OA\Response(response: 404, description: 'Burger not found')]
    public function show(Burger $burger)
    {
        // ...
    }

    #[OA\Post(
        path: '/burgers',
        operationId: 'createBurger',
        summary: 'Create burger',
        tags: ['burgers']
    )]
    #[OA\RequestBody(
        required: true,
        content: new OA\JsonContent(ref: '#/components/schemas/CreateBurger')
    )]
    #[OA\Response(
        response: 201,
        description: 'Burger created',
        content: new OA\JsonContent(ref: '#/components/schemas/Burger')
    )]
    #[OA\Response(response: 422, description: 'Validation error')]
    public function store(CreateBurgerRequest $request)
    {
        // ...
    }
}
```

### Schema Definitions

```php
<?php
// app/OpenApi/Schemas.php

namespace App\OpenApi;

use OpenApi\Attributes as OA;

#[OA\Schema(
    schema: 'Burger',
    type: 'object',
    required: ['id', 'name', 'price']
)]
class BurgerSchema
{
    #[OA\Property(description: 'Unique identifier', example: '123')]
    public string $id;

    #[OA\Property(description: 'Burger name', maxLength: 100, example: 'Classic Burger')]
    public string $name;

    #[OA\Property(description: 'Price in USD', minimum: 0.01, example: 9.99)]
    public float $price;

    #[OA\Property(description: 'Optional description', nullable: true)]
    public ?string $description;
}

#[OA\Schema(
    schema: 'CreateBurger',
    type: 'object',
    required: ['name', 'price']
)]
class CreateBurgerSchema
{
    #[OA\Property(description: 'Burger name', maxLength: 100, example: 'Classic Burger')]
    public string $name;

    #[OA\Property(description: 'Price in USD', minimum: 0.01, example: 9.99)]
    public float $price;

    #[OA\Property(description: 'Optional description')]
    public ?string $description;
}

#[OA\Schema(schema: 'Error', type: 'object', required: ['message'])]
class ErrorSchema
{
    #[OA\Property(description: 'Error message')]
    public string $message;

    #[OA\Property(description: 'Error code')]
    public ?string $code;
}
```

### Extraction

```bash
# Generate spec
php artisan l5-swagger:generate

# Output location
cat storage/api-docs/api-docs.json
```

## Speakeasy Extensions

### With Scramble

```php
// config/scramble.php
return [
    'extensions' => [
        'x-speakeasy-retries' => [
            'strategy' => 'backoff',
            'backoff' => [
                'initialInterval' => 500,
                'maxInterval' => 60000,
                'exponent' => 1.5,
            ],
            'statusCodes' => ['5XX', '429'],
        ],
    ],
];

// Per-operation in controller
/**
 * List burgers
 *
 * @operationId listBurgers
 * @x-speakeasy-group burgers
 * @x-speakeasy-name-override list
 */
public function index(): BurgerCollection
{
    // ...
}
```

### With L5-Swagger

```php
#[OA\Get(
    path: '/burgers',
    operationId: 'listBurgers',
    tags: ['burgers'],
    x: [
        'speakeasy-group' => 'burgers',
        'speakeasy-name-override' => 'list',
        'speakeasy-retries' => [
            'strategy' => 'backoff',
            'backoff' => [
                'initialInterval' => 500,
                'maxInterval' => 60000,
                'exponent' => 1.5,
            ],
            'statusCodes' => ['5XX', '429'],
        ],
    ]
)]
public function index(Request $request)
{
    // ...
}
```

### Pagination

```php
#[OA\Get(
    path: '/burgers',
    operationId: 'listBurgers',
    x: [
        'speakeasy-pagination' => [
            'type' => 'offsetLimit',
            'inputs' => [
                ['name' => 'offset', 'in' => 'parameters', 'type' => 'offset'],
                ['name' => 'limit', 'in' => 'parameters', 'type' => 'limit'],
            ],
            'outputs' => [
                'results' => '$.data',
                'numPages' => '$.meta.last_page',
            ],
        ],
    ]
)]
public function index(Request $request)
{
    // ...
}
```

## Authentication

### Security Schemes

```php
// app/OpenApi/OpenApiSpec.php

#[OA\SecurityScheme(
    securityScheme: 'bearer-auth',
    type: 'http',
    scheme: 'bearer',
    bearerFormat: 'JWT'
)]
#[OA\SecurityScheme(
    securityScheme: 'api-key',
    type: 'apiKey',
    in: 'header',
    name: 'X-API-Key'
)]
class OpenApiSpec {}
```

### Apply to Endpoints

```php
// Protected endpoint
#[OA\Get(
    path: '/protected',
    security: [['bearer-auth' => []]],
    // ...
)]
public function protectedEndpoint()
{
    // ...
}

// Public endpoint
#[OA\Get(
    path: '/public',
    security: [],
    // ...
)]
public function publicEndpoint()
{
    // ...
}

// Multiple auth options
#[OA\Get(
    path: '/flexible',
    security: [['bearer-auth' => []], ['api-key' => []]],
    // ...
)]
public function flexibleAuth()
{
    // ...
}
```

## File Upload

```php
#[OA\Post(
    path: '/upload',
    operationId: 'uploadFile',
    tags: ['files']
)]
#[OA\RequestBody(
    required: true,
    content: new OA\MediaType(
        mediaType: 'multipart/form-data',
        schema: new OA\Schema(
            properties: [
                new OA\Property(
                    property: 'file',
                    type: 'string',
                    format: 'binary',
                    description: 'File to upload'
                ),
                new OA\Property(
                    property: 'caption',
                    type: 'string',
                    description: 'Optional caption'
                ),
            ],
            required: ['file']
        )
    )
)]
#[OA\Response(response: 200, description: 'File uploaded')]
public function upload(Request $request)
{
    // ...
}
```

## Webhooks

```php
// app/OpenApi/Webhooks.php

#[OA\PathItem(path: 'order-status-changed')]
class OrderWebhook
{
    #[OA\Post(
        operationId: 'onOrderStatusChanged',
        summary: 'Order status changed',
        description: 'Triggered when an order status changes'
    )]
    #[OA\RequestBody(
        content: new OA\JsonContent(
            properties: [
                new OA\Property(property: 'order_id', type: 'string'),
                new OA\Property(
                    property: 'status',
                    type: 'string',
                    enum: ['pending', 'processing', 'shipped', 'delivered']
                ),
                new OA\Property(property: 'timestamp', type: 'string', format: 'date-time'),
            ]
        )
    )]
    #[OA\Response(response: 200, description: 'Webhook received')]
    public function handle() {}
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Scramble not detecting routes | Ensure routes are in `routes/api.php` |
| Missing return types | Add return type hints to controller methods |
| Schemas not generated | Run `php artisan l5-swagger:generate` |
| Form request not documented | Add `bodyParameters()` method to request class |
| Validation rules not reflected | Use explicit schema definitions for complex rules |
