---
short_description: Extract OpenAPI from NestJS using @nestjs/swagger
long_description: NestJS provides native OpenAPI generation through @nestjs/swagger module. This guide covers setup, decorators, schema registration, and customization for SDK generation.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/nestjs.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# NestJS OpenAPI Extraction

NestJS has built-in OpenAPI support via `@nestjs/swagger` module.

## Installation

```bash
npm install --save @nestjs/swagger @scalar/nestjs-api-reference
```

## Basic Setup

**main.ts**:

```typescript
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { apiReference } from '@scalar/nestjs-api-reference';

const config = new DocumentBuilder()
  .setTitle('Pet API')
  .setDescription('Create a cat or dog record and view pets by id')
  .setVersion('1.0')
  .setContact(
    'Speakeasy support',
    'http://www.example.com/support',
    'support@example.com'
  )
  .setTermsOfService('http://example.com/terms/')
  .setLicense(
    'Apache 2.0',
    'https://www.apache.org/licenses/LICENSE-2.0.html'
  )
  .addServer('http://localhost:3000/', 'Development server')
  .addTag('Pets', 'Pets operations', {
    url: 'https://example.com/api',
    description: 'Operations API endpoint',
  })
  .addExtension('x-speakeasy-retries', {
    strategy: 'backoff',
    backoff: {
      initialInterval: 500,
      maxInterval: 60000,
      maxElapsedTime: 3600000,
      exponent: 1.5,
    },
    statusCodes: ['5XX'],
    retryConnectionErrors: true,
  })
  .build();

const document = SwaggerModule.createDocument(app, config);
SwaggerModule.setup('api', app, document, {
  swaggerUiEnabled: false,
});

app.use(
  '/api',
  apiReference({
    spec: {
      content: document,
    },
  })
);
```

## CLI Plugin for Auto-Documentation

**nest-cli.json**:

```json
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "compilerOptions": {
    "deleteOutDir": true,
    "plugins": [
      {
        "name": "@nestjs/swagger",
        "options": {
          "introspectComments": true
        }
      }
    ]
  }
}
```

This auto-generates `@ApiProperty()` decorators from TypeScript types and JSDoc comments.

## DTO with Comments

```typescript
export class Cat {
  /**
   * The type of pet
   * @example 'cat'
   */
  @IsEnum(['cat'])
  readonly type: 'cat';

  /**
   * The name of the cat
   * @example 'Panama'
   */
  @IsString()
  readonly name: string;

  /**
   * Age in years
   * @example 3
   */
  @IsNumber()
  readonly age: number;
}
```

## Controller with OpenAPI Decorators

```typescript
import {
  ApiOperation,
  ApiResponse,
  ApiBadRequestResponse,
  ApiBody,
  ApiOkResponse,
  ApiForbiddenResponse,
  ApiTags,
  ApiExtension,
  getSchemaPath,
} from '@nestjs/swagger';

@Controller('pets')
@ApiTags('Pets')
export class PetsController {
  @Get('cats/:id')
  @ApiOperation({ summary: 'Get cat' })
  @ApiResponse({
    description: 'The found record',
    type: Cat,
  })
  @ApiBadRequestResponse({ description: 'Bad Request' })
  findOneCat(@Param('id') id: string) {
    return this.petsService.findOneCat(id);
  }

  @Post()
  @ApiOperation({ summary: 'Create a pet' })
  @ApiBody({
    schema: {
      oneOf: [
        { $ref: getSchemaPath(Cat) },
        { $ref: getSchemaPath(Dog) }
      ],
      discriminator: {
        propertyName: 'type',
        mapping: {
          cat: getSchemaPath(Cat),
          dog: getSchemaPath(Dog),
        },
      },
    },
    description: 'Create a pet cat or dog',
  })
  @ApiOkResponse({
    schema: {
      oneOf: [
        { $ref: getSchemaPath(Cat) },
        { $ref: getSchemaPath(Dog) }
      ],
    },
  })
  @ApiForbiddenResponse({ description: 'Forbidden' })
  @ApiBadRequestResponse({ description: 'Bad Request' })
  create(@Body() createPetDto: CreatePetDto) {
    return this.petsService.create(createPetDto);
  }

  @Get()
  @ApiExtension('x-speakeasy-retries', {
    strategy: 'backoff',
    backoff: {
      initialInterval: 300,
      maxInterval: 40000,
      maxElapsedTime: 3000000,
      exponent: 1.2,
    },
    statusCodes: ['5XX'],
    retryConnectionErrors: true,
  })
  findAll() {
    return this.petsService.findAll();
  }
}
```

## Operation ID Customization

```typescript
const options: SwaggerDocumentOptions = {
  operationIdFactory: (controllerKey: string, methodKey: string) => methodKey,
};

const document = SwaggerModule.createDocument(app, config, options);
```

## Saving OpenAPI to File

```typescript
import * as yaml from 'js-yaml';
import { writeFileSync } from 'fs';

const yamlString = yaml.dump(document);
writeFileSync('openapi.yaml', yamlString);
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

- @nestjs/swagger: https://docs.nestjs.com/openapi/introduction
- NestJS: https://nestjs.com

---

## Pre-defined TODO List

When extracting OpenAPI from NestJS, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify NestJS application exists | Verifying NestJS application exists |
| 2 | Install @nestjs/swagger package | Installing @nestjs/swagger package |
| 3 | Configure Swagger in main.ts | Configuring Swagger in main.ts |
| 4 | Add decorators to DTOs (@ApiProperty) | Adding decorators to DTOs |
| 5 | Add decorators to controllers (@ApiTags, @ApiOperation) | Adding decorators to controllers |
| 6 | Start NestJS application | Starting NestJS application |
| 7 | Access OpenAPI spec at /api-json endpoint | Accessing OpenAPI spec endpoint |
| 8 | Validate spec with speakeasy validate | Validating spec with speakeasy validate |

**Usage:**
```
TodoWrite([
  {content: "Verify NestJS application exists", status: "pending", activeForm: "Verifying NestJS application exists"},
  {content: "Install @nestjs/swagger package", status: "pending", activeForm: "Installing @nestjs/swagger package"},
  {content: "Configure Swagger in main.ts", status: "pending", activeForm: "Configuring Swagger in main.ts"},
  {content: "Add decorators to DTOs (@ApiProperty)", status: "pending", activeForm: "Adding decorators to DTOs"},
  {content: "Add decorators to controllers (@ApiTags, @ApiOperation)", status: "pending", activeForm: "Adding decorators to controllers"},
  {content: "Start NestJS application", status: "pending", activeForm: "Starting NestJS application"},
  {content: "Access OpenAPI spec at /api-json endpoint", status: "pending", activeForm: "Accessing OpenAPI spec endpoint"},
  {content: "Validate spec with speakeasy validate", status: "pending", activeForm: "Validating spec with speakeasy validate"}
])
```

**Nested workflows:**
- For validation issues, see `spec-first/validation.md`
- For SDK generation after extraction, see `plans/sdk-generation.md`

