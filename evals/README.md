# Skill Evaluation Harness

Workspace-based evaluation framework for Speakeasy agent skills using the Claude Agent SDK.

## Overview

This harness evaluates skills by running real SDK generation workflows in isolated workspaces using the SDK's native skill loading mechanism. It:

1. Creates an isolated workspace with an OpenAPI spec
2. Copies the skill being tested to the workspace's `.claude/skills/` directory
3. Runs a Claude agent with `setting_sources=["project"]` to discover the skill
4. Lets Claude autonomously invoke the skill when relevant
5. Assesses the workspace state after the agent completes

This matches how skills work in Claude Code - skills are discovered from the filesystem and Claude decides when to invoke them based on the task.

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
        command: speakeasy lint
      - name: generate
        command: speakeasy quickstart
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

1. **Workspace Setup**: Creates an isolated temp directory with:
   - The OpenAPI spec at `openapi.yaml`
   - The skill copied to `.claude/skills/{skill-name}/SKILL.md`

2. **Agent Configuration**: Runs with:
   ```python
   ClaudeAgentOptions(
       cwd=workspace_dir,
       setting_sources=["project"],  # Load skills from .claude/skills/
       allowed_tools=["Skill", "Bash", "Read", "Write", "Glob", "Grep"],
       permission_mode="bypassPermissions",
   )
   ```

3. **Skill Discovery**: The SDK discovers skills from `.claude/skills/` at startup, just like Claude Code does

4. **Autonomous Invocation**: Claude decides when to invoke the skill based on:
   - The skill's `description` field (trigger phrases)
   - The task being performed

5. **State Assessment**: After completion, verifies:
   - Were expected files created?
   - Is the generated SDK valid?
   - Did overlays contain expected extensions?
   - Was the skill actually invoked?

## What This Tests

The evaluation measures whether skills effectively:

1. **Activate correctly** - Does Claude invoke the skill for relevant tasks?
2. **Guide CLI usage** - Does the agent use correct speakeasy commands?
3. **Produce valid output** - Are generated SDKs/overlays structurally correct?
4. **Complete workflows** - Can multi-step tasks be completed successfully?

Results include `skill_invoked: true/false` to track whether skills are being triggered.

## Development

```bash
# Install with dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Type checking
uv run mypy skill_eval
```
