# Claude Code Instructions

This file contains Claude-specific guidance for working with Speakeasy Agent Skills.

## Installation

```bash
# Via skills CLI
npx skills add speakeasy-api/agent-skills

# Via Claude Code marketplace
/plugin marketplace add speakeasy-api/agent-skills
/plugin install speakeasy
```

## Skill Invocation

Skills are namespaced under `speakeasy:`:

```
/speakeasy:start-new-sdk-project
/speakeasy:validate-openapi-spec
/speakeasy:regenerate-sdk
```

Or invoke via the Skill tool:
```
skill: "speakeasy:start-new-sdk-project"
```

## Speakeasy CLI Prerequisites

Before using these skills, ensure:

1. **Speakeasy CLI is installed**:
   ```bash
   brew install speakeasy-api/homebrew-tap/speakeasy
   # or
   curl -fsSL https://raw.githubusercontent.com/speakeasy-api/speakeasy/main/install.sh | sh
   ```

2. **Authentication is configured** (for non-interactive environments):
   ```bash
   export SPEAKEASY_API_KEY="<your-api-key>"
   ```

## Workflow Patterns

### New SDK Project

```bash
# 1. Initialize with quickstart
speakeasy quickstart -s ./openapi.yaml -t typescript

# 2. Generate the SDK
speakeasy run
```

### Iterative Development

```bash
# After spec changes, regenerate
speakeasy run --output console

# Validate changes
speakeasy lint openapi -s ./openapi.yaml
```

### Fixing Issues with Overlays

```bash
# Get AI suggestions for operation IDs
speakeasy suggest operation-ids -s ./openapi.yaml -o ./overlay.yaml

# Apply overlay
speakeasy overlay apply -s ./openapi.yaml -o ./overlay.yaml
```

## Error Handling

When SDK generation fails:

1. **Check the error output** - Look for specific validation errors
2. **Use `diagnose-generation-failure` skill** - Provides troubleshooting steps
3. **Create overlays for fixable issues** - Don't modify source specs
4. **Escalate structural issues** - Ask the user for guidance

## Context Efficiency

These skills are designed for efficient context usage:

- **Metadata only** (~100 tokens): Skill names and descriptions load at startup
- **Full instructions** (< 500 lines): Loaded when skill activates
- **On-demand resources**: Additional files loaded as needed

When running Speakeasy commands, reduce output context:

```bash
# Limit output to last 50 lines
speakeasy run 2>&1 | tail -50

# Filter for errors only
speakeasy lint openapi -s spec.yaml 2>&1 | grep -i error
```

## Supported Languages

Speakeasy generates SDKs for:

| Language | Target Flag |
|----------|-------------|
| TypeScript | `typescript` |
| Python | `python` |
| Go | `go` |
| Java | `java` |
| C# | `csharp` |
| PHP | `php` |
| Ruby | `ruby` |
| Kotlin | `kotlin` |
| Terraform | `terraform` |
