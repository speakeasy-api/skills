---
name: extract-openapi-laravel
description: >-
  Use when extracting OpenAPI from Laravel using l5-swagger.
  Triggers on "Laravel OpenAPI", "l5-swagger", "Laravel SDK", "Laravel API docs".
license: Apache-2.0
---

# extract-openapi-laravel

Extract an OpenAPI specification from Laravel using l5-swagger.

## When to Use

- User has a Laravel application
- User wants to generate an SDK from Laravel
- User says: "Laravel OpenAPI", "l5-swagger", "Laravel SDK"

## Installation

```bash
composer require darkaonline/l5-swagger
php artisan vendor:publish --provider "L5Swagger\L5SwaggerServiceProvider"
```

## Extraction

```bash
php artisan l5-swagger:generate
```

Output is written to `storage/api-docs/api-docs.json`.

## Annotation Examples

```php
/**
 * @OA\Info(title="My API", version="1.0.0")
 * @OA\Server(url="https://api.example.com")
 */
class Controller extends BaseController { }

/**
 * @OA\Get(
 *     path="/api/books",
 *     operationId="listBooks",
 *     tags={"Books"},
 *     @OA\Response(response=200, description="List of books")
 * )
 */
public function index() { ... }
```

## Adding Speakeasy Extensions

Use custom annotations or modify the generated spec:

```php
/**
 * @OA\Get(
 *     path="/api/books",
 *     operationId="listBooks",
 *     x={"x-speakeasy-group": "books", "x-speakeasy-name-override": "list"}
 * )
 */
```

Or post-process the generated JSON and add extensions.

## Post-Extraction

```bash
speakeasy lint openapi -s storage/api-docs/api-docs.json
speakeasy quickstart -s storage/api-docs/api-docs.json -t php -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
