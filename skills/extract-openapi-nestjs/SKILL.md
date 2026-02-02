---
name: extract-openapi-nestjs
description: >-
  Use when extracting OpenAPI from NestJS using @nestjs/swagger.
  Covers setup, decorators, CLI plugin, and Speakeasy extensions.
  Triggers on "NestJS OpenAPI", "NestJS swagger", "NestJS SDK",
  "Nest API docs".
license: Apache-2.0
---

# extract-openapi-nestjs

Extract an OpenAPI specification from NestJS using @nestjs/swagger.

## When to Use

- User has a NestJS application
- User wants to generate an SDK from NestJS
- User says: "NestJS OpenAPI", "NestJS swagger", "NestJS SDK"

## Installation

```bash
npm install @nestjs/swagger swagger-ui-express
```

## Setup

**main.ts:**

```typescript
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('My API')
    .setVersion('1.0.0')
    .addServer('https://api.example.com', 'Production')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);

  await app.listen(3000);
}
bootstrap();
```

## Extraction

**Option 1: From running server**

```bash
npm run start &
sleep 10
curl http://localhost:3000/api-json -o openapi.json
kill %1
```

**Option 2: Script (no server)**

```typescript
// scripts/export-openapi.ts
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from '../src/app.module';
import * as fs from 'fs';

async function main() {
  const app = await NestFactory.create(AppModule, { logger: false });
  const config = new DocumentBuilder().setTitle('API').build();
  const doc = SwaggerModule.createDocument(app, config);
  fs.writeFileSync('openapi.json', JSON.stringify(doc, null, 2));
  await app.close();
}
main();
```

```bash
npx tsx scripts/export-openapi.ts
```

## Adding Speakeasy Extensions

Use `@ApiExtension` decorator:

```typescript
import { ApiExtension, ApiOperation } from '@nestjs/swagger';

@Controller('items')
export class ItemsController {
  @Get()
  @ApiOperation({ operationId: 'listItems' })
  @ApiExtension('x-speakeasy-group', 'items')
  @ApiExtension('x-speakeasy-name-override', 'list')
  @ApiExtension('x-speakeasy-retries', {
    strategy: 'backoff',
    statusCodes: ['5XX', '429']
  })
  findAll() { ... }
}
```

For global extensions, modify the document after creation:

```typescript
const document = SwaggerModule.createDocument(app, config);
document['x-speakeasy-retries'] = {
  strategy: 'backoff',
  backoff: { initialInterval: 500, maxInterval: 60000, exponent: 1.5 },
  statusCodes: ['5XX']
};
```

## CLI Plugin (Auto-documentation)

Enable in **nest-cli.json** to auto-generate from TypeScript types:

```json
{
  "compilerOptions": {
    "plugins": ["@nestjs/swagger"]
  }
}
```

## Post-Extraction

```bash
speakeasy lint openapi -s openapi.json
speakeasy quickstart -s openapi.json -t typescript -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
