---
short_description: "Generate MCP servers for AI assistant integration"
long_description: |
  Guide for generating Model Context Protocol (MCP) servers that allow AI
  assistants like Claude to interact with your API. The MCP server exposes
  API operations as tools that AI assistants can call directly.
source:
  repo: "opalsecurity/opal-mcp"
  path: "/"
  ref: "main"
  last_reconciled: "2025-12-11"
related:
  - "../sdk-languages/typescript.md"
  - "../spec-first/overlays.md"
---

# MCP Server Generation

Speakeasy TypeScript SDKs can generate a Model Context Protocol (MCP) server that enables AI assistants to interact with your API directly.

> **Agent Note**: Build a dedicated MCP server package using overlays to configure which endpoints are exposed as tools. See the [Overlay-Based Configuration](#overlay-based-configuration) section below.

## What is MCP?

The Model Context Protocol (MCP) is a standard for AI assistants to interact with external tools. When generating an MCP server, Speakeasy creates:

- A complete MCP server implementation
- One tool per API operation
- Scope-based access control
- A CLI entry point with multiple transports (stdio, SSE)
- Docker support for containerized deployment

## Quick Start: Dedicated MCP Package

The recommended pattern is creating a dedicated MCP package that wraps your API:

### 1. Create Workflow Configuration

```yaml
# .speakeasy/workflow.yaml
workflowVersion: 1.0.0
speakeasyVersion: latest
sources:
  My-API:
    inputs:
      - location: https://api.example.com/openapi.yaml
    overlays:
      - location: mcp-scopes-overlay.yaml
      - location: mcp-documentation-overlay.yaml
    output: openapi.yaml
targets:
  mcp-server:
    target: typescript
    source: My-API
    publish:
      npm:
        token: $npm_token
```

### 2. Create MCP Scopes Overlay

The `x-speakeasy-mcp` extension controls which operations become MCP tools:

```yaml
# mcp-scopes-overlay.yaml
openapi: 3.1.0
overlay: 1.0.0
info:
  title: Add MCP scopes
  version: 0.0.0
actions:
  # Enable read operations
  - target: $.paths.*["get","head"]
    update:
      x-speakeasy-mcp:
        scopes: [read]
        disabled: false

  # Enable write operations
  - target: $.paths.*["post","put","delete","patch"]
    update:
      x-speakeasy-mcp:
        scopes: [write]
        disabled: false

  # Disable specific sensitive endpoints
  - target: $.paths["/admin/danger-zone"]["delete"]
    update:
      x-speakeasy-mcp:
        disabled: true
```

### 3. Configure gen.yaml

```yaml
# .speakeasy/gen.yaml
configVersion: 2.0.0
generation:
  sdkClassName: MyApiMcp
  maintainOpenAPIOrder: true
  devContainers:
    enabled: true
    schemaPath: https://api.example.com/openapi.yaml
typescript:
  version: 1.0.0
  packageName: my-api-mcp
  enableMCPServer: true
  envVarPrefix: MYAPI
  baseErrorName: MyApiError
```

### 4. Generate the MCP Server

```bash
speakeasy run
```

---

## Overlay-Based Configuration

### The x-speakeasy-mcp Extension

Control MCP tool generation per-operation using the `x-speakeasy-mcp` OpenAPI extension:

```yaml
x-speakeasy-mcp:
  scopes: [read]      # Required scopes for this tool
  disabled: false     # Set to true to exclude from MCP
```

### Scope Patterns

Define scopes based on HTTP methods:

```yaml
# mcp-scopes-overlay.yaml
actions:
  # Read operations (GET, HEAD)
  - target: $.paths.*["get","head","query"]
    update:
      x-speakeasy-mcp:
        scopes: [read]
        disabled: false

  # Write operations (POST, PUT, DELETE, PATCH)
  - target: $.paths.*["post","put","delete","patch"]
    update:
      x-speakeasy-mcp:
        scopes: [write]
        disabled: false
```

### Disabling Specific Endpoints

Exclude sensitive or unnecessary endpoints:

```yaml
actions:
  # Disable admin endpoints
  - target: $.paths["/admin/*"].*
    update:
      x-speakeasy-mcp:
        disabled: true

  # Disable deprecated endpoints
  - target: $.paths["/v1/legacy/*"].*
    update:
      x-speakeasy-mcp:
        disabled: true
```

### Field Visibility Overlay

Hide irrelevant or sensitive fields from MCP tools:

```yaml
# mcp-field-visibility-overlay.yaml
openapi: 3.1.0
overlay: 1.0.0
info:
  title: Hide irrelevant fields
  version: 0.0.0
actions:
  - target: "#/components/schemas/User/properties/internalId"
    remove: true

  - target: "#/components/schemas/Request/properties/legacyField"
    remove: true
```

### Documentation Enhancement Overlay

Improve tool descriptions for AI understanding:

```yaml
# mcp-documentation-overlay.yaml
openapi: 3.1.0
overlay: 1.0.0
info:
  title: Enhance MCP documentation
  version: 0.0.0
actions:
  - target: $.paths["/users"].get
    update:
      description: |
        Retrieves a list of users. Use this to:
        - Find users by email or ID
        - List all users in an organization
        - Check user status and permissions

        Returns paginated results. Use cursor parameter for pagination.

  - target: $.components.schemas.UserStatus
    update:
      description: |
        User status values:
        - ACTIVE: User has full access
        - SUSPENDED: Temporarily restricted
        - DEPROVISIONED: Access removed
```

---

## Generated Components

| Component | Path | Purpose |
|-----------|------|---------|
| Server | `src/mcp-server/server.ts` | Main MCP server factory |
| Tools | `src/mcp-server/tools/` | One tool per API operation |
| CLI | `src/mcp-server/mcp-server.ts` | Command-line entry point |
| Scopes | `src/mcp-server/scopes.ts` | Permission scope definitions |
| Prompts | `src/mcp-server/prompts.ts` | AI prompt definitions |
| Resources | `src/mcp-server/resources.ts` | MCP resource handlers |

### Generated Tool Structure

Each API operation becomes an MCP tool:

```typescript
// src/mcp-server/tools/usersGetUsers.ts
import { usersGetUsers } from "../../funcs/usersGetUsers.js";
import * as operations from "../../models/operations/index.js";
import { formatResult, ToolDefinition } from "../tools.js";

const args = {
  request: operations.GetUsersRequest$inboundSchema,
};

export const tool$usersGetUsers: ToolDefinition<typeof args> = {
  name: "users-get-users",
  description: `Returns a list of users for your organization.`,
  scopes: ["read"],
  args,
  tool: async (client, args, ctx) => {
    const [result, apiCall] = await usersGetUsers(
      client,
      args.request,
      { fetchOptions: { signal: ctx.signal } },
    ).$inspect();

    if (!result.ok) {
      return {
        content: [{ type: "text", text: result.error.message }],
        isError: true,
      };
    }

    return formatResult(result.value.result, apiCall);
  },
};
```

---

## Using the MCP Server

### CLI Commands

The generated MCP server includes a full CLI:

```bash
# Show help
npx my-api-mcp mcp start --help

# Run with stdio transport (default)
npx my-api-mcp mcp start --bearer-auth "YOUR_TOKEN"

# Run with SSE transport on port 3000
npx my-api-mcp mcp start --transport sse --port 3000 --bearer-auth "YOUR_TOKEN"

# Filter by scope
npx my-api-mcp mcp start --scope read --bearer-auth "YOUR_TOKEN"

# Mount specific tools only
npx my-api-mcp mcp start --tool users-get-users --tool users-create-user --bearer-auth "YOUR_TOKEN"

# Set log level
npx my-api-mcp mcp start --log-level debug --bearer-auth "YOUR_TOKEN"
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--transport` | Transport type: `stdio` or `sse` | `stdio` |
| `--port` | Port for SSE transport | `2718` |
| `--bearer-auth` | API authentication token | Required |
| `--server-url` | Override API base URL | From spec |
| `--scope` | Filter by scope (repeatable) | All scopes |
| `--tool` | Mount specific tools (repeatable) | All tools |
| `--log-level` | Logging level | `info` |
| `--env` | Set environment variables | - |

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-api": {
      "command": "npx",
      "args": [
        "-y", "--package", "my-api-mcp",
        "--",
        "mcp", "start",
        "--bearer-auth", "<API_TOKEN>"
      ]
    }
  }
}
```

### Claude Code Configuration

Add to `.claude/settings.json` or use `claude mcp add`:

```json
{
  "mcpServers": {
    "my-api": {
      "command": "npx",
      "args": [
        "-y", "--package", "my-api-mcp",
        "--",
        "mcp", "start",
        "--bearer-auth", "<API_TOKEN>"
      ]
    }
  }
}
```

### Cursor Configuration

Create `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "my-api": {
      "command": "npx",
      "args": [
        "-y", "--package", "my-api-mcp",
        "--",
        "mcp", "start",
        "--bearer-auth", "<API_TOKEN>"
      ]
    }
  }
}
```

---

## Docker Deployment

### Dockerfile

Generated MCP servers include Docker support:

```dockerfile
FROM node:20-slim AS builder
WORKDIR /app

# Install Bun for building
RUN apt-get update && apt-get install -y curl unzip && \
    curl -fsSL https://bun.sh/install | bash && \
    ln -s $HOME/.bun/bin/bun /usr/local/bin/bun

COPY package*.json ./
RUN npm ci --ignore-scripts --omit-dev

COPY . .
RUN npm run build
RUN npm link

FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/bin ./bin
COPY --from=builder /app/node_modules ./node_modules

ENTRYPOINT node bin/mcp-server.js start \
  --transport sse \
  --port $PORT \
  --bearer-auth $BEARER_AUTH \
  --server-url $SERVER_URL \
  --log-level $LOG_LEVEL
```

### Docker Compose

```yaml
# docker-compose.yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "${PORT:-32000}:${PORT:-32000}"
    environment:
      - PORT=${PORT:-32000}
      - BEARER_AUTH=${BEARER_AUTH}
      - SERVER_URL=${SERVER_URL:-https://api.example.com}
      - LOG_LEVEL=${LOG_LEVEL:-info}
```

### Running with Docker

```bash
# Create .env file
cat > .env << EOF
BEARER_AUTH=your_api_key_here
PORT=32000
SERVER_URL=https://api.example.com
LOG_LEVEL=info
EOF

# Start the server
docker-compose up -d

# Configure MCP client for SSE
{
  "mcpServers": {
    "my-api": {
      "url": "http://localhost:32000/sse"
    }
  }
}
```

---

## Scope-Based Access Control

### Defining Scopes

Scopes are extracted from `x-speakeasy-mcp` extensions:

```typescript
// src/mcp-server/scopes.ts (generated)
export const mcpScopes = [
  "read",
  "write",
] as const;

export type MCPScope = (typeof mcpScopes)[number];
```

### Custom Scope Patterns

Define granular scopes per resource:

```yaml
# mcp-scopes-overlay.yaml
actions:
  # User read operations
  - target: $.paths["/users*"]["get"]
    update:
      x-speakeasy-mcp:
        scopes: [users:read]

  # User write operations
  - target: $.paths["/users*"]["post","put","delete","patch"]
    update:
      x-speakeasy-mcp:
        scopes: [users:write]

  # Resource operations
  - target: $.paths["/resources*"]["get"]
    update:
      x-speakeasy-mcp:
        scopes: [resources:read]
```

### Runtime Scope Filtering

```bash
# Allow only read operations
npx my-api-mcp mcp start --scope read --bearer-auth "$TOKEN"

# Allow users and resources read
npx my-api-mcp mcp start --scope users:read --scope resources:read --bearer-auth "$TOKEN"
```

---

## Dev Containers

Enable dev container generation for instant development environments:

```yaml
# gen.yaml
generation:
  devContainers:
    enabled: true
    schemaPath: https://api.example.com/openapi.yaml
```

This generates `.devcontainer/` configuration for VS Code and GitHub Codespaces.

---

## Result Formatting

The MCP server includes utilities for formatting API responses:

```typescript
// src/mcp-server/tools.ts
export async function formatResult(
  value: unknown,
  init: { response?: Response | undefined },
): Promise<CallToolResult> {
  const { response } = init;
  const contentType = response?.headers.get("content-type") ?? "";

  // JSON responses
  if (contentType.search(/\bjson\b/g)) {
    return { content: [{ type: "text", text: JSON.stringify(value) }] };
  }

  // SSE streams
  if (contentType.startsWith("text/event-stream") && isAsyncIterable(value)) {
    return { content: await consumeSSE(value) };
  }

  // Text responses
  if (contentType.startsWith("text/") && typeof value === "string") {
    return { content: [{ type: "text", text: value }] };
  }

  // Image responses
  if (isBinaryData(value) && contentType.startsWith("image/")) {
    const data = await valueToBase64(value);
    return { content: [{ type: "image", data, mimeType: contentType }] };
  }

  return {
    content: [{ type: "text", text: `Unsupported content type: "${contentType}"` }],
    isError: true,
  };
}
```

---

## Best Practices

1. **Use overlays for configuration**: Configure MCP behavior through overlays, not gen.yaml options
2. **Define clear scopes**: Use meaningful scope names that map to your authorization model
3. **Enhance descriptions**: Use documentation overlays to make tool descriptions AI-friendly
4. **Hide sensitive fields**: Remove internal IDs and sensitive data from MCP schemas
5. **Filter tools at runtime**: Use `--scope` and `--tool` flags to limit exposure
6. **Use environment variables**: Never hardcode tokens; pass via environment
7. **Deploy with Docker**: Use SSE transport for production deployments
8. **Enable dev containers**: Allow instant development environment setup

---

## Pre-defined TODO List

When creating an MCP server, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Create workflow.yaml with MCP overlays | Creating workflow.yaml |
| 2 | Create mcp-scopes-overlay.yaml | Creating scopes overlay |
| 3 | Create mcp-documentation-overlay.yaml | Creating documentation overlay |
| 4 | Create mcp-field-visibility-overlay.yaml | Creating field visibility overlay |
| 5 | Configure gen.yaml for MCP server | Configuring gen.yaml |
| 6 | Run speakeasy generate | Running speakeasy generate |
| 7 | Test MCP server locally with stdio | Testing MCP server locally |
| 8 | Configure Claude/Cursor integration | Configuring AI assistant integration |
| 9 | Set up Docker deployment (optional) | Setting up Docker deployment |
| 10 | Publish to npm | Publishing to npm |

**Usage:**
```
TodoWrite([
  {content: "Create workflow.yaml with MCP overlays", status: "pending", activeForm: "Creating workflow.yaml"},
  {content: "Create mcp-scopes-overlay.yaml", status: "pending", activeForm: "Creating scopes overlay"},
  {content: "Create mcp-documentation-overlay.yaml", status: "pending", activeForm: "Creating documentation overlay"},
  {content: "Create mcp-field-visibility-overlay.yaml", status: "pending", activeForm: "Creating field visibility overlay"},
  {content: "Configure gen.yaml for MCP server", status: "pending", activeForm: "Configuring gen.yaml"},
  {content: "Run speakeasy generate", status: "pending", activeForm: "Running speakeasy generate"},
  {content: "Test MCP server locally with stdio", status: "pending", activeForm: "Testing MCP server locally"},
  {content: "Configure Claude/Cursor integration", status: "pending", activeForm: "Configuring AI assistant integration"},
  {content: "Set up Docker deployment (optional)", status: "pending", activeForm: "Setting up Docker deployment"},
  {content: "Publish to npm", status: "pending", activeForm: "Publishing to npm"}
])
```

**Related documentation:**
- `../sdk-languages/typescript.md` - TypeScript SDK configuration
- `../spec-first/overlays.md` - OpenAPI overlay patterns
- `../plans/sdk-generation.md` - Full SDK generation workflow
