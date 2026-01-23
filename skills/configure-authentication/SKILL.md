---
name: configure-authentication
description: Use when setting up Speakeasy auth or troubleshooting auth errors. Triggers on "set up API key", "configure auth", "SPEAKEASY_API_KEY", "unauthorized error", "authentication failed", "how to authenticate"
---

# configure-authentication

Set up authentication for Speakeasy CLI commands.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| API key | Yes | From Speakeasy Dashboard |

## Outputs

| Output | Description |
|--------|-------------|
| Authenticated CLI | Commands can access Speakeasy services |

## Quick Setup

Set `SPEAKEASY_API_KEY` environment variable (takes precedence over config files):

```bash
export SPEAKEASY_API_KEY="<your-api-key>"
```

Get your API key: [Speakeasy Dashboard](https://app.speakeasy.com) → Settings → API Keys

## Verifying Authentication

```bash
speakeasy status --output json
```

Returns workspace info if authenticated; `unauthorized` error if not.

## Common Errors

| Error | Solution |
|-------|----------|
| `unauthorized` | Set valid `SPEAKEASY_API_KEY` env var |
| `workspace not found` | Check workspace ID in `~/.speakeasy/config.yaml` |

## Alternative: Config File

Create `~/.speakeasy/config.yaml`:

```yaml
speakeasy_api_key: "<your-api-key>"
speakeasy_workspace_id: "<workspace-id>"  # optional
# For multiple workspaces:
workspace_api_keys:
  org@workspace: "<api-key>"
```

## Related Skills

- `start-new-sdk-project` - Requires auth for quickstart
- `check-workspace-status` - Verify auth is working
- `regenerate-sdk` - Requires auth for generation
