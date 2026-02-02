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

### Phase 2: Future Work

| Content Area | Recommendation |
|--------------|----------------|
| Multi-target SDKs | Create `orchestrate-multi-target-sdks` |
| Multi-repo workflows | Create `orchestrate-multi-repo-sdks` |
| Terraform publishing | Enhance `generate-terraform-provider` |
| Advanced validation | Enhance `diagnose-generation-failure` |

### Phase 3: Meta Skill Removal

Once all content is distributed:
1. Verify all trigger phrases are covered by granular skills
2. Update meta skill description to be a pure router
3. Eventually deprecate or remove meta skill

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
| Multi-target skill | Pending (Phase 2) |
| Multi-repo skill | Pending (Phase 2) |
| Meta skill removal | Pending (Phase 3) |
