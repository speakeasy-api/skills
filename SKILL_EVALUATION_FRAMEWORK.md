# Skill Evaluation Framework

Inspired by [Vercel's agents.md evaluation methodology](https://vercel.com/blog/agents-md-outperforms-skills-md-in-our-agent-evals), this framework measures Speakeasy skill efficacy using behavioral assertions rather than implementation details.

## Core Principles

1. **Behavioral over Implementation** - Test what the agent *does*, not how it does it
2. **Unknown Knowledge Focus** - Target Speakeasy-specific knowledge not in model training data
3. **Pass Rate Metrics** - Build, Lint, Test dimensions
4. **Hardened Test Suite** - Remove leakage, resolve contradictions

## Evaluation Dimensions

| Dimension | What It Measures | How to Test |
|-----------|------------------|-------------|
| **Activation** | Does the skill trigger on correct phrases? | Prompt → skill selection accuracy |
| **Correctness** | Does output match expected behavior? | Generated code/config validation |
| **Completeness** | Are all required steps performed? | Checklist completion rate |
| **No Hallucination** | Does it use real Speakeasy APIs/extensions? | Static analysis of generated content |

## Test Case Structure

### 1. Activation Tests

Test that skills activate on expected trigger phrases and don't activate on similar but incorrect phrases.

```yaml
# skill_activation_tests.yaml
tests:
  - skill: configure-speakeasy-extensions
    should_activate:
      - "add retries to my SDK"
      - "configure x-speakeasy-pagination"
      - "make enums open"
      - "add global headers to SDK"
    should_not_activate:
      - "add retry logic to my code"  # Generic, not Speakeasy-specific
      - "configure pagination"         # Too generic
      - "add headers"                   # Too generic

  - skill: generate-terraform-provider
    should_activate:
      - "generate terraform provider from spec"
      - "add x-speakeasy-entity annotations"
      - "map CRUD operations for terraform"
    should_not_activate:
      - "write terraform config"        # Using TF, not generating provider
      - "create terraform module"       # Not provider generation

  - skill: extract-openapi-from-code
    should_activate:
      - "extract OpenAPI from FastAPI"
      - "generate spec from Django"
      - "code first OpenAPI"
    should_not_activate:
      - "write OpenAPI spec"            # Authoring, not extracting
      - "validate OpenAPI"              # Different skill
```

### 2. Correctness Tests

Test that generated content uses correct Speakeasy-specific syntax.

```yaml
# skill_correctness_tests.yaml
tests:
  - skill: configure-speakeasy-extensions
    prompt: "Add retry configuration to GET /users endpoint"
    assertions:
      - type: contains
        target: output
        value: "x-speakeasy-retries"
      - type: valid_yaml
        target: output
      - type: schema_valid
        target: output
        schema: speakeasy_retries_schema

  - skill: generate-terraform-provider
    prompt: "Annotate Pet schema for Terraform"
    assertions:
      - type: contains
        target: output
        value: "x-speakeasy-entity: Pet"
      - type: contains
        target: output
        value: "x-speakeasy-entity-operation"
      - type: not_contains
        target: output
        value: "#list"  # Invalid operation type

  - skill: extract-openapi-from-code
    prompt: "Extract OpenAPI from this FastAPI app"
    context:
      file: sample_fastapi_app.py
    assertions:
      - type: contains
        target: output
        value: "app.openapi()"
      - type: contains
        target: output
        value: "speakeasy lint"
```

### 3. Completeness Tests

Test that skills perform all required steps.

```yaml
# skill_completeness_tests.yaml
tests:
  - skill: generate-terraform-provider
    prompt: "Set up a new Terraform provider for my API"
    required_steps:
      - "Add x-speakeasy-entity to schemas"
      - "Add x-speakeasy-entity-operation to CRUD endpoints"
      - "Run speakeasy quickstart with -t terraform"
      - "Build with go build"
    optional_steps:
      - "Configure GPG signing"
      - "Set up release workflow"

  - skill: configure-speakeasy-extensions
    prompt: "Make all enums in my spec open"
    required_steps:
      - "Create overlay file"
      - "Target $..[?length(@.enum) > 1]"
      - "Add x-speakeasy-unknown-values: allow"
      - "Add overlay to workflow.yaml"
```

### 4. Hallucination Tests

Test that skills don't invent non-existent APIs or extensions.

```yaml
# skill_hallucination_tests.yaml
valid_extensions:
  - x-speakeasy-retries
  - x-speakeasy-pagination
  - x-speakeasy-name-override
  - x-speakeasy-group
  - x-speakeasy-entity
  - x-speakeasy-entity-operation
  - x-speakeasy-unknown-values
  - x-speakeasy-globals
  - x-speakeasy-custom-security-scheme
  - x-speakeasy-ignore
  - x-speakeasy-usage-example

valid_cli_commands:
  - speakeasy quickstart
  - speakeasy run
  - speakeasy lint openapi
  - speakeasy overlay apply
  - speakeasy overlay validate
  - speakeasy overlay compare
  - speakeasy suggest operation-ids
  - speakeasy auth login

tests:
  - skill: configure-speakeasy-extensions
    prompts:
      - "Add caching to my SDK"
      - "Configure rate limiting"
    assertions:
      - type: no_invalid_extensions
        valid_list: valid_extensions
      - type: no_invalid_commands
        valid_list: valid_cli_commands
```

## Metrics

### Pass Rate Calculation

```
Activation Pass Rate = (correct_activations + correct_non_activations) / total_activation_tests
Correctness Pass Rate = passed_correctness_tests / total_correctness_tests
Completeness Pass Rate = avg(steps_completed / required_steps) across tests
Hallucination Rate = tests_with_hallucinations / total_tests
```

### Target Metrics

| Metric | Target | Acceptable |
|--------|--------|------------|
| Activation Pass Rate | >95% | >90% |
| Correctness Pass Rate | >90% | >85% |
| Completeness Pass Rate | >85% | >80% |
| Hallucination Rate | <5% | <10% |

## Test Data Requirements

### Speakeasy-Specific Knowledge (Not in Training Data)

Focus tests on Speakeasy-specific content that models wouldn't know from general training:

| Category | Examples |
|----------|----------|
| **Extensions** | `x-speakeasy-unknown-values`, `x-speakeasy-globals`, custom security schemes |
| **Overlay Recipes** | Open all enums pattern, global headers pattern |
| **CLI Commands** | `speakeasy overlay compare`, `speakeasy suggest operation-ids` |
| **Config Files** | `gen.yaml` structure, `workflow.yaml` sources/targets |
| **Terraform** | Entity operation syntax, type inference rules |

### Sample Test Fixtures

```
fixtures/
├── sample_openapi_specs/
│   ├── minimal.yaml
│   ├── with_enums.yaml
│   └── needs_annotations.yaml
├── sample_code/
│   ├── fastapi_app.py
│   ├── django_settings.py
│   └── spring_boot_controller.java
└── expected_outputs/
    ├── retries_overlay.yaml
    ├── open_enums_overlay.yaml
    └── terraform_annotated.yaml
```

## Running Evaluations

### Manual Evaluation

1. Present prompt to Claude with skill loaded
2. Capture output
3. Run assertions against output
4. Record pass/fail and any hallucinations

### Automated Evaluation (Future)

```bash
# Proposed CLI
speakeasy skills eval --suite activation
speakeasy skills eval --suite correctness
speakeasy skills eval --suite all --output results.json
```

## Iteration Process

1. **Baseline** - Run eval suite, record metrics
2. **Identify Failures** - Categorize why tests fail (activation, correctness, completeness, hallucination)
3. **Improve Skills** - Update trigger phrases, add examples, clarify instructions
4. **Re-evaluate** - Run suite again, compare to baseline
5. **Harden Tests** - Remove test leakage, resolve contradictions

## Comparison: Skills vs No Skills

Run evaluation suite with:
1. **Skills loaded** - Full skill context available
2. **No skills** - Base model only

This measures the delta that skills provide for Speakeasy-specific tasks.

| Test Category | No Skills | With Skills | Delta |
|---------------|-----------|-------------|-------|
| Activation | N/A | 95% | - |
| Correctness | 40% | 92% | +52% |
| Completeness | 30% | 88% | +58% |
| Hallucination | 25% | 3% | -22% |

## Related Files

- `templates/SKILL.template.md` - Skill authoring template
- `CLAUDE.md` - Skill design principles
- `META_SKILL_DECOMPOSITION_PLAN.md` - Decomposition strategy
