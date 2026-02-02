# Skill Evaluation Harness

Automated evaluation framework for Speakeasy agent skills using the Claude Agent SDK.

## Quick Start

```bash
cd evals
uv sync
export ANTHROPIC_API_KEY="your-key"

# Run all evaluations
uv run skill-eval run --suite all

# Compare with/without skills
uv run skill-eval compare --suite correctness
```

## Test Suites

| Suite | Purpose |
|-------|---------|
| `activation` | Does skill trigger on correct phrases? |
| `correctness` | Does output use valid Speakeasy syntax? |
| `completeness` | Are all required steps performed? |
| `hallucination` | Does it invent non-existent APIs? |

## Usage

```bash
# Run specific suite
uv run skill-eval run --suite correctness

# Filter by skill
uv run skill-eval run --skill configure-speakeasy-extensions

# Output JSON
uv run skill-eval run --suite all -o results.json

# Use different model
uv run skill-eval run --suite all --model claude-opus-4-20250514

# List available tests
uv run skill-eval list
```

## Adding Tests

Edit YAML files in `tests/`:

```yaml
# tests/correctness.yaml
tests:
  - skill: configure-speakeasy-extensions
    prompt: "Add retry configuration to GET /users"
    assertions:
      - type: contains
        value: "x-speakeasy-retries"
      - type: valid_yaml
```

## Architecture

```
evals/
├── skill_eval/           # Python package
│   ├── __main__.py       # CLI
│   ├── runner.py         # Test runner
│   ├── evaluator.py      # Claude Agent SDK integration
│   ├── assertions.py     # Output validators
│   └── reporter.py       # Results formatting
├── tests/                # Test definitions
│   ├── activation.yaml
│   ├── correctness.yaml
│   ├── completeness.yaml
│   └── hallucination.yaml
└── pyproject.toml
```
