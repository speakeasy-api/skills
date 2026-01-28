---
name: speakeasy-agent-mode
description: FIRST step for any Speakeasy/SDK/OpenAPI task. Triggers on "speakeasy", "SDK generation", "generate SDK", "OpenAPI", "API spec".
license: Apache-2.0
---

# speakeasy-agent-mode

## Rule

Before any Speakeasy task: **run `speakeasy agent context`**. Prefer CLI output over web/docs.

## Commands

```bash
speakeasy agent context          # Get current CLI capabilities
speakeasy agent feedback "<msg>" # Report issues or suggestions
speakeasy <command> --help       # Command-specific help
```

## Workflow

1. `speakeasy agent context`
2. Do the task using Speakeasy CLI
3. If needed: `speakeasy agent feedback "<msg>"`

## Don'ts

- Don't use web search as source of truth
- Don't guess syntax; use `context` or `--help`
- Don't skip `context` at session start