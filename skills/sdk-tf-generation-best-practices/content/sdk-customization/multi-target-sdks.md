---
short_description: Generate multiple SDK variants from one repository
long_description: |
  Guide for generating multiple SDK packages (e.g., core, Azure, GCP variants)
  from a single repository using Speakeasy's workflow.yaml multi-target feature.
  Covers workflow configuration, repository structure, and CI patterns.
source:
  repo: "mistralai/client-ts"
  path: ".speakeasy/workflow.yaml"
  ref: "main"
  last_reconciled: "2025-12-11"
related:
  - "../plans/sdk-generation.md"
  - "../sdk-languages/typescript.md"
  - "./hooks.md"
---

# Multi-Target SDK Generation

Generate multiple SDK variants from different OpenAPI sources in a single repository. This pattern is useful for cloud-specific variants, regional APIs, or partner-branded SDKs.

## Use Cases

- **Cloud-specific variants**: Core SDK + Azure SDK + GCP SDK
- **Tenant-specific SDKs**: Different OpenAPI specs per customer
- **Regional API variants**: US, EU, APAC endpoints with different schemas
- **Partner-branded SDKs**: White-label SDKs with different branding

## Workflow Configuration

### Basic Multi-Target workflow.yaml

```yaml
workflowVersion: 1.0.0
speakeasyVersion: latest

sources:
    # Main API source
    main-source:
        inputs:
            - location: registry.speakeasyapi.dev/org/repo/main-openapi:main

    # Azure-specific API source
    azure-source:
        inputs:
            - location: registry.speakeasyapi.dev/org/repo/azure-openapi:main

    # GCP-specific API source
    gcp-source:
        inputs:
            - location: registry.speakeasyapi.dev/org/repo/gcp-openapi:main

targets:
    # Main SDK - outputs to repository root
    main-sdk:
        target: typescript
        source: main-source
        output: ./
        publish:
            npm:
                token: $npm_token
        codeSamples:
            registry:
                location: registry.speakeasyapi.dev/org/repo/main-code-samples
            blocking: false

    # Azure variant - outputs to packages subdirectory
    azure-sdk:
        target: typescript
        source: azure-source
        output: ./packages/azure
        publish:
            npm:
                token: $npm_token
        codeSamples:
            registry:
                location: registry.speakeasyapi.dev/org/repo/azure-code-samples
            blocking: false

    # GCP variant - outputs to packages subdirectory
    gcp-sdk:
        target: typescript
        source: gcp-source
        output: ./packages/gcp
        publish:
            npm:
                token: $npm_token
        codeSamples:
            registry:
                location: registry.speakeasyapi.dev/org/repo/gcp-code-samples
            blocking: false
```

### Key Configuration Fields

| Field | Description |
|-------|-------------|
| `sources.<name>.inputs.location` | OpenAPI spec location (registry, URL, or local path) |
| `targets.<name>.source` | Reference to source definition |
| `targets.<name>.output` | Output directory for generated SDK |
| `targets.<name>.publish` | Publishing configuration per target |
| `targets.<name>.codeSamples` | Code samples registry location |

## Repository Structure

### Recommended Layout

```
my-multi-sdk/
├── .speakeasy/
│   ├── workflow.yaml          # Multi-target workflow config
│   ├── workflow.lock          # Workflow lock file
│   ├── gen.yaml               # Main SDK generation config
│   └── gen.lock               # Generation lock file
├── src/                       # Main SDK source
│   ├── sdk/
│   ├── models/
│   ├── hooks/                 # Shared hooks (if applicable)
│   └── extra/                 # Shared custom code
├── packages/
│   ├── azure/                 # Azure variant
│   │   ├── .speakeasy/
│   │   │   └── gen.yaml       # Azure-specific config
│   │   ├── src/
│   │   └── package.json
│   └── gcp/                   # GCP variant
│       ├── .speakeasy/
│       │   └── gen.yaml       # GCP-specific config
│       ├── src/
│       └── package.json
├── examples/                  # Examples (can cover all variants)
├── tests/                     # Tests for custom code
├── .github/workflows/
│   ├── sdk_generation_main.yaml
│   ├── sdk_generation_azure.yaml
│   ├── sdk_generation_gcp.yaml
│   ├── sdk_publish_main.yaml
│   ├── sdk_publish_azure.yaml
│   └── sdk_publish_gcp.yaml
├── package.json               # Main SDK package
└── README.md
```

### Per-Target gen.yaml Configuration

Each target can have its own `gen.yaml` with variant-specific settings:

```yaml
# packages/azure/.speakeasy/gen.yaml
configVersion: 2.0.0
generation:
  sdkClassName: MySDKAzure
typescript:
  version: 1.0.0
  packageName: '@myorg/mysdk-azure'
  author: MyOrg
  envVarPrefix: MYSDK_AZURE
```

## CI/CD Workflows

### Generation Workflow Per Target

Create separate workflow files for each target to enable independent regeneration:

```yaml
# .github/workflows/sdk_generation_main.yaml
name: Generate Main SDK
permissions:
  checks: write
  contents: write
  pull-requests: write
  statuses: write

on:
  workflow_dispatch:
    inputs:
      force:
        description: Force generation of SDK
        type: boolean
        default: false
      set_version:
        description: Optionally set a specific SDK version
        type: string

jobs:
  generate:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/workflow-executor.yaml@v15
    with:
      force: ${{ github.event.inputs.force }}
      mode: pr
      set_version: ${{ github.event.inputs.set_version }}
      speakeasy_version: latest
      target: main-sdk
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
```

```yaml
# .github/workflows/sdk_generation_azure.yaml
name: Generate Azure SDK
permissions:
  checks: write
  contents: write
  pull-requests: write
  statuses: write

on:
  workflow_dispatch:
    inputs:
      force:
        description: Force generation of SDK
        type: boolean
        default: false
      set_version:
        description: Optionally set a specific SDK version
        type: string

jobs:
  generate:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/workflow-executor.yaml@v15
    with:
      force: ${{ github.event.inputs.force }}
      mode: pr
      set_version: ${{ github.event.inputs.set_version }}
      speakeasy_version: latest
      target: azure-sdk
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
```

### Publishing Workflow Per Target

```yaml
# .github/workflows/sdk_publish_main.yaml
name: Publish Main SDK
on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/workflow-executor.yaml@v15
    with:
      mode: release
      target: main-sdk
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
      npm_token: ${{ secrets.NPM_TOKEN }}
```

## Package Naming Conventions

### Recommended Naming Pattern

| Variant | Package Name | Class Name |
|---------|--------------|------------|
| Main | `@myorg/mysdk` | `MySDK` |
| Azure | `@myorg/mysdk-azure` | `MySDKAzure` |
| GCP | `@myorg/mysdk-gcp` | `MySDKGCP` |
| AWS | `@myorg/mysdk-aws` | `MySDKAWS` |

### Configuration Example

```yaml
# Main SDK gen.yaml
typescript:
  packageName: '@myorg/mysdk'
  sdkClassName: MySDK
  envVarPrefix: MYSDK

# Azure variant gen.yaml
typescript:
  packageName: '@myorg/mysdk-azure'
  sdkClassName: MySDKAzure
  envVarPrefix: MYSDK_AZURE
```

## Versioning Strategies

### Lockstep Versioning

All variants share the same version number. Simplest approach for tightly coupled APIs.

```yaml
# All gen.yaml files
typescript:
  version: 1.5.0
```

### Independent Versioning

Each variant has its own version. Better for variants that evolve at different rates.

```yaml
# Main gen.yaml
typescript:
  version: 2.1.0

# Azure gen.yaml
typescript:
  version: 1.8.0

# GCP gen.yaml
typescript:
  version: 1.3.0
```

## Sharing Code Across Variants

### Shared Hooks Pattern

If all variants need the same hooks (e.g., user-agent, telemetry), you have two options:

**Option 1: Duplicate hooks in each variant**
- Simpler but requires manual sync
- Each variant has its own `src/hooks/` directory

**Option 2: Shared hooks via npm package**
- Create a private `@myorg/mysdk-common` package
- Import hooks from common package in each variant

### Shared Extra Modules

For complex custom logic shared across variants:

```
my-multi-sdk/
├── shared/
│   ├── package.json           # @myorg/mysdk-shared
│   └── src/
│       ├── structuredOutput.ts
│       └── helpers.ts
├── packages/
│   ├── azure/
│   │   └── package.json       # depends on @myorg/mysdk-shared
│   └── gcp/
│       └── package.json       # depends on @myorg/mysdk-shared
```

## Testing Multi-Target SDKs

### Test Custom Code Per Variant

```yaml
# .github/workflows/test_custom_code.yaml
name: Test Custom Code

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install
      - run: npm run build
      - run: npm test

  test-azure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install --prefix packages/azure
      - run: npm run build --prefix packages/azure
      - run: npm test --prefix packages/azure

  test-gcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install --prefix packages/gcp
      - run: npm run build --prefix packages/gcp
      - run: npm test --prefix packages/gcp
```

## Best Practices

1. **Use consistent naming**: Follow a predictable pattern for package names, class names, and env var prefixes
2. **Separate workflows**: Create independent CI workflows per target for flexibility
3. **Document variants**: Clearly document what differs between variants in your README
4. **Test each variant**: Ensure tests cover variant-specific functionality
5. **Consider shared code**: Extract common customizations to avoid duplication
6. **Version thoughtfully**: Choose lockstep or independent versioning based on your release cadence

---

## Pre-defined TODO List

When implementing multi-target SDK generation, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Design variant strategy (cloud, regional, partner) | Designing variant strategy |
| 2 | Set up OpenAPI sources in Speakeasy registry | Setting up OpenAPI sources |
| 3 | Create workflow.yaml with multiple targets | Creating multi-target workflow |
| 4 | Configure gen.yaml per target | Configuring per-target generation |
| 5 | Set up repository directory structure | Setting up directory structure |
| 6 | Create CI workflows per target | Creating CI workflows |
| 7 | Configure package naming and versioning | Configuring package naming |
| 8 | Set up shared code if needed | Setting up shared code |
| 9 | Test generation for all targets | Testing all target generation |
| 10 | Configure publishing per target | Configuring publishing |

**Usage:**
```
TodoWrite([
  {content: "Design variant strategy (cloud, regional, partner)", status: "pending", activeForm: "Designing variant strategy"},
  {content: "Set up OpenAPI sources in Speakeasy registry", status: "pending", activeForm: "Setting up OpenAPI sources"},
  {content: "Create workflow.yaml with multiple targets", status: "pending", activeForm: "Creating multi-target workflow"},
  {content: "Configure gen.yaml per target", status: "pending", activeForm: "Configuring per-target generation"},
  {content: "Set up repository directory structure", status: "pending", activeForm: "Setting up directory structure"},
  {content: "Create CI workflows per target", status: "pending", activeForm: "Creating CI workflows"},
  {content: "Configure package naming and versioning", status: "pending", activeForm: "Configuring package naming"},
  {content: "Set up shared code if needed", status: "pending", activeForm: "Setting up shared code"},
  {content: "Test generation for all targets", status: "pending", activeForm: "Testing all target generation"},
  {content: "Configure publishing per target", status: "pending", activeForm: "Configuring publishing"}
])
```
