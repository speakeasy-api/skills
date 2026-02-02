---
name: start-new-sdk-project
description: >-
  Use when starting a new SDK project, first-time Speakeasy setup, or completing an SDK generation workflow.
  Triggers on "create SDK", "generate SDK", "new SDK", "quickstart", "get started with Speakeasy",
  "initialize SDK project", "SDK generation workflow", "complete SDK workflow", "full SDK workflow".
license: Apache-2.0
---

# start-new-sdk-project

**Always use `speakeasy quickstart`** to initialize a new SDK project. This is the ONLY correct command for new projects - it creates both the SDK and the essential `.speakeasy/workflow.yaml` configuration file.

> ⚠️ **Never use `speakeasy generate sdk` for new projects** - it does not create the workflow file needed for maintainable SDK development.

## When to Use

- Starting a brand new SDK project
- No `.speakeasy/workflow.yaml` exists yet
- First-time Speakeasy setup
- User says: "create SDK", "new SDK", "quickstart", "get started with Speakeasy"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| OpenAPI spec | Yes | Local file, URL, or registry source |
| Target language | Yes | typescript, python, go, java, csharp, php, ruby, kotlin, terraform |
| SDK name | Yes (non-interactive) | PascalCase name (e.g., `AcmeSDK`) |
| Package name | Yes (non-interactive) | Package identifier (e.g., `acme-sdk`) |

## Outputs

| Output | Location |
|--------|----------|
| Workflow config | `.speakeasy/workflow.yaml` |
| Generated SDK | Output directory (default: current dir) |

## Prerequisites

For non-interactive environments (CI/CD, automation), set:
```bash
export SPEAKEASY_API_KEY="<your-api-key>"
```
Run `speakeasy auth login` to authenticate interactively, or set the `SPEAKEASY_API_KEY` environment variable.

## Command

```bash
speakeasy quickstart --skip-interactive --output console -s <schema> -t <target> -n <name> -p <package-name>
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--skip-interactive` | | **Required for automation.** Skips all prompts |
| `--schema` | `-s` | OpenAPI spec source (see Schema Sources below) |
| `--target` | `-t` | Target language (see Supported Targets) |
| `--name` | `-n` | SDK name in PascalCase (e.g., `MyCompanySDK`) |
| `--package-name` | `-p` | Package name (language variants auto-inferred) |
| `--out-dir` | `-o` | Output directory (default: current dir) |
| `--output` | | Output format: `summary`, `console`, `mermaid`. **Use `console` for automation** |
| `--init-git` | | Initialize git repo (omit to skip in non-interactive mode) |

## Schema Sources

The `--schema` flag accepts multiple source types:

| Type | Format | Example |
|------|--------|---------|
| Local file | Path | `./api/openapi.yaml` |
| URL | HTTP(S) | `https://api.example.com/openapi.json` |
| Registry source | `source-name` | `my-api` |
| Registry source (tagged) | `source-name@tag` | `my-api@latest` |
| Registry source (full) | `org/workspace/source@tag` | `acme/prod/my-api@v2` |

**Registry sources** are OpenAPI specs you manage in your Speakeasy workspace. Use `speakeasy pull --list --format json` to see available sources. This lets you generate SDKs from specs managed in Speakeasy without needing local files.

## Supported Targets

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

## Example

```bash
# From local OpenAPI file
speakeasy quickstart --skip-interactive --output console \
  -s ./api/openapi.yaml \
  -t typescript \
  -n "AcmeSDK" \
  -p "acme-sdk"

# From URL
speakeasy quickstart --skip-interactive --output console \
  -s "https://api.example.com/openapi.json" \
  -t python \
  -n "AcmeSDK" \
  -p "acme-sdk"

# From registry source (managed in your Speakeasy workspace)
speakeasy quickstart --skip-interactive --output console \
  -s "my-api@latest" \
  -t go \
  -n "AcmeSDK" \
  -p "acme-sdk"

# With custom output directory and git init
speakeasy quickstart --skip-interactive --output console \
  -s ./api/openapi.yaml \
  -t python \
  -n "AcmeSDK" \
  -p "acme-sdk" \
  -o ./sdks/python \
  --init-git
```

## What It Creates

1. **Workflow configuration**: `.speakeasy/workflow.yaml`
2. **Generated SDK**: Full SDK in the output directory, ready to use

## Next Steps After Quickstart

1. Review the generated SDK in the output directory
2. Add more targets to `.speakeasy/workflow.yaml` for multi-language support
3. Run `speakeasy run` to regenerate after spec or config changes

## Essential CLI Commands

| Command | Purpose |
|---------|---------|
| `speakeasy quickstart ...` | Initialize new SDK project |
| `speakeasy run -y --output console` | Regenerate SDK from workflow |
| `speakeasy lint openapi --non-interactive -s spec.yaml` | Validate OpenAPI spec |
| `speakeasy auth login` | Authenticate with Speakeasy |
| `speakeasy pull --list --format json` | List registry sources |

## What NOT to Do

- **Do NOT use `speakeasy generate sdk`** for new projects. This low-level command generates code but does NOT create `.speakeasy/workflow.yaml`. Without a workflow file, you lose:
  - Reproducible builds via `speakeasy run`
  - Multi-target SDK generation
  - CI/CD integration
  - Version tracking and upgrade paths

- **Do NOT skip `--skip-interactive`** in automated environments. The command will hang waiting for user input.

- **Do NOT omit `--output console`** in automated environments. You need structured output to verify success.

### quickstart vs generate sdk

| Command | Creates workflow.yaml | Use case |
|---------|----------------------|----------|
| `speakeasy quickstart` | ✅ Yes | **New projects** - Always use this |
| `speakeasy generate sdk` | ❌ No | One-off generation (rare, advanced use only) |

**Always use `quickstart` for new SDK projects.** The workflow file it creates is essential for maintainable SDK development.

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Workflow already exists | `.speakeasy/workflow.yaml` already present | Run `speakeasy run` to regenerate the existing SDK instead |
| Unauthorized | Missing or invalid API key | Run `speakeasy auth login` or set `SPEAKEASY_API_KEY` |
| Schema not found | Invalid path, URL, or source name | Verify path exists or use `speakeasy pull --list` for sources |

## Related Skills

- `diagnose-generation-failure` - When generation fails
- `manage-openapi-overlays` - Customize spec with overlays
- `generate-sdk-for-python` - Python-specific configuration
- `generate-sdk-for-typescript` - TypeScript-specific configuration
- `generate-sdk-for-go` - Go-specific configuration
