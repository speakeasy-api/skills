---
name: extract-openapi-hono
description: >-
  Use when extracting OpenAPI from Hono using @hono/zod-openapi.
  Triggers on "Hono OpenAPI", "zod-openapi", "Hono SDK", "Hono API spec".
license: Apache-2.0
---

# extract-openapi-hono

Extract an OpenAPI specification from Hono using @hono/zod-openapi.

## When to Use

- User has a Hono application with zod-openapi
- User wants to generate an SDK from Hono
- User says: "Hono OpenAPI", "zod-openapi", "Hono SDK"

## Installation

```bash
npm install @hono/zod-openapi zod
```

## Setup

```typescript
import { OpenAPIHono, createRoute, z } from '@hono/zod-openapi';

const app = new OpenAPIHono();

const route = createRoute({
  method: 'get',
  path: '/items',
  responses: {
    200: {
      content: {
        'application/json': {
          schema: z.array(z.object({ id: z.string(), name: z.string() }))
        }
      },
      description: 'List items'
    }
  }
});

app.openapi(route, (c) => {
  return c.json([{ id: '1', name: 'Item 1' }]);
});
```

## Extraction

```typescript
// scripts/export-openapi.ts
import { app } from '../src/app';
import * as fs from 'fs';

const doc = app.getOpenAPIDocument({
  openapi: '3.1.0',
  info: { title: 'My API', version: '1.0.0' }
});

fs.writeFileSync('openapi.json', JSON.stringify(doc, null, 2));
```

```bash
npx tsx scripts/export-openapi.ts
```

## Adding Speakeasy Extensions

Add extensions directly in route definitions:

```typescript
const route = createRoute({
  method: 'get',
  path: '/items',
  'x-speakeasy-group': 'items',
  'x-speakeasy-name-override': 'list',
  responses: { ... }
});
```

Or modify the document after generation:

```typescript
const doc = app.getOpenAPIDocument({ ... });
doc['x-speakeasy-retries'] = {
  strategy: 'backoff',
  statusCodes: ['5XX']
};
```

## Post-Extraction

```bash
speakeasy lint openapi -s openapi.json
speakeasy quickstart -s openapi.json -t typescript -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
