---
name: skill-name
description: Use when [trigger condition]. Triggers on "[phrase 1]", "[phrase 2]", or "[phrase 3]"
license: Apache-2.0
---

# skill-name

[One-sentence summary of what this skill does and when to use it.]

## When to Use

- [Scenario 1 - describe the situation]
- [Scenario 2 - describe the situation]
- User says: "[trigger phrase example]"
- User asks: "[question example]"

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| [Input name] | Yes/No | [What it is and how to provide it] |
| [Another input] | Yes/No | [Description] |

## Outputs

| Output | Description |
|--------|-------------|
| [Output name] | [What gets produced] |
| [Another output] | [Description] |

## Prerequisites

[Any required setup before using this skill]

```bash
# Example: Set API key for non-interactive use
export SPEAKEASY_API_KEY="<your-api-key>"
```

See `configure-authentication` skill for details.

## Command

```bash
speakeasy [command] [required-args]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-s, --spec` | Path to OpenAPI spec | Required |
| `-o, --output` | Output path | `.` |

## Example

```bash
# [Description of what this example does]
speakeasy [command] -s ./openapi.yaml [other-args]
```

### Expected Output

```
[Example of what the command outputs]
```

## Decision Framework

Use this table to determine the appropriate action:

| Situation | Action | Rationale |
|-----------|--------|-----------|
| [Condition 1] | [What to do] | [Why] |
| [Condition 2] | [What to do] | [Why] |
| [Condition 3] | Ask the user | [Why user input needed] |

## What NOT to Do

- **Do NOT** [anti-pattern 1] - [why it's bad]
- **Do NOT** [anti-pattern 2] - [why it's bad]
- **Do NOT** proceed without user input on [specific case]

## Troubleshooting

### [Common Issue 1]

**Symptom:** [What the user sees]

**Cause:** [Why it happens]

**Fix:**
```bash
[Command or steps to fix]
```

### [Common Issue 2]

**Symptom:** [What the user sees]

**Fix:** [How to resolve]

## Related Skills

- `related-skill-1` - Use when [condition]
- `related-skill-2` - Use after this skill to [purpose]
