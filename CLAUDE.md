# CLAUDE.md

Claude-specific instructions for working on the Speakeasy Agent Skills repository.

## Quick Reference

```bash
# Create a new skill
mkdir skills/{skill-name}
cp templates/SKILL.template.md skills/{skill-name}/SKILL.md

# Test a skill locally
cp -r skills/{skill-name} ~/.claude/skills/

# Reload Claude Code and test trigger phrases
```

## Repository Structure

```
speakeasy-api/skills/
├── .claude-plugin/          # Claude Code plugin configuration
│   ├── plugin.json          # Plugin manifest (namespace: "speakeasy")
│   └── marketplace.json     # Marketplace metadata
├── skills/                  # Skill definitions
│   └── {skill-name}/
│       └── SKILL.md         # Skill instructions
├── templates/               # Skill templates
│   └── SKILL.template.md    # Template for new skills
├── AGENTS.md                # General agent guidance
├── CLAUDE.md                # This file (Claude-specific guidance)
├── README.md                # End-user documentation
└── LICENSE                  # Apache-2.0
```

## Creating a New Skill

### 1. Directory Structure

```bash
mkdir skills/{skill-name}
```

Use `kebab-case` for directory names (e.g., `validate-openapi-spec`).

### 2. SKILL.md Format

Every skill must have a `SKILL.md` file with YAML frontmatter. See `templates/SKILL.template.md` for a complete example.

**Required structure:**

```yaml
---
name: skill-name
description: Use when [trigger condition]. Triggers on "X", "Y", or "Z".
license: Apache-2.0
---
```

> **Spec Reference**: Skills follow the [agentskills.io specification](https://agentskills.io/specification).

**Required sections:**

| Section | Purpose |
|---------|---------|
| `# skill-name` | Title matching the directory name |
| `## When to Use` | Trigger scenarios and example phrases |
| `## Inputs` | Table of required/optional inputs |
| `## Outputs` | Table of what the skill produces |
| `## Command` | The speakeasy command to run |
| `## Example` | Working example with explanation |

**Recommended sections:**

| Section | Purpose |
|---------|---------|
| `## Prerequisites` | Required setup, env vars, dependencies |
| `## Decision Framework` | Table mapping situations to actions |
| `## What NOT to Do` | Anti-patterns the AI should avoid |
| `## Troubleshooting` | Common errors and solutions |
| `## Related Skills` | Links to related skills (always last) |

### agentskills.io Spec Compliance

Our skills follow the [agentskills.io specification](https://agentskills.io/specification). Key constraints:

| Field | Constraint |
|-------|------------|
| `name` | Max 64 chars, lowercase + hyphens only, must match directory name |
| `description` | Max 1024 chars, describe what AND when to use (include trigger phrases here) |
| `license` | Simple string (we use `Apache-2.0`) |
| `metadata` | String keys to string values only (no arrays) |
| `compatibility` | Plain string, max 500 chars (optional) |
| Body content | No format restrictions, keep under 500 lines |

**Note**: Trigger phrases belong in the `description` field, not in `metadata` (which only supports string values, not arrays).

**Standard section order:**

```
1. Frontmatter (name, description)
2. # Title
3. Intro paragraph
4. ## When to Use
5. ## Inputs
6. ## Outputs
7. ## Prerequisites (if needed)
8. ## Command
9. ## Example
10. ... other content sections ...
11. ## Decision Framework (if needed)
12. ## What NOT to Do (if needed)
13. ## Troubleshooting (if needed)
14. ## Related Skills (always last)
```

### 3. Naming Conventions

- **Directory**: `kebab-case` (e.g., `start-new-sdk-project`)
- **SKILL.md**: Always uppercase, exact filename
- **Frontmatter `name`**: Must match directory name exactly

## Skill Design Principles

### Context Efficiency

Skills are loaded on-demand. Only the name and description are loaded at startup; full SKILL.md loads when activated.

- **Keep SKILL.md under 500 lines** - Large files waste context
- **Write specific descriptions** - Include trigger phrases for better activation
- **Use progressive disclosure** - Reference supporting files for details
- **Prefer commands over inline code** - Command output is smaller than code

### Speakeasy CLI Patterns

Skills for the Speakeasy CLI should follow these patterns:

1. **Always include `--output console`** for structured, parseable output
2. **Pipe large output** to reduce context: `speakeasy run 2>&1 | tail -50`
3. **Reference the Decision Framework** for issue categorization
4. **Link to related skills** when appropriate

### Decision Framework Integration

All diagnostic and fix skills should use this escalation path:

| Issue Type | Action | Example |
|------------|--------|---------|
| Naming issues | Fix with overlays | Bad operationIds, missing descriptions |
| Structural issues | Ask the user | Invalid `$ref`, missing schemas |
| Design issues | Produce strategy document | Authentication, API restructuring |

### Anti-Patterns for Skills

Document what the AI should **not** do:

```markdown
## What NOT to Do

- **Do NOT** modify source OpenAPI specs directly
- **Do NOT** disable lint rules to hide errors
- **Do NOT** assume you can fix structural problems
- **Do NOT** proceed without user input on design decisions
```

## Modifying Existing Skills

When modifying skills:

1. **Read the skill first** - Understand current behavior before changing
2. **Preserve the frontmatter format** - Name and description are required
3. **Maintain backward compatibility** - Don't change skill behavior unexpectedly
4. **Update related skills** if behavior changes affect them
5. **Keep under 500 lines** - Large skills waste context

## Running Speakeasy Commands

When testing or demonstrating commands:

```bash
# Use --output console for structured output
speakeasy run --output console

# Pipe large output to reduce context
speakeasy lint openapi -s spec.yaml 2>&1 | tail -50

# Filter for errors only
speakeasy lint openapi -s spec.yaml 2>&1 | grep -E "(error|warning)"
```

## Skill Writing Guidelines

### Description Field

The `description` in frontmatter is critical for skill activation. Include:

- **Trigger condition**: "Use when X"
- **Trigger phrases**: Exact phrases users might say
- **Keywords**: Terms that should activate this skill

**Good example** - see `skills/diagnose-generation-failure/SKILL.md`

**Bad**: `description: Helps with generation issues` (too vague, no trigger phrases)

### Template Sections

See `templates/SKILL.template.md` for the complete structure including:
- Inputs/Outputs tables
- Decision Framework table
- What NOT to Do section
- Troubleshooting section
- Related Skills links

## Common Speakeasy Commands

Reference for skill authors:

| Command | Purpose |
|---------|---------|
| `speakeasy quickstart -s <spec> -t <target>` | Initialize new project |
| `speakeasy run` | Generate SDK from workflow |
| `speakeasy run --output console` | Generate with structured output |
| `speakeasy lint openapi --non-interactive -s <spec>` | Validate OpenAPI spec |
| `speakeasy suggest operation-ids -s <spec>` | AI suggestions for operation IDs |
| `speakeasy overlay apply -s <spec> -o <overlay>` | Apply overlay to spec |
| `speakeasy overlay validate -o <overlay>` | Validate overlay file |
| `speakeasy merge -s <spec1> -s <spec2> -o <output>` | Merge multiple specs |
| `speakeasy pull --list --format json` | List registry sources |

## Plugin Configuration

### Namespace

All skills are namespaced under `speakeasy:` via `.claude-plugin/plugin.json`:

```json
{
  "name": "speakeasy",
  "version": "1.0.0",
  "description": "SDK generation and OpenAPI tooling with Speakeasy CLI",
  "skills": "../skills/"
}
```

Skills appear as `speakeasy:skill-name` in Claude Code.

### Adding Skills

Skills are auto-discovered from the `skills/` directory. Just create the directory and SKILL.md file.

## Testing Skills

### Local Testing

```bash
# Copy to Claude's skills directory
cp -r skills/{skill-name} ~/.claude/skills/

# Reload Claude Code and test trigger phrases
```

### Validation

Manual validation checklist:
1. Frontmatter has `name` and `description` fields
2. Description includes trigger phrases ("Use when...")
3. Commands match actual CLI (`speakeasy <command> --help` to verify)
4. Related skills links are valid

## Common Tasks

### Add a new skill for a speakeasy command

1. Check if a related skill exists
2. Create `skills/{command-name}/SKILL.md`
3. Follow the template structure
4. Include trigger phrases in description
5. Add decision framework if diagnostic
6. Update README.md skill table

### Update an existing skill

1. Read the current skill
2. Make minimal changes
3. Preserve frontmatter format
4. Check for breaking changes to related skills

### Fix a skill that isn't triggering

1. Check the `description` field has trigger phrases
2. Ensure phrases match how users ask
3. Add more keyword variations
4. Test with actual trigger phrases

## Commit Guidelines

```bash
# Create a branch first
git checkout -b feat/add-new-skill

# Commit with clear message
git commit -m "Add skill for [purpose]

- Created skills/{name}/SKILL.md
- Added trigger phrases for [scenarios]
- Linked to related skills"

# Push and create PR
git push -u origin feat/add-new-skill
```

## PR Guidelines

When submitting changes:

1. **Create a branch** - Don't push directly to master
2. **Write clear commit messages** - Describe what changed and why
3. **Update README.md** if adding new skills
4. **Test before submitting** - Verify skills work as expected

## File Reference

| File | Purpose |
|------|---------|
| `skills/*/SKILL.md` | Skill definitions |
| `templates/SKILL.template.md` | Template for new skills |
| `.claude-plugin/plugin.json` | Plugin manifest (namespace) |
| `README.md` | End-user documentation |
| `AGENTS.md` | General agent guidance |
| `CLAUDE.md` | This file |
