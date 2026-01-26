---
short_description: Extract OpenAPI from Hono using Zod OpenAPI middleware
long_description: Hono uses @hono/zod-openapi middleware for type-safe OpenAPI generation with Zod schemas. This guide covers route definition, schema registration, and OpenAPI customization.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/hono.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Hono OpenAPI Extraction

Hono uses `@hono/zod-openapi` middleware for OpenAPI generation with Zod validation.

## Installation

```bash
npm i zod @hono/zod-openapi @scalar/hono-api-reference js-yaml
```

## Schema Definition

**schemas.ts**:

```typescript
import { z } from "@hono/zod-openapi";

export const UserSelectSchema = z
  .object({
    id: z.string().openapi({ example: "123" }),
    name: z.string().openapi({ example: "John Doe" }),
    age: z.number().openapi({ example: 42 }),
  })
  .openapi("UserSelect");

export const UserInsertSchema = z
  .object({
    name: z.string().openapi({ example: "John Doe" }),
    age: z.number().openapi({ example: 42 }),
  })
  .openapi("UserInsert");

export const idParamsSchema = z.object({
  id: z.string().min(3).openapi({
    param: {
      name: "id",
      in: "path",
    },
    example: "423",
  }),
});
```

## App Setup

**createApp.ts**:

```typescript
import { OpenAPIHono } from "@hono/zod-openapi";

export function createApp() {
  return new OpenAPIHono({ strict: false });
}
```

## Route Definition

**users.routes.ts**:

```typescript
import { createRoute } from "@hono/zod-openapi";

export const list = createRoute({
  operationId: 'getUsers',
  path: "/users",
  method: "get",
  tags: ['Users'],
  'x-speakeasy-retries': {
    strategy: 'backoff',
    backoff: {
      initialInterval: 300,
      maxInterval: 40000,
      maxElapsedTime: 3000000,
      exponent: 1.2,
    },
    statusCodes: ['5XX'],
    retryConnectionErrors: true,
  },
  responses: {
    200: {
      content: {
        "application/json": {
          schema: z.array(UserSelectSchema),
        },
      },
      description: "The list of users",
    },
  },
});

export const create = createRoute({
  operationId: 'createUser',
  path: "/users",
  method: "post",
  tags: ['Users'],
  request: {
    body: {
      content: {
        "application/json": {
          schema: UserInsertSchema,
        },
      },
      description: "The user to create",
      required: true,
    },
  },
  responses: {
    201: {
      content: {
        "application/json": {
          schema: UserSelectSchema,
        },
      },
      description: "The created user",
    },
    422: {
      content: {
        "application/json": {
          schema: createErrorSchema(UserInsertSchema),
        },
      },
      description: "Validation error",
    },
  },
});
```

## Route Handlers

**users.handlers.ts**:

```typescript
import type { AppRouteHandler } from "@/lib/types";

export const list: AppRouteHandler<ListRoute> = async (c) => {
  return c.json([
    { age: 42, id: "123", name: "John Doe" },
    { age: 32, id: "124", name: "Sarah Jones" },
  ], 200);
};

export const create: AppRouteHandler<CreateRoute> = async (c) => {
  const user = c.req.valid("json");
  return c.json({
    id: "2342",
    age: user.age,
    name: user.name,
  }, 201);
};
```

## Router Registration

**users.index.ts**:

```typescript
import { createRouter } from "@/lib/createApp";
import * as handlers from "./users.handlers";
import * as routes from "./users.routes";

const router = createRouter()
  .openapi(routes.list, handlers.list)
  .openapi(routes.create, handlers.create)
  .openapi(routes.getOne, handlers.getOne);

export default router;
```

## OpenAPI Configuration

**configureOpenAPI.ts**:

```typescript
import type { OpenAPIHono } from "@hono/zod-openapi";
import { Scalar } from "@scalar/hono-api-reference";
import packageJson from "../../package.json";

export const openAPIObjectConfig = {
  openapi: '3.1.0',
  externalDocs: {
    description: 'Find out more about Users API',
    url: 'https://www.example.com',
  },
  info: {
    version: packageJson.version,
    title: 'Users API',
  },
  servers: [
    {
      url: 'http://localhost:3000/',
      description: 'Development server',
    },
  ],
  tags: [{
    name: 'Users',
    description: 'Users operations',
    externalDocs: {
      description: 'Find more info here',
      url: 'https://example.com',
    },
  }],
  'x-speakeasy-retries': {
    strategy: 'backoff',
    backoff: {
      initialInterval: 500,
      maxInterval: 60000,
      maxElapsedTime: 3600000,
      exponent: 1.5,
    },
    statusCodes: ['5XX'],
    retryConnectionErrors: true,
  },
};

export default function configureOpenAPI(app: OpenAPIHono) {
  app.doc31("/doc", openAPIObjectConfig);
  app.get(
    "/ui",
    Scalar({
      url: "/doc",
      pageTitle: "Users Management API",
    })
  );
}
```

## Generating OpenAPI File

**generateOpenAPIYamlFile.ts**:

```typescript
import { writeFileSync } from "node:fs";
import * as yaml from "js-yaml";
import configureOpenAPI, { openAPIObjectConfig } from "./lib/configureOpenAPI";
import createApp from "./lib/createApp";
import users from "@/routes/users/users.index";

const app = createApp();
const routes = [users] as const;

configureOpenAPI(app);
routes.forEach((route) => {
  app.route("/", route);
});

const yamlString = yaml.dump(app.getOpenAPI31Document(openAPIObjectConfig));
writeFileSync("openapi.yaml", yamlString);
```

**package.json**:

```json
{
  "scripts": {
    "create:openapi": "npx tsx ./src/generateOpenAPIYamlFile.ts"
  }
}
```

```bash
npm run create:openapi
```

## Validation

```bash
speakeasy lint openapi --schema ./openapi.yaml
```

## SDK Generation

```bash
speakeasy quickstart --schema openapi.yaml --target typescript --out-dir ./sdk
```

## Reference

- @hono/zod-openapi: https://hono.dev/examples/zod-openapi
- Hono: https://hono.dev
- Zod: https://zod.dev

---

## Pre-defined TODO List

When extracting OpenAPI from Hono, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Hono application exists | Verifying Hono application exists |
| 2 | Install @hono/zod-openapi package | Installing @hono/zod-openapi package |
| 3 | Replace Hono() with OpenAPIHono() | Replacing Hono with OpenAPIHono |
| 4 | Define Zod schemas for request/response | Defining Zod schemas |
| 5 | Create routes with openapi() method | Creating routes with openapi method |
| 6 | Add OpenAPI documentation endpoint | Adding OpenAPI documentation endpoint |
| 7 | Generate OpenAPI document | Generating OpenAPI document |
| 8 | Validate spec with speakeasy validate | Validating spec with speakeasy validate |

**Usage:**
```
TodoWrite([
  {content: "Verify Hono application exists", status: "pending", activeForm: "Verifying Hono application exists"},
  {content: "Install @hono/zod-openapi package", status: "pending", activeForm: "Installing @hono/zod-openapi package"},
  {content: "Replace Hono() with OpenAPIHono()", status: "pending", activeForm: "Replacing Hono with OpenAPIHono"},
  {content: "Define Zod schemas for request/response", status: "pending", activeForm: "Defining Zod schemas"},
  {content: "Create routes with openapi() method", status: "pending", activeForm: "Creating routes with openapi method"},
  {content: "Add OpenAPI documentation endpoint", status: "pending", activeForm: "Adding OpenAPI documentation endpoint"},
  {content: "Generate OpenAPI document", status: "pending", activeForm: "Generating OpenAPI document"},
  {content: "Validate spec with speakeasy validate", status: "pending", activeForm: "Validating spec with speakeasy validate"}
])
```

**Nested workflows:**
- For validation issues, see `spec-first/validation.md`
- For SDK generation after extraction, see `plans/sdk-generation.md`

