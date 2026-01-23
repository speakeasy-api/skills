# Agent Guidelines

This document provides guidance for AI coding agents working with Speakeasy Agent Skills.

## Repository Structure

```
speakeasy-api/agent-skills/
├── .claude-plugin/          # Claude Code plugin configuration
│   ├── plugin.json          # Plugin manifest (name: "speakeasy")
│   └── marketplace.json     # Marketplace metadata
├── skills/                  # Skill definitions
│   └── {skill-name}/
│       └── SKILL.md         # Skill instructions
├── AGENTS.md                # This file
├── CLAUDE.md                # Claude-specific instructions
├── README.md                # User documentation
└── LICENSE                  # Apache-2.0
```

## Skill Format

Each skill follows the [Agent Skills specification](https://agentskills.io/specification):

```yaml
---
name: skill-name
description: When to use this skill (include trigger phrases)
---

# skill-name

Instructions for the agent...
```

### Naming Conventions

- **Directories**: `kebab-case` (e.g., `start-new-sdk-project`)
- **Files**: `SKILL.md` (uppercase, exact filename)
- **Names in frontmatter**: Must match directory name

## Available Skills

| Skill | Purpose |
|-------|---------|
| `start-new-sdk-project` | Initialize SDK generation with `speakeasy quickstart` |
| `regenerate-sdk` | Re-run SDK generation with `speakeasy run` |
| `validate-openapi-spec` | Lint and validate OpenAPI specs |
| `create-openapi-overlay` | Create overlays to customize specs without modification |
| `apply-openapi-overlay` | Apply overlay files to specs |
| `merge-openapi-specs` | Combine multiple OpenAPI specs |
| `check-workspace-status` | View configured targets and sources |
| `diagnose-generation-failure` | Troubleshoot failed SDK generation |
| `fix-validation-errors-with-overlays` | Fix lint errors using overlays |
| `get-ai-suggestions` | Get AI-powered suggestions for operation IDs |
| `improve-operation-ids` | Improve SDK method naming |
| `configure-authentication` | Set up Speakeasy CLI authentication |

## Key Principles

### 1. Overlay Over Modify

Never modify source OpenAPI specs directly. Use overlays to:
- Fix validation errors
- Improve operation IDs
- Add Speakeasy extensions

Overlays are portable across spec versions and don't require access to the original spec.

### 2. Decision Framework

When encountering issues:

| Issue Type | Action |
|------------|--------|
| Naming issues (operationIds, descriptions) | Fix with overlays |
| Structural issues (invalid $refs, missing schemas) | Ask the user |
| Design issues (authentication, API structure) | Produce strategy document |

### 3. AI-Friendly Output

For commands with large output, reduce context by piping:

```bash
speakeasy run --output console 2>&1 | tail -50
speakeasy lint openapi -s spec.yaml 2>&1 | grep -E "(error|warning)"
```

### 4. Grouped SDK Methods

Guide users toward clean SDK patterns:

```typescript
// Good: Grouped methods
sdk.users.list()
sdk.users.get(id)

// Avoid: Flat methods
sdk.listUsers()
sdk.getUser(id)
```

Use `x-speakeasy-group` and `x-speakeasy-name-override` in overlays.

## Contributing Skills

1. Create a new directory under `skills/`
2. Add a `SKILL.md` file with proper frontmatter
3. Keep instructions under 500 lines
4. Include trigger phrases in the description
5. Test with multiple agent platforms

## Validation

Use [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) to validate:

```bash
skills-ref validate ./skills/my-skill
```
