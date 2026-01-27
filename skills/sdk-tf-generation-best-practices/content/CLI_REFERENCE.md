---
short_description: "Canonical Speakeasy CLI command reference"
long_description: |
  The authoritative source of truth for Speakeasy CLI commands. Agents MUST only
  use commands documented here. All commands verified against speakeasy v1.698.0.
---

# Speakeasy CLI Reference

This document contains the canonical CLI commands for Speakeasy. Agents should ONLY recommend commands listed here.

> **Note:** Commands verified against `speakeasy version 1.698.0`. Run `speakeasy --help` to check for updates.

---

## Installation

> **CHOOSE ONE** of the following installation methods:

### Option A: Homebrew (macOS)

```bash
brew install speakeasy-api/tap/speakeasy
```

### Option B: Script (macOS/Linux)

```bash
curl -fsSL https://go.speakeasy.com/cli-install.sh | sh
```

### Option C: Windows (winget)

```bash
winget install speakeasy
```

### Option D: Windows (Chocolatey)

```bash
choco install speakeasy
```

---

## Authentication

### Login

Authenticate with Speakeasy (opens browser for OAuth):

```bash
speakeasy auth login
```

### Logout

```bash
speakeasy auth logout
```

### Switch workspace

```bash
speakeasy auth switch
```

**Environment Variable Alternative:**

```bash
export SPEAKEASY_API_KEY="your-api-key"
```

---

## SDK Generation

### Quickstart

First-time SDK setup with guided wizard:

```bash
speakeasy quickstart
```

**With flags (non-interactive, for agents and automation):**

```bash
speakeasy quickstart --skip-interactive --output console \
  -s path/to/openapi.yaml \
  -t python \
  -o ./sdk-python
```

**Available flags:**
- `-s, --schema` - Local filepath, URL, or registry source (see [Schema Sources](#schema-sources))
- `-t, --target` - Generation target (see supported targets below)
- `-o, --out-dir` - Output directory
- `-n, --name` - SDK name (avoids interactive prompt)
- `-p, --package-name` - Package name (avoids interactive prompt)
- `--skip-interactive` - Skip browser auth and interactive prompts (requires `SPEAKEASY_API_KEY`)
- `--output console` - Structured output for agent/automation consumption
- `-f, --from` - Template from Speakeasy sandbox
- `--skip-compile` - Skip compilation after setup

**Supported targets:**
- `csharp`
- `go`
- `java`
- `mcp-typescript`
- `php`
- `postman`
- `python`
- `ruby`
- `terraform`
- `typescript`
- `unity`

### Schema Sources

The `-s, --schema` flag accepts multiple source formats:

| Format | Syntax | Example |
|--------|--------|---------|
| Local file | File path | `./api/openapi.yaml` |
| URL | HTTP(S) URL | `https://api.example.com/openapi.json` |
| Registry source | `source-name` | `my-api` |
| Registry source (tagged) | `source-name@tag` | `my-api@latest` |
| Registry source (fully qualified) | `org/workspace/source@tag` | `acme/prod/my-api@v2` |

### Run

Execute the workflow defined in `.speakeasy/workflow.yaml`:

```bash
speakeasy run
```

**Common flags (non-interactive):**

```bash
speakeasy run -y --output console \
  --target my-sdk \
  --skip-compile \
  --skip-versioning \
  --set-version 1.2.3
```

**All available flags:**
- `-y, --auto-yes` - Auto-accept all prompts (non-interactive)
- `--output console` - Structured output for agent/automation consumption
- `-t, --target` - Target to run (use 'all' for all targets)
- `-s, --source` - Source to run (use 'all' for all sources)
- `--skip-compile` - Skip compilation
- `--skip-versioning` - Skip automatic version increments
- `--skip-testing` - Skip testing after generation
- `--set-version` - Manual version to apply
- `--minimal` - Only run strictly necessary steps
- `-d, --debug` - Enable debug files with broken code
- `--github` - Kick off generation in GitHub
- `--github-repos` - Run across multiple repos ('all' or comma-separated URLs)

### Generate SDK

Direct generation without quickstart wizard:

```bash
speakeasy generate sdk \
  --schema path/to/openapi.yaml \
  --lang python \
  --out ./sdk-python
```

---

## OpenAPI Validation

### Validate/Lint Spec

Check OpenAPI spec for errors (validate and lint are aliases):

```bash
speakeasy lint openapi --non-interactive -s path/to/spec.yaml
```

or equivalently:

```bash
speakeasy validate openapi --non-interactive -s path/to/spec.yaml
```

**Available flags:**
- `--non-interactive` - Skip interactive prompts (recommended for agents/automation)
- `-s, --schema` - Path to the OpenAPI spec file
- `-H, --header` - Additional headers for remote spec URLs (can be repeated)

**Output:** Lists validation errors with line numbers and suggestions.

---

## Terraform Provider Generation

### Generate Provider

```bash
speakeasy generate sdk \
  --lang terraform \
  -s path/to/openapi.yaml \
  -o ./terraform-provider
```

> **Note:** There is no separate `speakeasy generate terraform` command. Use `generate sdk --lang terraform`.

**Prerequisites:**
- OpenAPI spec must have `x-speakeasy-entity` annotations
- See `speakeasy agent context terraform/crud-mapping` for annotation guide

---

## OpenAPI Transformation

Transform commands have subcommands for specific operations.

### Convert Swagger 2.0 to OpenAPI 3.x

```bash
speakeasy openapi transform convert-swagger \
  -s path/to/swagger2.yaml \
  -o path/to/openapi3.yaml
```

### Filter Operations

Filter spec to specific operations:

```bash
speakeasy openapi transform filter-operations \
  -s path/to/spec.yaml \
  --operations "listUsers,getUser,createUser" \
  -o filtered.yaml
```

### Remove Unused Components

```bash
speakeasy openapi transform remove-unused \
  -s path/to/spec.yaml \
  -o cleaned.yaml
```

### Format Spec

Make spec more human-readable:

```bash
speakeasy openapi transform format \
  -s path/to/spec.yaml \
  -o formatted.yaml
```

### Cleanup

Clean up formatting:

```bash
speakeasy openapi transform cleanup \
  -s path/to/spec.yaml \
  -o cleaned.yaml
```

### Normalize

Normalize document structure:

```bash
speakeasy openapi transform normalize \
  -s path/to/spec.yaml \
  -o normalized.yaml
```

---

## Merge Multiple Specs

Merge multiple OpenAPI documents (command is at root level, not under `openapi`):

```bash
speakeasy merge \
  -s spec1.yaml \
  -s spec2.yaml \
  -o merged.yaml
```

> **Note:** Duplicate operations/components are overwritten by later documents in the list.

---

## Overlay Management

Overlays allow declarative modifications to OpenAPI specs without editing the source.

### Apply Overlay

Apply an overlay to modify a spec:

```bash
speakeasy overlay apply \
  -s path/to/spec.yaml \
  -o path/to/overlay.yaml \
  --out modified-spec.yaml
```

### Validate Overlay

```bash
speakeasy overlay validate -o path/to/overlay.yaml
```

### Compare Specs

Compare two specs to generate an overlay:

```bash
speakeasy overlay compare \
  --before original.yaml \
  --after modified.yaml \
  --out changes.overlay.yaml
```

### Common Overlay Use Cases

- Add `x-speakeasy-*` annotations for SDK customization
- Fix validation errors in third-party specs
- Add missing operationIds
- Customize response types

---

## Configuration

Configure workflow file settings:

### Configure Sources

```bash
speakeasy configure sources
```

### Configure Targets

```bash
speakeasy configure targets
```

### Configure GitHub

```bash
speakeasy configure github
```

### Configure Publishing

```bash
speakeasy configure publishing
```

### Configure Tests

```bash
speakeasy configure tests
```

### Create Local Workflow

```bash
speakeasy configure local-workflow
```

---

## Testing

### Run Tests

Start mock API server and run tests for each workflow target:

```bash
speakeasy test
```

**Available flags:**

| Flag | Description |
|------|-------------|
| `--target <name>` | Run tests for a single target (default: all) |
| `--disable-mockserver` | Skip starting the mock API server |
| `--verbose` | Verbose output |

---

## Troubleshooting

### Version Check

```bash
speakeasy -v
```

or:

```bash
speakeasy --version
```

### Verbose Mode

Add `--logLevel` to any command for detailed output:

```bash
speakeasy run --logLevel info
```

Available log levels: `info`, `warn`, `error`

---

## Command Not Found?

If you need a CLI command that is not listed here:

1. Check `speakeasy --help` for the latest commands
2. Check `speakeasy <command> --help` for subcommands
3. If the command exists but is not documented here, add it
4. If the command does not exist, do NOT invent it
5. Use `TODO: CLI_COMMAND` marker and describe the intended action

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Generate SDK | `speakeasy quickstart --skip-interactive --output console -s spec.yaml -t python -o ./sdk` |
| Regenerate SDK | `speakeasy run -y --output console` |
| Run specific target | `speakeasy run -y --output console --target my-sdk` |
| Validate spec | `speakeasy lint openapi --non-interactive -s spec.yaml` |
| Convert Swagger | `speakeasy openapi transform convert-swagger -s old.yaml -o new.yaml` |
| Merge specs | `speakeasy merge -s spec1.yaml -s spec2.yaml -o merged.yaml` |
| Apply overlay | `speakeasy overlay apply -s spec.yaml -o overlay.yaml --out modified.yaml` |
| Run tests | `speakeasy test` |
| Check version | `speakeasy -v` |
| Login | `speakeasy auth login` |
