# Meta Skill Decomposition Plan

This document outlines the plan to decompose `sdk-tf-generation-best-practices` into granular skills.

## Background

The meta skill (`sdk-tf-generation-best-practices`) acts as a routing hub that directs to specific skills and content files. Broad "meta" skills are less effective for agent skill triggering compared to focused, specific skills.

## Current State

### Existing Granular Skills (11 total)
- `start-new-sdk-project` - Initial SDK setup ✓
- `diagnose-generation-failure` - Troubleshooting ✓
- `manage-openapi-overlays` - Overlay management ✓
- `improve-sdk-naming` - Naming improvements ✓
- `writing-openapi-specs` - OpenAPI authoring ✓
- `customize-sdk-hooks` - SDK hooks ✓
- `customize-sdk-runtime` - Runtime config ✓
- `setup-sdk-testing` - Testing patterns ✓
- `generate-terraform-provider` - Terraform generation ✓
- `generate-mcp-server` - MCP server generation ✓
- `extract-openapi-from-code` - Code-first extraction ✓

### New Language-Specific Skills (7 total) - CREATED
- `generate-sdk-for-python` - Python SDK configuration
- `generate-sdk-for-typescript` - TypeScript SDK configuration
- `generate-sdk-for-go` - Go SDK configuration
- `generate-sdk-for-java` - Java SDK configuration
- `generate-sdk-for-csharp` - C# SDK configuration
- `generate-sdk-for-ruby` - Ruby SDK configuration
- `generate-sdk-for-php` - PHP SDK configuration

## Content Distribution

### Phase 1: Completed ✓

| Meta Skill Content | Distributed To |
|-------------------|----------------|
| Language-specific routing | 7 new language skills |
| Troubleshooting tree | `diagnose-generation-failure` |
| CLI reference | `start-new-sdk-project` |
| Large spec handling | `diagnose-generation-failure` |
| Decision tree (start) | Covered by existing skills |

### Phase 2: Completed ✓

| Content Area | Status |
|--------------|--------|
| Multi-target SDKs | ✓ Created `orchestrate-multi-target-sdks` |
| Multi-repo workflows | ✓ Created `orchestrate-multi-repo-sdks` |
| Terraform publishing | ✓ Enhanced `generate-terraform-provider` |

### Phase 3: In Progress

| Content Area | Status | Target Skill |
|--------------|--------|--------------|
| Speakeasy extensions | ✓ Created `configure-speakeasy-extensions` | New skill |
| Framework Speakeasy integration | ✓ Enhanced `extract-openapi-from-code` | Added x-speakeasy-* examples |
| Terraform testing | ✓ Enhanced `generate-terraform-provider` | Added acceptance test patterns |
| `code-first/` detailed guides | Pending | Content files remain as reference |
| `sdk-testing/` Arazzo/contract | Pending | Enhance `setup-sdk-testing` |
| `spec-first/` validation | Pending | Enhance `writing-openapi-specs` |
| `plans/` generation workflows | Pending | Keep as reference |

### Phase 4: Meta Skill Removal

Once Phase 3 is complete:
1. Verify all trigger phrases are covered by granular skills
2. Move any remaining reference content to a docs location
3. Remove the meta skill

## Skill Trigger Coverage

After decomposition, these phrases trigger specific skills:

| Phrase | Triggered Skill |
|--------|----------------|
| "generate Python SDK" | `generate-sdk-for-python` |
| "TypeScript client" | `generate-sdk-for-typescript` |
| "Go SDK interfaces" | `generate-sdk-for-go` |
| "Java Maven Central" | `generate-sdk-for-java` |
| "C# NuGet publish" | `generate-sdk-for-csharp` |
| "Ruby gem" | `generate-sdk-for-ruby` |
| "PHP Packagist" | `generate-sdk-for-php` |
| "SDK generation failed" | `diagnose-generation-failure` |
| "create SDK" | `start-new-sdk-project` |
| "SDK hooks" | `customize-sdk-hooks` |
| "OpenAPI overlay" | `manage-openapi-overlays` |
| "Terraform provider" | `generate-terraform-provider` |
| "MCP server" | `generate-mcp-server` |
| "multi-target SDK" | `orchestrate-multi-target-sdks` |
| "SDK monorepo" | `orchestrate-multi-target-sdks` |
| "multi-repo SDK" | `orchestrate-multi-repo-sdks` |
| "cross-repo workflows" | `orchestrate-multi-repo-sdks` |
| "x-speakeasy" | `configure-speakeasy-extensions` |
| "add retries" | `configure-speakeasy-extensions` |
| "open enums" | `configure-speakeasy-extensions` |
| "global headers" | `configure-speakeasy-extensions` |

## Content Files Retention

The `content/sdk-languages/*.md` files remain as detailed reference material. The new skills are compact routers that:
1. Provide essential configuration
2. Show quick-start patterns
3. Link to related skills

This approach keeps skills under 150 lines while detailed content remains available in the content directory.

## Implementation Summary

| Item | Status |
|------|--------|
| Python skill | ✓ Created |
| TypeScript skill | ✓ Created |
| Go skill | ✓ Created |
| Java skill | ✓ Created |
| C# skill | ✓ Created |
| Ruby skill | ✓ Created |
| PHP skill | ✓ Created |
| CLI reference embedded | ✓ Added to start-new-sdk-project |
| Troubleshooting tree embedded | ✓ Added to diagnose-generation-failure |
| Large spec handling embedded | ✓ Added to diagnose-generation-failure |
| Multi-target skill | ✓ Created (Phase 2) |
| Multi-repo skill | ✓ Created (Phase 2) |
| Terraform publishing enhanced | ✓ Added to generate-terraform-provider (Phase 2) |
| Speakeasy extensions skill | ✓ Created (Phase 3) |
| Framework Speakeasy integration | ✓ Enhanced extract-openapi-from-code (Phase 3) |
| Terraform testing | ✓ Enhanced generate-terraform-provider (Phase 3) |
| Code-first detailed guides | Pending (Phase 3) |
| SDK testing content | Pending (Phase 3) |
| Spec-first content | Pending (Phase 3) |
| Meta skill removal | Pending (Phase 4) |
