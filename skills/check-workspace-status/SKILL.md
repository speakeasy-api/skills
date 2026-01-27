---
name: check-workspace-status
description: Use when checking current Speakeasy setup or workspace info. Triggers on "workspace status", "speakeasy status", "what targets configured", "show current setup", "list SDK targets"
license: Apache-2.0
---

# check-workspace-status

Check configured targets, sources, and workspace info.

## When to Use

- Checking what SDK targets are configured
- Viewing published SDK versions and URLs
- Verifying workspace authentication is working
- User says: "workspace status", "what targets configured", "list SDK targets"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Authentication | Yes | Via `speakeasy auth login` or `SPEAKEASY_API_KEY` env var |

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

Requires `SPEAKEASY_API_KEY` env var (run `speakeasy auth login` or export `SPEAKEASY_API_KEY` directly).

## Output Includes

- Workspace name and account type
- Published targets (version, URLs, last publish/generate)
- Configured targets (unpublished, with repo URLs)
- Unconfigured targets and generation failures

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "unauthorized" | Missing or invalid API key | Run `speakeasy auth login` or set `SPEAKEASY_API_KEY` |
| Empty output | No targets configured | Run `start-new-sdk-project` to set up first |
| "workspace not found" | Wrong workspace ID | Check `~/.speakeasy/config.yaml` |
