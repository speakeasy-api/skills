# Hono OpenAPI Extraction

Detailed guide for extracting OpenAPI specs from Hono applications using @hono/zod-openapi.

## Installation

```bash
npm install hono @hono/zod-openapi zod
```

## Setup

```typescript
import { OpenAPIHono } from '@hono/zod-openapi';

const app = new OpenAPIHono();

// Configure OpenAPI document
app.doc('/openapi.json', {
  openapi: '3.0.0',
  info: {
    title: 'My API',
    version: '1.0.0',
    description: 'API description with **markdown** support'
  },
  servers: [
    { url: 'https://api.example.com', description: 'Production' },
    { url: 'https://staging.example.com', description: 'Staging' }
  ]
});
```

## Extraction

### Runtime Endpoint

```bash
# Start server
npm run dev

# Fetch spec
curl http://localhost:3000/openapi.json > openapi.json
```

### Script-Based (No Server)

```typescript
// extract-openapi.ts
import { app } from './app';

const spec = app.getOpenAPIDocument({
  openapi: '3.0.0',
  info: { title: 'My API', version: '1.0.0' }
});

await Bun.write('openapi.json', JSON.stringify(spec, null, 2));
// Or with Node.js
// fs.writeFileSync('openapi.json', JSON.stringify(spec, null, 2));
```

## Route Documentation

### Schema Definitions

```typescript
import { z } from 'zod';
import { createRoute, OpenAPIHono } from '@hono/zod-openapi';

// Path parameters
const BurgerIdParam = z.object({
  id: z.string().openapi({
    param: { name: 'id', in: 'path' },
    description: 'Burger ID',
    example: '123'
  })
});

// Query parameters
const ListBurgersQuery = z.object({
  limit: z.coerce.number().int().min(1).max(100).default(20).openapi({
    param: { name: 'limit', in: 'query' },
    description: 'Page size'
  }),
  offset: z.coerce.number().int().min(0).default(0).openapi({
    param: { name: 'offset', in: 'query' },
    description: 'Page offset'
  })
});

// Response schemas
const BurgerSchema = z.object({
  id: z.string().openapi({ description: 'Unique identifier', example: '123' }),
  name: z.string().max(100).openapi({ description: 'Burger name', example: 'Classic Burger' }),
  price: z.number().positive().openapi({ description: 'Price in USD', example: 9.99 }),
  description: z.string().nullable().openapi({ description: 'Optional description' })
}).openapi('Burger');

const BurgersListSchema = z.array(BurgerSchema).openapi('BurgersList');

// Request body schema
const CreateBurgerSchema = z.object({
  name: z.string().min(1).max(100).openapi({ description: 'Burger name', example: 'Classic Burger' }),
  price: z.number().positive().openapi({ description: 'Price in USD', example: 9.99 }),
  description: z.string().optional().openapi({ description: 'Optional description' })
}).openapi('CreateBurger');

// Error schema
const ErrorSchema = z.object({
  message: z.string().openapi({ description: 'Error message' }),
  code: z.string().openapi({ description: 'Error code' })
}).openapi('Error');
```

### Route Definitions

```typescript
const app = new OpenAPIHono();

// List burgers
const listBurgersRoute = createRoute({
  method: 'get',
  path: '/burgers',
  operationId: 'listBurgers',
  tags: ['burgers'],
  summary: 'List burgers',
  description: 'Returns a paginated list of all burgers',
  request: {
    query: ListBurgersQuery
  },
  responses: {
    200: {
      description: 'List of burgers',
      content: {
        'application/json': {
          schema: BurgersListSchema
        }
      }
    }
  }
});

app.openapi(listBurgersRoute, async (c) => {
  const { limit, offset } = c.req.valid('query');
  // Implementation
  return c.json([]);
});

// Get burger by ID
const getBurgerRoute = createRoute({
  method: 'get',
  path: '/burgers/{id}',
  operationId: 'getBurger',
  tags: ['burgers'],
  summary: 'Get burger',
  description: 'Returns a single burger by ID',
  request: {
    params: BurgerIdParam
  },
  responses: {
    200: {
      description: 'Burger found',
      content: {
        'application/json': {
          schema: BurgerSchema
        }
      }
    },
    404: {
      description: 'Burger not found',
      content: {
        'application/json': {
          schema: ErrorSchema
        }
      }
    }
  }
});

app.openapi(getBurgerRoute, async (c) => {
  const { id } = c.req.valid('param');
  // Implementation
  return c.json({ id, name: 'Burger', price: 9.99, description: null });
});

// Create burger
const createBurgerRoute = createRoute({
  method: 'post',
  path: '/burgers',
  operationId: 'createBurger',
  tags: ['burgers'],
  summary: 'Create burger',
  request: {
    body: {
      content: {
        'application/json': {
          schema: CreateBurgerSchema
        }
      }
    }
  },
  responses: {
    201: {
      description: 'Burger created',
      content: {
        'application/json': {
          schema: BurgerSchema
        }
      }
    },
    400: {
      description: 'Invalid input',
      content: {
        'application/json': {
          schema: ErrorSchema
        }
      }
    }
  }
});

app.openapi(createBurgerRoute, async (c) => {
  const body = c.req.valid('json');
  // Implementation
  return c.json({ id: '123', ...body, description: body.description ?? null }, 201);
});
```

## Speakeasy Extensions

### Per-Route Extensions

```typescript
const listBurgersRoute = createRoute({
  method: 'get',
  path: '/burgers',
  operationId: 'listBurgers',
  tags: ['burgers'],
  // Speakeasy extensions
  'x-speakeasy-group': 'burgers',
  'x-speakeasy-name-override': 'list',
  'x-speakeasy-retries': {
    strategy: 'backoff',
    backoff: {
      initialInterval: 500,
      maxInterval: 60000,
      exponent: 1.5
    },
    statusCodes: ['5XX', '429']
  },
  request: { query: ListBurgersQuery },
  responses: { /* ... */ }
});
```

### Pagination Extension

```typescript
const listBurgersRoute = createRoute({
  method: 'get',
  path: '/burgers',
  operationId: 'listBurgers',
  'x-speakeasy-pagination': {
    type: 'offsetLimit',
    inputs: [
      { name: 'offset', in: 'parameters', type: 'offset' },
      { name: 'limit', in: 'parameters', type: 'limit' }
    ],
    outputs: {
      results: '$.data',
      numPages: '$.meta.totalPages'
    }
  },
  // ...
});
```

### Global Extensions

```typescript
app.doc('/openapi.json', (c) => ({
  openapi: '3.0.0',
  info: { title: 'My API', version: '1.0.0' },
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
}));
```

## Authentication

### Security Schemes

```typescript
const app = new OpenAPIHono();

// Register security schemes
app.openAPIRegistry.registerComponent('securitySchemes', 'bearer-auth', {
  type: 'http',
  scheme: 'bearer',
  bearerFormat: 'JWT'
});

app.openAPIRegistry.registerComponent('securitySchemes', 'api-key', {
  type: 'apiKey',
  in: 'header',
  name: 'X-API-Key'
});

// Protected route
const protectedRoute = createRoute({
  method: 'get',
  path: '/protected',
  security: [{ 'bearer-auth': [] }],
  responses: {
    200: { description: 'Success' }
  }
});

// Public route (no auth)
const publicRoute = createRoute({
  method: 'get',
  path: '/public',
  security: [],  // Explicitly no auth
  responses: {
    200: { description: 'Success' }
  }
});
```

### Auth Middleware Integration

```typescript
import { bearerAuth } from 'hono/bearer-auth';

// Apply middleware
app.use('/protected/*', bearerAuth({ token: 'secret' }));

// Document in route
const protectedRoute = createRoute({
  method: 'get',
  path: '/protected/resource',
  security: [{ 'bearer-auth': [] }],
  // ...
});
```

## Tags

```typescript
app.doc('/openapi.json', {
  openapi: '3.0.0',
  info: { title: 'My API', version: '1.0.0' },
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
});
```

## File Upload

```typescript
const uploadRoute = createRoute({
  method: 'post',
  path: '/upload',
  operationId: 'uploadFile',
  tags: ['files'],
  request: {
    body: {
      content: {
        'multipart/form-data': {
          schema: z.object({
            file: z.instanceof(File).openapi({
              type: 'string',
              format: 'binary',
              description: 'File to upload'
            })
          })
        }
      }
    }
  },
  responses: {
    200: {
      description: 'File uploaded',
      content: {
        'application/json': {
          schema: z.object({
            url: z.string().url()
          })
        }
      }
    }
  }
});
```

## Webhooks

```typescript
// Register webhook
app.openAPIRegistry.registerWebhook({
  method: 'post',
  path: 'order-status-changed',
  operationId: 'onOrderStatusChanged',
  description: 'Triggered when an order status changes',
  requestBody: {
    content: {
      'application/json': {
        schema: z.object({
          orderId: z.string(),
          status: z.enum(['pending', 'processing', 'shipped', 'delivered']),
          timestamp: z.string().datetime()
        })
      }
    }
  },
  responses: {
    200: { description: 'Webhook received' }
  }
});
```

## Grouped Routes

```typescript
// Create a group router
const burgersRouter = new OpenAPIHono();

// Define routes on the group
burgersRouter.openapi(listBurgersRoute, handler);
burgersRouter.openapi(getBurgerRoute, handler);
burgersRouter.openapi(createBurgerRoute, handler);

// Mount on main app
app.route('/api/v1', burgersRouter);
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Type errors with extensions | Use type assertion: `'x-speakeasy-group' as any` |
| Schema not in components | Call `.openapi('SchemaName')` on Zod schemas |
| Path params not validated | Ensure `{param}` syntax matches schema key |
| Missing operation IDs | Add `operationId` to every route |
| Coercion issues | Use `z.coerce.number()` for query params |
