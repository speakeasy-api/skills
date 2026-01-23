---
name: start-new-sdk-project
description: Use when you have an OpenAPI spec and want to generate an SDK, or asking "how do I get started with Speakeasy"
---

# start-new-sdk-project

Use `speakeasy quickstart` to initialize a new project with a workflow configuration.

## Prerequisites

For non-interactive environments (CI/CD, AI agents), set:
```bash
export SPEAKEASY_API_KEY="<your-api-key>"
```
See `configure-authentication` skill for details.

## Command

```bash
speakeasy quickstart --skip-interactive -s <schema> -t <target> -n <name> -p <package-name>
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--skip-interactive` | | **Required for AI agents.** Skips all prompts |
| `--schema` | `-s` | OpenAPI spec: local file, URL, or registry (`namespace` or `org/workspace/namespace@tag`) |
| `--target` | `-t` | Target language (see Supported Targets) |
| `--name` | `-n` | SDK name in PascalCase (e.g., `MyCompanySDK`) |
| `--package-name` | `-p` | Package name (language variants auto-inferred) |
| `--out-dir` | `-o` | Output directory (default: current dir) |
| `--init-git` | | Initialize git repo (omit to skip in non-interactive mode) |

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
# Non-interactive mode (recommended for AI agents)
speakeasy quickstart --skip-interactive \
  -s ./api/openapi.yaml \
  -t typescript \
  -n "AcmeSDK" \
  -p "acme-sdk"

# With custom output directory and git init
speakeasy quickstart --skip-interactive \
  -s ./api/openapi.yaml \
  -t python \
  -n "AcmeSDK" \
  -p "acme-sdk" \
  -o ./sdks/python \
  --init-git

# Using registry schema
speakeasy quickstart --skip-interactive \
  -s "my-namespace@latest" \
  -t go \
  -n "AcmeSDK" \
  -p "acme-sdk"
```

## What It Creates

1. **Workflow configuration**: `.speakeasy/workflow.yaml`
2. **Generated SDK**: Full SDK in the output directory, ready to use

## Next Steps After Quickstart

1. Review the generated SDK in the output directory
2. Add more targets to `.speakeasy/workflow.yaml` for multi-language support
3. Run `speakeasy run` to regenerate after spec or config changes
