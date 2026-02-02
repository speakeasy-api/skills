---
name: extract-openapi-from-code
description: Use when extracting OpenAPI from existing API code. Routes to framework-specific skills. Triggers on "extract OpenAPI", "code first", "generate spec from code", "existing API".
license: Apache-2.0
---

# extract-openapi-from-code

Extract an OpenAPI specification from an existing API codebase. This skill routes to framework-specific extraction skills.

## When to Use

- User has an existing API and wants to generate an OpenAPI spec
- User wants to create an SDK from code without an existing spec
- User says: "extract OpenAPI", "code first", "generate spec from code"

## Framework Routing

| Framework | Skill | Extraction Method |
|-----------|-------|-------------------|
| FastAPI | `extract-openapi-fastapi` | `app.openapi()` script |
| Django REST | `extract-openapi-django` | `manage.py spectacular` |
| Flask | `extract-openapi-flask` | `flask openapi write` |
| Spring Boot | `extract-openapi-spring` | HTTP endpoint |
| NestJS | `extract-openapi-nestjs` | Script or HTTP |
| Hono | `extract-openapi-hono` | Script export |
| Rails | `extract-openapi-rails` | `rails rswag:specs:swaggerize` |
| Laravel | `extract-openapi-laravel` | `artisan l5-swagger:generate` |

## Quick Reference

### Python Frameworks

```bash
# FastAPI (no server needed)
python -c "import json; from main import app; print(json.dumps(app.openapi()))" > openapi.json

# Django REST Framework
python manage.py spectacular --file openapi.yaml

# Flask (flask-smorest)
flask openapi write openapi.json
```

### Java/Kotlin

```bash
# Spring Boot (requires running server)
./mvnw spring-boot:run &
sleep 15
curl http://localhost:8080/v3/api-docs -o openapi.json
kill %1
```

### TypeScript/JavaScript

```bash
# NestJS (script extraction)
npx tsx scripts/export-openapi.ts

# Hono
npx tsx scripts/export-openapi.ts
```

### Ruby/PHP

```bash
# Rails (rswag)
rails rswag:specs:swaggerize

# Laravel (l5-swagger)
php artisan l5-swagger:generate
```

## Post-Extraction Workflow

1. **Validate**: `speakeasy lint openapi -s openapi.json`
2. **Fix issues**: Use overlays or `speakeasy suggest operation-ids`
3. **Generate SDK**: `speakeasy quickstart -s openapi.json -t <language>`

## What NOT to Do

- **Do NOT** hand-write a spec when the framework can generate one
- **Do NOT** edit the extracted spec directly — use overlays
- **Do NOT** skip validation — extracted specs often have issues

## Related Skills

- `extract-openapi-fastapi` - FastAPI extraction
- `extract-openapi-django` - Django DRF extraction
- `extract-openapi-spring` - Spring Boot extraction
- `extract-openapi-nestjs` - NestJS extraction
- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
