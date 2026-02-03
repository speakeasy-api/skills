# NestJS OpenAPI Extraction

Detailed guide for extracting OpenAPI specs from NestJS applications using @nestjs/swagger.

## Installation

```bash
npm install @nestjs/swagger swagger-ui-express
```

## Setup

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('My API')
    .setDescription('API description with **markdown** support')
    .setVersion('1.0.0')
    .addServer('https://api.example.com', 'Production')
    .addServer('https://staging.example.com', 'Staging')
    .addBearerAuth()
    .addApiKey({ type: 'apiKey', name: 'X-API-Key', in: 'header' }, 'api-key')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);

  await app.listen(3000);
}
bootstrap();
```

## Extraction Methods

### Runtime Endpoint

```bash
# Start server
npm run start

# Fetch spec
curl http://localhost:3000/api-json > openapi.json
```

### Script-Based (No Server)

```typescript
// scripts/export-openapi.ts
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from '../src/app.module';
import * as fs from 'fs';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { logger: false });

  const config = new DocumentBuilder()
    .setTitle('My API')
    .setVersion('1.0.0')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  fs.writeFileSync('openapi.json', JSON.stringify(document, null, 2));

  await app.close();
  console.log('OpenAPI spec exported to openapi.json');
}
bootstrap();
```

```bash
npx ts-node scripts/export-openapi.ts
```

## Controller Documentation

### Basic Controller

```typescript
import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiParam, ApiQuery } from '@nestjs/swagger';

@ApiTags('burgers')
@Controller('burgers')
export class BurgersController {
  @Get()
  @ApiOperation({
    summary: 'List burgers',
    description: 'Returns a paginated list of all burgers',
    operationId: 'listBurgers'
  })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  @ApiQuery({ name: 'offset', required: false, type: Number })
  @ApiResponse({ status: 200, description: 'List of burgers', type: [BurgerDto] })
  findAll(@Query('limit') limit: number, @Query('offset') offset: number) {
    // ...
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get burger', operationId: 'getBurger' })
  @ApiParam({ name: 'id', description: 'Burger ID' })
  @ApiResponse({ status: 200, description: 'Burger found', type: BurgerDto })
  @ApiResponse({ status: 404, description: 'Burger not found' })
  findOne(@Param('id') id: string) {
    // ...
  }

  @Post()
  @ApiOperation({ summary: 'Create burger', operationId: 'createBurger' })
  @ApiResponse({ status: 201, description: 'Burger created', type: BurgerDto })
  @ApiResponse({ status: 400, description: 'Invalid input' })
  create(@Body() createBurgerDto: CreateBurgerDto) {
    // ...
  }
}
```

## DTOs with Validation

```typescript
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsString, IsNumber, IsOptional, Min, MaxLength } from 'class-validator';

export class CreateBurgerDto {
  @ApiProperty({
    description: 'Burger name',
    example: 'Classic Burger',
    maxLength: 100
  })
  @IsString()
  @MaxLength(100)
  name: string;

  @ApiProperty({
    description: 'Price in USD',
    example: 9.99,
    minimum: 0.01
  })
  @IsNumber()
  @Min(0.01)
  price: number;

  @ApiPropertyOptional({
    description: 'Burger description',
    example: 'A delicious classic burger'
  })
  @IsOptional()
  @IsString()
  description?: string;
}

export class BurgerDto extends CreateBurgerDto {
  @ApiProperty({ description: 'Unique identifier', example: '123' })
  id: string;

  @ApiProperty({ description: 'Creation timestamp' })
  createdAt: Date;
}
```

## Response Types

### Generic Response Wrapper

```typescript
import { ApiProperty } from '@nestjs/swagger';

export class PaginatedResponse<T> {
  @ApiProperty()
  data: T[];

  @ApiProperty()
  total: number;

  @ApiProperty()
  page: number;

  @ApiProperty()
  limit: number;
}

// Usage in controller
@ApiResponse({
  status: 200,
  description: 'Paginated burger list',
  schema: {
    allOf: [
      { $ref: getSchemaPath(PaginatedResponse) },
      {
        properties: {
          data: {
            type: 'array',
            items: { $ref: getSchemaPath(BurgerDto) }
          }
        }
      }
    ]
  }
})
```

### Extra Models

Register models not directly referenced:

```typescript
// main.ts
const document = SwaggerModule.createDocument(app, config, {
  extraModels: [PaginatedResponse, ErrorResponse, BurgerDto]
});
```

## Speakeasy Extensions

```typescript
import { ApiExtension } from '@nestjs/swagger';

@Get()
@ApiOperation({ summary: 'List burgers', operationId: 'listBurgers' })
@ApiExtension('x-speakeasy-group', 'burgers')
@ApiExtension('x-speakeasy-name-override', 'list')
@ApiExtension('x-speakeasy-retries', {
  strategy: 'backoff',
  backoff: {
    initialInterval: 500,
    maxInterval: 60000,
    exponent: 1.5
  },
  statusCodes: ['5XX', '429']
})
findAll() {
  // ...
}
```

### Pagination Extension

```typescript
@Get()
@ApiExtension('x-speakeasy-pagination', {
  type: 'offsetLimit',
  inputs: [
    { name: 'offset', in: 'parameters', type: 'offset' },
    { name: 'limit', in: 'parameters', type: 'limit' }
  ],
  outputs: {
    results: '$.data',
    numPages: '$.meta.totalPages'
  }
})
findAll(@Query('offset') offset: number, @Query('limit') limit: number) {
  // ...
}
```

## Authentication

```typescript
// main.ts
const config = new DocumentBuilder()
  .addBearerAuth(
    { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
    'bearer-auth'
  )
  .addApiKey(
    { type: 'apiKey', name: 'X-API-Key', in: 'header' },
    'api-key'
  )
  .build();

// controller.ts
import { ApiBearerAuth, ApiSecurity } from '@nestjs/swagger';

@ApiBearerAuth('bearer-auth')
@Controller('protected')
export class ProtectedController {
  // All routes require bearer auth
}

@ApiSecurity('api-key')
@Controller('api-protected')
export class ApiProtectedController {
  // All routes require API key
}
```

## Tags with Metadata

```typescript
// main.ts
const config = new DocumentBuilder()
  .addTag('burgers', 'Burger operations', {
    description: 'External docs',
    url: 'https://example.com/docs/burgers'
  })
  .addTag('orders', 'Order management')
  .build();
```

## File Upload

```typescript
import { ApiConsumes, ApiBody } from '@nestjs/swagger';

@Post('upload')
@ApiConsumes('multipart/form-data')
@ApiBody({
  schema: {
    type: 'object',
    properties: {
      file: {
        type: 'string',
        format: 'binary'
      }
    }
  }
})
uploadFile(@UploadedFile() file: Express.Multer.File) {
  // ...
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| DTOs not showing | Use `@ApiProperty()` on all properties |
| Circular dependencies | Use `forwardRef()` and lazy imports |
| Generic types not resolved | Register in `extraModels` |
| Missing operation IDs | Add `operationId` to `@ApiOperation()` |
