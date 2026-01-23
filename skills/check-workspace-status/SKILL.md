---
name: check-workspace-status
description: Use when checking current Speakeasy setup or workspace info. Triggers on "workspace status", "speakeasy status", "what targets configured", "show current setup", "list SDK targets"
---

# check-workspace-status

Check configured targets, sources, and workspace info.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| SPEAKEASY_API_KEY | Yes | Environment variable |

## Outputs

| Output | Description |
|--------|-------------|
| Workspace info | Name, account type |
| Published targets | Version, URLs, last publish date |
| Configured targets | Unpublished targets, repo URLs |
| Unconfigured targets | Targets with issues |

## Command

```bash
# For LLMs/automation (recommended)
speakeasy status --output json

# For human-readable output
speakeasy status --output console
```

Requires `SPEAKEASY_API_KEY` env var (see `configure-authentication` skill).

## Output Includes

- Workspace name and account type
- Published targets (version, URLs, last publish/generate)
- Configured targets (unpublished, with repo URLs)
- Unconfigured targets and generation failures

## Related Skills

- `configure-authentication` - Set up API key if status fails
- `regenerate-sdk` - Run generation for configured targets
- `start-new-sdk-project` - Set up new targets
