---
short_description: "Entry point for Speakeasy agent context"
long_description: |
  This is the navigation index for the Speakeasy agent context filesystem.
  Start here to find the right guide for your task. This file serves as
  the routing table for AI agents using `speakeasy agent context`.
---

# Speakeasy Agent Context Index

This filesystem provides context and plans for AI agents to autonomously generate SDKs and Terraform providers using Speakeasy.

## Quick Routing Table

**What are you trying to do?**

| Goal | Start Here |
|------|------------|
| Generate an SDK from an OpenAPI spec | `plans/sdk-generation.md` |
| Generate a Terraform provider | `plans/tf-provider-generation.md` |
| Extract OpenAPI from existing code | `code-first/[framework].md` |
| Fix OpenAPI validation errors | `spec-first/validation.md` |
| Customize SDK generation | `sdk-customization/` |
| Generate multiple SDK variants (Azure, GCP, etc.) | `sdk-customization/multi-target-sdks.md` |
| Set up a multi-SDK monorepo | `plans/sdk-generation.md#advanced-multi-sdk-monorepos` |
| Use overlay recipes (open enums, global headers) | `spec-first/overlays.md#overlay-recipes` |
| Use multi-overlay workflows | `spec-first/overlays.md#multi-overlay-workflow-patterns` |
| Track overlay changes with metadata | `spec-first/overlays.md#overlay-metadata-tracking` |
| Implement custom security (HMAC, signatures) | `spec-first/overlays.md#custom-security-schemes-via-overlay` |
| Add SDK hooks (user-agent, telemetry) | `sdk-customization/hooks.md` |
| Implement HTTP signature authentication | `sdk-customization/hooks.md#custom-security-hook-http-signature-authentication` |
| Configure SDK retries, timeouts, pagination | `sdk-customization/runtime-configuration.md` |
| Configure SDK authentication and security | `sdk-customization/authentication-config.md` |
| Customize SDK error handling | `sdk-customization/error-handling.md` |
| Persist custom code changes across regenerations | `sdk-customization/custom-code.md` |
| Generate MCP server for AI assistants | `sdk-customization/mcp-server.md` |
| Orchestrate multi-repo SDK generation | `sdk-customization/multi-repo-workflows.md` |
| Understand SDK language specifics | `sdk-languages/[language].md` |
| Add custom utilities to Python SDKs | `sdk-languages/python.md#extending-the-sdk-with-sidecar-utilities` |
| Publish Java SDK to Maven Central | `sdk-languages/java.md#maven-central-publishing` |
| Add custom code to TypeScript SDKs | `sdk-languages/typescript.md#custom-code-regions` |
| Publish TypeScript SDK to JSR (Deno) | `sdk-languages/typescript.md#jsr-deno-publishing` |
| Configure Ruby SDK with Sorbet typing | `sdk-languages/ruby.md#sorbet-type-checking` |
| Publish Ruby SDK to RubyGems | `sdk-languages/ruby.md#rubygems-publishing` |
| Configure PHP SDK with Laravel integration | `sdk-languages/php.md#laravel-integration` |
| Publish PHP SDK to Packagist | `sdk-languages/php.md#publishing-to-packagist` |
| Generate Go SDK with interfaces for testing | `sdk-languages/go.md#interface-generation` |
| Use Go SDK in Kubernetes operators | `sdk-languages/go.md#kubernetes-operator-integration` |
| Set up SDK integration tests | `sdk-testing/integration-testing.md` |
| Configure Arazzo API testing | `sdk-testing/arazzo-testing.md` |
| Disable tests for specific endpoints | `sdk-testing/arazzo-testing.md#disabling-tests-via-overlay` |
| Run AI-powered contract tests | `sdk-testing/contract-testing.md` |
| Fix ResponseValidationError at runtime | `sdk-testing/contract-testing.md` |
| Validate spec matches live API | `spec-first/validation.md#dynamic-validation-contract-testing` |

## Directory Structure

```
agent-context/
├── INDEX.md                    # You are here
├── plans/                      # Decision trees for workflows
│   ├── sdk-generation.md       # Full SDK generation workflow
│   └── tf-provider-generation.md
├── code-first/                 # Extract OpenAPI from code
│   ├── fastapi.md
│   ├── flask.md
│   ├── django.md
│   ├── spring-boot.md
│   ├── nestjs.md
│   ├── hono.md
│   ├── rails.md
│   └── laravel.md
├── spec-first/                 # OpenAPI validation and fixes
│   ├── validation.md
│   ├── overlays.md             # OpenAPI overlays and recipes
│   ├── security-schemes.md
│   ├── pagination.md
│   └── schemas.md
├── sdk-languages/              # Language-specific SDK guides
│   ├── python.md
│   ├── typescript.md           # TS: code regions, extra modules, Zod
│   ├── go.md                   # Go: hooks, interfaces, mocks, K8s
│   ├── java.md
│   ├── csharp.md
│   ├── ruby.md                 # Ruby: Sorbet typing, RubyGems publishing
│   └── php.md
├── sdk-customization/          # Cross-language SDK customization
│   ├── hooks.md                # SDK hooks (UA, telemetry, custom security)
│   ├── runtime-configuration.md # Retries, timeouts, pagination, servers
│   ├── authentication-config.md # Global/per-op security, env vars
│   ├── error-handling.md       # Custom error classes and schemas
│   ├── custom-code.md          # Persist changes across regenerations
│   ├── multi-target-sdks.md    # Multiple variants from one repo
│   ├── multi-repo-workflows.md # Cross-repo SDK orchestration (CI/CD)
│   ├── mcp-server.md           # MCP server for AI assistant integration
│   └── readme-customization.md # SDK README branding
├── sdk-testing/                # SDK testing patterns
│   ├── integration-testing.md  # Integration test infrastructure
│   ├── arazzo-testing.md       # Arazzo API testing format
│   └── contract-testing.md     # AI-powered contract testing
├── terraform/                  # Terraform provider specifics
│   ├── crud-mapping.md
│   ├── customization.md
│   ├── testing-guide.md
│   └── publishing.md
└── CLI_REFERENCE.md            # Canonical CLI command documentation
```

## Decision Tree: Where to Start

```
START
  │
  ├─ Do you have an OpenAPI/Swagger spec?
  │    │
  │    ├─ YES ──► Is the spec valid?
  │    │           │
  │    │           ├─ YES ──► What do you want to generate?
  │    │           │           │
  │    │           │           ├─ SDK ──► plans/sdk-generation.md
  │    │           │           └─ Terraform Provider ──► plans/tf-provider-generation.md
  │    │           │
  │    │           └─ NO/UNSURE ──► spec-first/validation.md
  │    │
  │    └─ NO ──► Do you have API code?
  │               │
  │               ├─ YES ──► What framework?
  │               │           ├─ FastAPI ──► code-first/fastapi.md
  │               │           ├─ Flask ──► code-first/flask.md
  │               │           ├─ Django ──► code-first/django.md
  │               │           ├─ Spring Boot ──► code-first/spring-boot.md
  │               │           ├─ NestJS ──► code-first/nestjs.md
  │               │           ├─ Hono ──► code-first/hono.md
  │               │           ├─ Rails ──► code-first/rails.md
  │               │           └─ Laravel ──► code-first/laravel.md
  │               │
  │               └─ NO ──► Cannot proceed without spec or code
```

## Troubleshooting Tree

```
PROBLEM
  │
  ├─ Getting ResponseValidationError at runtime?
  │    │
  │    └─ SDK types don't match server responses
  │         ├─ Run contract tests to identify all mismatches
  │         │    → sdk-testing/contract-testing.md
  │         └─ Fix spec or create overlay to correct types
  │              → spec-first/validation.md#dynamic-validation-contract-testing
  │
  ├─ SDK doesn't match live API behavior?
  │    │
  │    ├─ Spec may have drifted from API
  │    │    → Run contract tests to detect drift
  │    │       sdk-testing/contract-testing.md
  │    │
  │    └─ Third-party spec may be inaccurate
  │         → Validate with contract testing before trusting
  │            sdk-testing/contract-testing.md
  │
  ├─ Type mismatch errors in generated SDK?
  │    │
  │    ├─ At compile time ──► Check spec schema definitions
  │    │                       spec-first/validation.md
  │    │
  │    └─ At runtime ──► Server returns unexpected types
  │                      → Contract testing required
  │                         sdk-testing/contract-testing.md
  │
  └─ Enum value not recognized?
       │
       └─ API returned value not in spec enum
            ├─ Add missing value to spec/overlay
            │    → spec-first/overlays.md
            └─ Or use open enums for anti-fragility
                 → spec-first/overlays.md#overlay-recipes
```

## Common Workflows

### Workflow A: First-Time SDK Generation

1. Read `plans/sdk-generation.md`
2. Run `speakeasy quickstart`
3. Follow interactive prompts
4. SDK generated in `./sdk-[language]/`

### Workflow B: Existing Codebase → SDK

1. Identify framework in `code-first/`
2. Extract OpenAPI spec
3. Validate with `speakeasy validate openapi`
4. Fix issues using `spec-first/` guides
5. Generate SDK via `plans/sdk-generation.md`

### Workflow C: SDK Customization

1. Ensure `gen.yaml` exists (from quickstart)
2. Read `sdk-customization/` guides
3. Modify `gen.yaml`
4. Regenerate with `speakeasy run`

### Workflow D: Multi-Target SDK (Azure, GCP, etc.)

1. Read `sdk-customization/multi-target-sdks.md`
2. Configure multiple sources in `workflow.yaml`
3. Set up target outputs to `packages/` subdirectories
4. Create CI workflows per target

### Workflow E: SDK Extensions (Hooks, Custom Methods)

1. For persistent changes anywhere → `sdk-customization/custom-code.md`
2. For cross-cutting concerns → `sdk-customization/hooks.md`
3. For predefined extension points → `sdk-languages/typescript.md#custom-code-regions`
4. For complex logic → `sdk-languages/typescript.md#extra-modules-pattern`

## Essential CLI Commands

| Command | Purpose |
|---------|---------|
| `speakeasy quickstart` | Interactive SDK setup |
| `speakeasy run` | Regenerate SDK from gen.yaml |
| `speakeasy validate openapi -s spec.yaml` | Validate OpenAPI spec |
| `speakeasy auth login` | Authenticate with Speakeasy |
| `speakeasy agent context [path]` | Access this filesystem |

## Getting Help

- **Authentication issues:** Run `speakeasy auth login`
- **Validation errors:** See `spec-first/validation.md`
- **Unsupported feature:** Check language guide in `sdk-languages/`
- **CLI errors:** See `cli-reference/` or run `speakeasy --help`
