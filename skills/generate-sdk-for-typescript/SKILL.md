---
name: generate-sdk-for-typescript
description: >-
  Use when generating a TypeScript SDK with Speakeasy. Covers gen.yaml configuration,
  Zod validation, standalone functions, tree-shaking, custom code regions, JSR/npm publishing.
  Triggers on "TypeScript SDK", "generate TypeScript", "npm publish", "Zod validation",
  "standalone functions", "JSR publishing", "Deno SDK".
license: Apache-2.0
---

# Generate SDK for TypeScript

Configure and generate TypeScript SDKs with Speakeasy, featuring Zod validation, tree-shaking support, and multi-runtime compatibility (Node, Deno, Bun, browsers).

## When to Use

- Generating a new TypeScript SDK from an OpenAPI spec
- Configuring TypeScript-specific gen.yaml options
- Setting up standalone functions for tree-shaking
- Adding custom code regions or extra modules
- Publishing to npm or JSR (Deno)
- User says: "TypeScript SDK", "npm publish", "Zod", "standalone functions"

## Quick Start

```bash
speakeasy quickstart --skip-interactive --output console \
  -s openapi.yaml -t typescript -n "MySDK" -p "my-sdk"
```

## Essential gen.yaml Configuration

```yaml
typescript:
  version: 1.0.0
  packageName: "@myorg/my-sdk"
  author: "Your Name"

  # Module format
  moduleFormat: dual           # esm, commonjs, or dual

  # Method signatures
  maxMethodParams: 4
  flatteningOrder: parameters-first

  # Validation
  zodVersion: v4-mini          # v3, v4, or v4-mini

  # Error handling
  responseFormat: flat
  clientServerStatusCodesAsErrors: true
```

## Key Features

| Feature | Configuration |
|---------|--------------|
| Zod validation | Automatic - all models validated |
| Tree-shaking | `moduleFormat: dual` + standalone functions |
| Custom code | `enableCustomCodeRegions: true` |
| React Query | `enableReactQuery: true` |
| SSE streaming | Automatic for event-stream responses |

## Standalone Functions (Tree-Shaking)

Import only what you need for smaller bundles:

```typescript
import { TodoCore } from "my-sdk/core.js";
import { todosCreate } from "my-sdk/funcs/todosCreate.js";

const sdk = new TodoCore({ apiKey: "..." });
const res = await todosCreate(sdk, { title: "New todo" });

if (res.ok) {
  console.log(res.value);
}
```

## Custom Code Regions

Enable with `enableCustomCodeRegions: true`:

```typescript
// src/sdk/chat.ts
// #region imports
import { customHelper } from "../extra/helpers.js";
// #endregion imports

export class Chat extends ClientSDK {
    // #region sdk-class-body
    async customMethod(request: CustomRequest): Promise<CustomResponse> {
        return this.generatedMethod(customHelper(request));
    }
    // #endregion sdk-class-body
}
```

## Extra Modules Pattern

For complex custom logic, use `src/extra/`:

```
src/
├── extra/
│   ├── index.ts          # Public exports
│   ├── structuredOutput.ts
│   └── helpers.ts
├── hooks/
└── sdk/
```

## JSR (Deno) Publishing

Create `jsr.json`:
```json
{
  "name": "@myorg/my-sdk",
  "version": "1.0.0",
  "exports": {
    ".": "./src/index.ts"
  }
}
```

Publish: `deno publish`

## Common Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `zodVersion` | v4-mini | Zod version for validation |
| `moduleFormat` | dual | esm, commonjs, or dual |
| `enumFormat` | union | `enum` or `union` types |
| `useIndexModules` | true | Generate barrel files |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ResponseValidationError` | API response doesn't match spec |
| Bundle too large | Use standalone functions |
| Type mismatch at runtime | Check Zod validation errors |

## Related Skills

- `start-new-sdk-project` - Initial SDK setup
- `customize-sdk-hooks` - Hook implementation
- `setup-sdk-testing` - Testing patterns
