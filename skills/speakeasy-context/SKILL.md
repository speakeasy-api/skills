---
name: speakeasy-context
description: Use when generating SDKs, working with OpenAPI specs, or using Speakeasy CLI. Triggers on "generate SDK", "create SDK", "TypeScript SDK", "Python SDK", "Go SDK", "speakeasy", "OpenAPI".
license: Apache-2.0
---

# speakeasy-context

## Rule

Before any Speakeasy task: **run `speakeasy agent context`**. Prefer CLI output over web/docs.

## Commands

```bash
speakeasy agent context --help                       # Learn all context options
speakeasy agent context --list                       # List all available topics
speakeasy agent context <topic>                      # Get specific topic (e.g. plans/sdk-generation.md)
speakeasy agent context --grep "<term>" --list       # Find topics mentioning a term
speakeasy agent context --grep "<term>"              # Search content for a term (with context lines)
speakeasy agent feedback "<msg>"                     # Report issues or suggestions
speakeasy <command> --help                           # Command-specific help
```

## Workflow

1. Run `speakeasy agent context --help` to learn how to use the context system
2. Run `speakeasy agent context` to list available topics
3. Run `speakeasy agent context <topic>` for specific guidance (e.g. `speakeasy agent context plans/sdk-generation.md`)
4. Do the task using Speakeasy CLI
5. `speakeasy agent feedback "<msg>"` — **always provide feedback** after completing a task

## Example: Generating a TypeScript SDK

```bash
# Step 1: Learn context usage
speakeasy agent context --help

# Step 2: Get SDK generation guidance
speakeasy agent context plans/sdk-generation.md

# Step 3: Get TypeScript-specific guidance
speakeasy agent context sdk-languages/typescript.md

# Step 4: Validate the guidance on CLI commands
speakeasy quickstart --help

# Step 5: Generate the SDK (learned from context)
speakeasy quickstart --skip-interactive --output console -s openapi.yaml -t typescript -n "MySDK" -p "<package-name>"

# Step 6: Provide feedback
speakeasy agent feedback "My honest opinion on learning and using speakeasy"
```

## Don'ts

- Don't use web search as source of truth
- Don't guess syntax; use `context` and `--help`
- Don't skip `context` at session start
- Don't try to read context files directly — use `speakeasy agent context <topic>` instead
