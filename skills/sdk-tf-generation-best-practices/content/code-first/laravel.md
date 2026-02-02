---
short_description: Extract OpenAPI from Laravel using Scribe
long_description: Laravel applications use Scribe package to extract OpenAPI from source code, routes, and docblocks. This guide covers installation, configuration, and documentation techniques.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/laravel.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Laravel OpenAPI Extraction

Laravel uses `knuckleswtf/scribe` package to generate OpenAPI documents from source code introspection.

## Installation

```bash
composer require --dev knuckleswtf/scribe
php artisan vendor:publish --tag=scribe-config
```

This creates `config/scribe.php` configuration file.

## Configuration

**config/scribe.php**:

```php
return [
    // The HTML <title> for the generated documentation
    'title' => 'F1 Race API',

    // Short description of your API
    'description' => 'API for accessing Formula 1 race data',

    // Base URL for API requests
    'base_url' => env('APP_URL', 'http://localhost'),

    // Routes to document
    'routes' => [
        [
            'match' => [
                'prefixes' => ['api/*'],
            ],
        ],
    ],

    'type' => 'laravel',
    'theme' => 'default',
    'logo' => false,

    // Enable Try It Out feature
    'try_it_out' => [
        'enabled' => true,
    ],

    // Examples strategy - generates realistic examples from database
    'database_connections_to_transact' => [config('database.default')],
];
```

**Key configuration options:**

- `title`: API documentation title
- `description`: Brief API description
- `base_url`: Base URL for API endpoints
- `routes`: Specify which routes to document (by prefix, domain, etc.)
- `database_connections_to_transact`: Use database seeders to generate realistic examples

## Automatic Extraction

Scribe introspects your Laravel application to extract OpenAPI information:

- **Routes**: Automatically discovered from route definitions
- **Request bodies**: Extracted from validation rules
- **Response schemas**: Generated from API resources/serializers
- **Examples**: Created from database seeders (realistic data)

## Adding Descriptions with Docblocks

The first line of a docblock becomes the operation summary, the rest becomes the description:

```php
namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Race;

class RaceController extends Controller
{
    /**
     * Get races
     *
     * A collection of race resources, newest first, optionally filtered by circuit or season query parameters.
     */
    public function index(Request $request): RaceCollection
    {
        $query = Race::query();

        if ($request->has('circuit')) {
            $query->where('circuit_id', $request->circuit);
        }

        if ($request->has('season')) {
            $query->where('season', $request->season);
        }

        return new RaceCollection($query->get());
    }
}
```

Resulting OpenAPI:

```yaml
summary: Get races
operationId: getRaces
description: A collection of race resources, newest first, optionally filtered by circuit or season query parameters.
```

## Documenting Parameters with Attributes

Use Scribe attributes for detailed parameter documentation:

```php
use Knuckles\Scribe\Attributes\{QueryParam, BodyParam};

/**
 * Get races
 *
 * A collection of race resources, newest first, optionally filtered by circuit or season query parameters.
 */
#[QueryParam(name: 'season', type: 'string', description: 'Filter by season year', required: false, example: '2024')]
#[QueryParam(name: 'circuit', type: 'string', description: 'Filter by circuit name', required: false, example: 'Monaco')]
public function index(Request $request): RaceCollection
```

## Documenting Request Bodies

```php
/**
 * Create a race
 *
 * Allows authenticated users to submit a new Race resource to the system.
 */
#[Authenticated]
#[BodyParam(name: 'name', type: 'string', description: 'The name of the race.', required: true, example: 'Monaco Grand Prix')]
#[BodyParam(name: 'race_date', type: 'string', description: 'The date and time the race takes place, RFC 3339 in local timezone.', required: true, example: '2024-05-26T14:53:59')]
#[BodyParam(name: 'circuit_id', type: 'string', description: 'The Unique Identifier for the circuit where the race will be held.', required: true, example: '1234-1234-1234-1234')]
#[BodyParam(name: 'season', type: 'string', description: 'The season year for this race.', required: true, example: '2024')]
#[BodyParam(name: 'driver_ids', type: 'array', description: 'An array of Unique Identifiers for drivers participating in the race.', required: false, example: ["5678-5678-5678-5678", "6789-6789-6789-6789"])]
public function store(Request $request): RaceResource
{
    $validated = $request->validate([
        'name' => 'required|string',
        'circuit_id' => 'required|integer|exists:circuits,id',
        'race_date' => 'required|date',
        'season' => 'nullable|string',
        'driver_ids' => 'sometimes|array',
        'driver_ids.*' => 'integer|exists:drivers,id',
    ]);

    $race = Race::create([
        'name' => $validated['name'],
        'circuit_id' => $validated['circuit_id'],
        'race_date' => $validated['race_date'],
        'season' => $validated['season'] ?? null,
    ]);

    if (isset($validated['driver_ids'])) {
        $race->drivers()->attach($validated['driver_ids']);
    }

    return new RaceResource($race);
}
```

Scribe automatically extracts from Laravel validation rules but attributes provide better descriptions and examples.

## Tags

```php
use Knuckles\Scribe\Attributes\Group;

#[Group(name: 'Races', description: 'A series of endpoints that allow programmatic access to managing F1 races.')]
class RaceController extends Controller
{
    // ...
}
```

## Parameters

Scribe attributes for documenting parameters:

```php
use Knuckles\Scribe\Attributes\{QueryParam, BodyParam, UrlParam};

#[QueryParam(name: 'season', type: 'string', description: 'Filter by season year', required: false, example: '2024')]
#[QueryParam(name: 'circuit', type: 'string', description: 'Filter by circuit name', required: false, example: 'Monaco')]
public function index(Request $request)
```

## Request Bodies

```php
#[BodyParam(name: 'name', type: 'string', description: 'The name of the race.', required: true, example: 'Monaco Grand Prix')]
#[BodyParam(name: 'race_date', type: 'string', description: 'The date in RFC 3339 format.', required: true, example: '2024-05-26T14:53:59')]
```

## Generate OpenAPI Document

```bash
php artisan scribe:generate
```

OpenAPI document saved to `storage/app/private/scribe/openapi.yaml`.

Scribe performs these steps during generation:

1. Discovers API routes matching configured patterns
2. Extracts metadata from route definitions and docblocks
3. Generates request body schemas from validation rules
4. Creates response schemas from API resources
5. Generates realistic examples using database seeders
6. Outputs HTML documentation and OpenAPI YAML/JSON

## Common Issues

### Generic Operation IDs and Summaries

**Problem**: Default output has generic descriptions like "Display a listing of the resource."

**Solution**: Add docblock comments to controller methods:

```php
/**
 * Get drivers
 *
 * Returns a paginated list of all Formula 1 drivers.
 */
public function index()
```

### Missing or Poor Examples

**Problem**: Examples are not realistic or missing entirely.

**Solution**: Ensure database seeders are populated. Scribe uses seeded data to generate examples.

```php
// database/seeders/DatabaseSeeder.php
public function run()
{
    $this->call([
        DriverSeeder::class,
        CircuitSeeder::class,
    ]);
}
```

Then run:

```bash
php artisan db:seed
php artisan scribe:generate
```

### Validation Rule Extraction Issues

**Problem**: Request body documentation is incomplete or incorrect.

**Solution**: Use Scribe attributes to override or supplement validation rules:

```php
#[BodyParam(name: 'name', type: 'string', description: 'The driver name.', required: true, example: 'Lewis Hamilton')]
public function store(Request $request)
```

### Missing Route Documentation

**Problem**: Some routes are not appearing in the generated docs.

**Solution**: Check route prefix configuration in `config/scribe.php`:

```php
'routes' => [
    [
        'match' => [
            'prefixes' => ['api/*'],  // Ensure this matches your routes
        ],
    ],
],
```

## Validation

```bash
speakeasy validate openapi -s storage/app/private/scribe/openapi.yaml
```

## SDK Generation

```bash
speakeasy quickstart --schema storage/app/private/scribe/openapi.yaml --target php --out-dir ./sdk
```

## Reference

- Scribe: https://scribe.knuckles.wtf/laravel
- Laravel: https://laravel.com
- Config options: https://scribe.knuckles.wtf/laravel/reference/config

---

## Pre-defined TODO List

When extracting OpenAPI from Laravel, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Laravel application exists | Verifying Laravel application exists |
| 2 | Install knuckleswtf/scribe package via Composer | Installing knuckleswtf/scribe package |
| 3 | Publish Scribe configuration | Publishing Scribe configuration |
| 4 | Configure routes to document in config/scribe.php | Configuring routes to document |
| 5 | Add docblock comments to controller methods | Adding docblock comments to controllers |
| 6 | Add Scribe attributes for detailed parameter docs | Adding Scribe attributes |
| 7 | Ensure database seeders are populated | Ensuring database seeders are populated |
| 8 | Generate OpenAPI document with php artisan scribe:generate | Generating OpenAPI document |
| 9 | Validate spec with speakeasy validate | Validating spec with speakeasy validate |

**Usage:**
```
TodoWrite([
  {content: "Verify Laravel application exists", status: "pending", activeForm: "Verifying Laravel application exists"},
  {content: "Install knuckleswtf/scribe package via Composer", status: "pending", activeForm: "Installing knuckleswtf/scribe package"},
  {content: "Publish Scribe configuration", status: "pending", activeForm: "Publishing Scribe configuration"},
  {content: "Configure routes to document in config/scribe.php", status: "pending", activeForm: "Configuring routes to document"},
  {content: "Add docblock comments to controller methods", status: "pending", activeForm: "Adding docblock comments to controllers"},
  {content: "Add Scribe attributes for detailed parameter docs", status: "pending", activeForm: "Adding Scribe attributes"},
  {content: "Ensure database seeders are populated", status: "pending", activeForm: "Ensuring database seeders are populated"},
  {content: "Generate OpenAPI document with php artisan scribe:generate", status: "pending", activeForm: "Generating OpenAPI document"},
  {content: "Validate spec with speakeasy validate", status: "pending", activeForm: "Validating spec with speakeasy validate"}
])
```

**Nested workflows:**
- For validation issues, see `spec-first/validation.md`
- For SDK generation after extraction, see `plans/sdk-generation.md`

