# Skill Evaluation Harness

Workspace-based evaluation framework for Speakeasy agent skills using the Claude Agent SDK.

## Overview

This harness evaluates skills by running real SDK generation workflows in isolated workspaces. Instead of just checking if the model outputs certain strings, it:

1. Creates an isolated workspace with an OpenAPI spec
2. Runs a Claude agent with skill context and Speakeasy CLI tools
3. Assesses the workspace state after the agent completes
4. Verifies actual SDK artifacts were created correctly

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- [Speakeasy CLI](https://www.speakeasyapi.dev/docs/speakeasy-cli/getting-started)
- `ANTHROPIC_API_KEY` environment variable

## Quick Start

```bash
cd evals
uv sync
export ANTHROPIC_API_KEY="your-key"

# Check environment
uv run skill-eval check

# List available tests
uv run skill-eval list

# Run all evaluations
uv run skill-eval run --suite all
```

## Test Suites

| Suite | Purpose |
|-------|---------|
| `generation` | Can skill guide successful SDK generation? |
| `overlay` | Does skill create valid overlays with expected extensions? |
| `diagnosis` | Does skill correctly identify spec issues? |
| `workflow` | Can skill complete multi-step generation workflows? |

## Usage

```bash
# Run specific suite
uv run skill-eval run --suite generation

# Filter by skill
uv run skill-eval run --skill start-new-sdk-project

# Filter by test name
uv run skill-eval run --test typescript

# Run single test with verbose output
uv run skill-eval single typescript-sdk-from-clean-spec -v

# Output JSON
uv run skill-eval run --suite all -o results.json

# Use different model
uv run skill-eval run --model claude-opus-4-20250514
```

## Adding Tests

### Fixtures

Add OpenAPI specs to `fixtures/`:

```yaml
# fixtures/my-api.yaml
openapi: 3.0.3
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: listUsers
      # ...
```

### Test Cases

Edit YAML files in `tests/`:

```yaml
# tests/generation.yaml
tests:
  - name: my-sdk-test
    skill: start-new-sdk-project
    type: generation
    target: typescript
    spec_file: fixtures/my-api.yaml
    task: |
      Generate a TypeScript SDK from the OpenAPI spec.

# tests/overlay.yaml
tests:
  - name: add-retries
    skill: configure-speakeasy-extensions
    type: overlay
    spec_file: fixtures/my-api.yaml
    task: Add retry configuration for 5XX errors.
    expected_extensions:
      - x-speakeasy-retries

# tests/workflow.yaml
tests:
  - name: full-workflow
    skill: start-new-sdk-project
    type: workflow
    spec_file: fixtures/my-api.yaml
    steps:
      - name: lint
        tool: speakeasy_lint
      - name: generate
        tool: speakeasy_quickstart
      - name: verify
        creates_file: .speakeasy/workflow.yaml
```

## Architecture

```
evals/
├── skill_eval/
│   ├── __main__.py     # CLI entry point
│   ├── runner.py       # Test orchestration
│   ├── evaluator.py    # Claude Agent SDK integration
│   ├── workspace.py    # Isolated workspace management
│   ├── cli.py          # Speakeasy CLI wrapper
│   ├── assessor.py     # Workspace state assessment
│   ├── assertions.py   # Output validation
│   └── reporter.py     # Results formatting
├── tests/              # Test definitions (YAML)
│   ├── generation.yaml
│   ├── overlay.yaml
│   ├── diagnosis.yaml
│   └── workflow.yaml
├── fixtures/           # Sample OpenAPI specs
│   ├── petstore-minimal.yaml
│   ├── petstore-poor-naming.yaml
│   └── paginated-api.yaml
└── pyproject.toml
```

## How It Works

1. **Workspace Creation**: Each test runs in an isolated temporary directory with the OpenAPI spec

2. **Agent Execution**: A Claude agent is created with:
   - Skill content as system prompt context
   - MCP tools for workspace file operations
   - MCP tools for Speakeasy CLI commands (quickstart, run, lint, suggest, overlay)

3. **State Assessment**: After the agent completes, the workspace is assessed:
   - Were expected files created?
   - Is the generated SDK valid for the target language?
   - Did overlays contain expected extensions?
   - Were expected tools called?

4. **Results Reporting**: Pass/fail with detailed checks and tool call logs

## Available MCP Tools

The agent has access to these workspace tools:

| Tool | Description |
|------|-------------|
| `read_file` | Read a file from the workspace |
| `write_file` | Write a file to the workspace |
| `list_files` | List files matching a glob pattern |
| `speakeasy_quickstart` | Initialize a new SDK project |
| `speakeasy_run` | Regenerate SDK from workflow |
| `speakeasy_lint` | Lint an OpenAPI spec |
| `speakeasy_suggest` | Generate AI-suggested operation IDs |
| `speakeasy_overlay_apply` | Apply an overlay to a spec |
| `speakeasy_overlay_validate` | Validate an overlay file |

## Development

```bash
# Install with dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Type checking
uv run mypy skill_eval
```
