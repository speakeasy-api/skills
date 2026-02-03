# TypeScript SDK Configuration

Detailed gen.yaml configuration options for TypeScript SDKs.

## gen.yaml Configuration

```yaml
typescript:
  version: 1.0.0
  packageName: "@myorg/my-sdk"

  # Module format
  moduleFormat: dual              # esm, commonjs, or dual (recommended)

  # Validation
  zodVersion: v4-mini             # v3, v4, or v4-mini (smallest bundle)

  # Code regions
  enableCustomCodeRegions: true   # Preserve custom code on regeneration

  # React Query
  enableReactQuery: true          # Generate React Query hooks

  # MCP Server
  enableMCPServer: false          # Generate MCP server for AI assistants

  # Method signatures
  maxMethodParams: 4              # Params before object wrapper
  flatteningOrder: parameters-first
```

## Package Structure

```
src/
├── index.ts          # Main exports
├── sdk.ts            # SDK class
├── lib/
│   ├── http.ts       # HTTP client
│   └── sdks.ts       # Internal SDK logic
├── hooks/            # Custom hooks (preserved)
│   └── registration.ts
├── funcs/            # Standalone functions
│   └── usersCreate.js
└── models/
    ├── operations/   # Request/response types
    ├── shared/       # Shared schemas
    └── errors/       # Error types
```

## Module Format Options

| Format | Output | Use Case |
|--------|--------|----------|
| `esm` | ES Modules only | Modern bundlers, Node 18+ |
| `commonjs` | CommonJS only | Legacy Node.js, older tools |
| `dual` | Both formats | Maximum compatibility (recommended) |

### Dual Format Publishing

```json
// package.json (auto-generated)
{
  "exports": {
    ".": {
      "import": "./esm/index.js",
      "require": "./commonjs/index.js"
    }
  }
}
```

## Zod Validation Options

| Version | Size | Features |
|---------|------|----------|
| `v3` | Largest | Full Zod v3 |
| `v4` | Medium | Full Zod v4 |
| `v4-mini` | Smallest | Minimal Zod subset (recommended for tree-shaking) |

Validation runs on:
- User input to SDK methods
- Server responses (strict mode)

```typescript
// Error when server returns unexpected data
try {
  const user = await sdk.users.get("123");
} catch (e) {
  if (e instanceof ResponseValidationError) {
    console.error("Server response doesn't match schema:", e.rawValue);
  }
}
```

## Standalone Functions (Tree-Shaking)

For minimal bundle size, import standalone functions instead of the full SDK:

```typescript
// Full SDK - includes everything
import { MySDK } from "my-sdk";
const sdk = new MySDK({ apiKey: "..." });
const user = await sdk.users.create({ name: "Alice" });

// Standalone function - minimal bundle
import { MySDKCore } from "my-sdk/core.js";
import { usersCreate } from "my-sdk/funcs/usersCreate.js";
const sdk = new MySDKCore({ apiKey: "..." });
const user = await usersCreate(sdk, { name: "Alice" });
```

Bundle size comparison:
- Full SDK: ~150KB (varies)
- Standalone function: ~15KB per function

## React Query Integration

Enable with `enableReactQuery: true`:

```typescript
import { useUsersGet, useUsersCreate } from "my-sdk/react-query";

function UserProfile({ id }: { id: string }) {
  const { data: user, isLoading } = useUsersGet({ id });
  const createUser = useUsersCreate();

  if (isLoading) return <Loading />;
  return <div>{user.name}</div>;
}
```

Generated hooks follow React Query patterns:
- `useXGet()` - queries
- `useXCreate()` - mutations
- Automatic cache key management
- Optimistic updates support

## Custom Code Regions

Enable with `enableCustomCodeRegions: true`. Code between markers is preserved:

```typescript
// src/sdk.ts
export class MySDK {
  // speakeasy:custom-code-start
  customMethod() {
    return "preserved across regeneration";
  }
  // speakeasy:custom-end
}
```

Preserved locations:
- `src/hooks/*.ts` - All hook files
- `src/sdk.ts` - SDK class extensions
- `src/lib/config.ts` - Configuration helpers

## Additional Dependencies

Add runtime dependencies via gen.yaml:

```yaml
typescript:
  additionalDependencies:
    dependencies:
      crypto-js: "^4.1.1"
      uuid: "^9.0.0"
    devDependencies:
      "@types/uuid": "^9.0.0"
```

Use in hooks:

```typescript
// src/hooks/registration.ts
import CryptoJS from "crypto-js";
import { v4 as uuidv4 } from "uuid";

export function initHooks(hooks: Hooks) {
  hooks.beforeRequest((req) => {
    req.headers.set("X-Request-ID", uuidv4());
    return req;
  });
}
```

## Publishing Options

### npm

```bash
npm publish
# or for scoped packages
npm publish --access public
```

### JSR (Deno)

Create `jsr.json`:
```json
{
  "name": "@myorg/my-sdk",
  "version": "1.0.0",
  "exports": "./src/index.ts"
}
```

```bash
deno publish
```

## Runtime Configuration

```typescript
const sdk = new MySDK({
  // Authentication
  apiKey: process.env.API_KEY,

  // Server selection
  server: "production",              // or use serverURL
  serverURL: "https://api.example.com",

  // Timeouts
  timeoutMs: 30000,                  // Global timeout

  // Retries (override spec defaults)
  retryConfig: {
    strategy: "backoff",
    backoff: {
      initialInterval: 500,
      maxInterval: 60000,
      exponent: 1.5,
      maxElapsedTime: 300000,
    },
  },
});

// Per-call overrides
const result = await sdk.users.create(data, {
  timeoutMs: 60000,                  // This call only
  retries: { strategy: "none" },     // Disable retries
});
```

## Error Handling

```typescript
import { SDKError, APIError, ResponseValidationError } from "my-sdk/models/errors";

try {
  const result = await sdk.users.create(data);
} catch (e) {
  if (e instanceof APIError) {
    // Server returned error status
    console.error(e.statusCode, e.body);
  } else if (e instanceof ResponseValidationError) {
    // Response doesn't match schema
    console.error("Schema mismatch:", e.rawValue);
  } else if (e instanceof SDKError) {
    // Other SDK error (network, timeout)
    console.error(e.message);
  }
}
```

## Streaming Responses

For SSE endpoints:

```typescript
const stream = await sdk.chat.complete({ message: "Hello" });

for await (const event of stream) {
  console.log(event.content);
}
```

## Debugging

```typescript
const sdk = new MySDK({
  debugLogger: console,  // Log all requests/responses
});
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Bundle too large | Use standalone functions, set `zodVersion: v4-mini` |
| CJS/ESM conflicts | Set `moduleFormat: dual` |
| Type errors in strict mode | Ensure spec schemas match server responses |
| React Query not generating | Set `enableReactQuery: true` in gen.yaml |
