# Skill Evaluation Harness

Automated evaluation framework for Speakeasy agent skills using the Anthropic SDK.

## Overview

This harness tests skill efficacy across four dimensions:
- **Activation**: Does the skill trigger on correct phrases?
- **Correctness**: Does output use valid Speakeasy syntax?
- **Completeness**: Are all required steps performed?
- **Hallucination**: Does it invent non-existent APIs?

## Installation

```bash
cd evals
pip install -e .
```

Requires `ANTHROPIC_API_KEY` environment variable.

## Usage

```bash
# Run all evaluations
python -m skill_eval run --suite all

# Run specific suite
python -m skill_eval run --suite activation
python -m skill_eval run --suite correctness

# Run for specific skill
python -m skill_eval run --skill configure-speakeasy-extensions

# Output results as JSON
python -m skill_eval run --suite all --output results.json

# Compare with/without skills
python -m skill_eval compare --suite correctness
```

## Test Case Format

Test cases are defined in YAML:

```yaml
# tests/activation.yaml
tests:
  - skill: configure-speakeasy-extensions
    should_activate:
      - "add retries to my SDK"
      - "configure x-speakeasy-pagination"
    should_not_activate:
      - "add retry logic"  # too generic
```

## Architecture

```
evals/
├── skill_eval/
│   ├── __init__.py
│   ├── __main__.py       # CLI entry point
│   ├── runner.py         # Test runner
│   ├── evaluator.py      # Anthropic SDK integration
│   ├── assertions.py     # Output validators
│   └── reporter.py       # Results formatting
├── tests/
│   ├── activation.yaml
│   ├── correctness.yaml
│   ├── completeness.yaml
│   └── hallucination.yaml
├── fixtures/
│   └── sample_specs/
└── pyproject.toml
```

## Extending

Add new test cases to the YAML files. The harness auto-discovers tests.

See `SKILL_EVALUATION_FRAMEWORK.md` for detailed methodology.
