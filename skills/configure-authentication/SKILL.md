---
name: configure-authentication
description: Use when setting up Speakeasy auth or troubleshooting auth errors. Triggers on "set up API key", "configure auth", "speakeasy auth login", "unauthorized error", "authentication failed", "how to authenticate"
license: Apache-2.0
---

# configure-authentication

Set up authentication for Speakeasy CLI commands.

## When to Use

- First time setting up Speakeasy CLI
- Getting "unauthorized" errors from commands
- Setting up CI/CD or AI agent environments
- User says: "set up API key", "configure auth", "authentication failed"

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

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `unauthorized` | Missing or invalid API key | Run `speakeasy auth login` or set `SPEAKEASY_API_KEY` |
| `workspace not found` | Wrong workspace configured | Check workspace ID in `~/.speakeasy/config.yaml` |
| Token expired | Session timed out | Re-run `speakeasy auth login` |

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
