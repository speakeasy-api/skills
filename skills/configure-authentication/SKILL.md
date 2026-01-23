---
name: configure-authentication
description: Use when setting up Speakeasy auth or troubleshooting auth errors. Triggers on "set up API key", "configure auth", "speakeasy auth login", "unauthorized error", "authentication failed", "how to authenticate"
---

# configure-authentication

Set up authentication for Speakeasy CLI commands.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| API key | Yes | From Speakeasy Dashboard or browser login |

## Outputs

| Output | Description |
|--------|-------------|
| Authenticated CLI | Commands can access Speakeasy services |

## Interactive Login (Recommended)

```bash
speakeasy auth login
```

Opens browser for authentication. Credentials stored at `~/.speakeasy/config.yaml`.

## Non-Interactive (CI/AI Agents)

Set `SPEAKEASY_API_KEY` environment variable:

```bash
export SPEAKEASY_API_KEY="<your-api-key>"
```

Get your API key: [Speakeasy Dashboard](https://app.speakeasy.com) → Settings → API Keys

Note: Environment variable takes precedence over config file.

## Verifying Authentication

```bash
speakeasy status --output json
```

Returns workspace info as JSON if authenticated; `unauthorized` error if not.

## Common Errors

| Error | Solution |
|-------|----------|
| `unauthorized` | Run `speakeasy auth login` or set `SPEAKEASY_API_KEY` |
| `workspace not found` | Check workspace ID in `~/.speakeasy/config.yaml` |

## Config File Location

Credentials stored at `~/.speakeasy/config.yaml`:

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
