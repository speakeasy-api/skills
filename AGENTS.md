# AGENTS.md

This file provides guidance for AI coding agents working on the Speakeasy Agent Skills repository. It covers how to create, maintain, and improve skills for the Speakeasy CLI.

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
├── AGENTS.md                # This file (contributor guidance)
├── CLAUDE.md                # Claude-specific contributor guidance
├── README.md                # End-user documentation
└── LICENSE                  # Apache-2.0
```

## Creating a New Skill

### 1. Directory Structure

```bash
mkdir skills/{skill-name}
```

Use `kebab-case` for directory names (e.g., `manage-openapi-overlays`).

### 2. SKILL.md Format

Every skill must have a `SKILL.md` file with YAML frontmatter. See `templates/SKILL.template.md` for a complete example.

**Required structure:**

```yaml
---
name: skill-name
description: Use when [trigger condition]. Include phrases like "X", "Y", or "Z".
---
```

**Required sections:**

| Section | Purpose |
|---------|---------|
| `# skill-name` | Title matching the directory name |
| `## When to Use` | Trigger scenarios and example phrases |
| `## Command` | The speakeasy command to run |
| `## Example` | Working example with explanation |

**Recommended sections:**

| Section | Purpose |
|---------|---------|
| `## Prerequisites` | Required setup, env vars, dependencies |
| `## Decision Framework` | Table mapping situations to actions |
| `## What NOT to Do` | Anti-patterns the AI should avoid |
| `## Related Skills` | Links to related skills |

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

## Updating Existing Skills

When modifying skills:

1. **Preserve the frontmatter format** - Name and description are required
2. **Maintain backward compatibility** - Don't change skill behavior unexpectedly
3. **Update related skills** if behavior changes affect them
4. **Test with multiple agents** - Claude Code, Cursor, Copilot if possible

## Testing Skills

### Manual Testing

1. Install the skill locally:
   ```bash
   cp -r skills/{skill-name} ~/.claude/skills/
   ```

2. Test trigger phrases work as expected
3. Verify command output is parseable

### Validation

Use the AgentSkills validator if available:
```bash
npx skills validate ./skills/{skill-name}
```

## Common Speakeasy Commands

Reference for skill authors:

| Command | Purpose |
|---------|---------|
| `speakeasy quickstart -s <spec> -t <target>` | Initialize new project |
| `speakeasy run` | Generate SDK from workflow |
| `speakeasy run --output console` | Generate with structured output |
| `speakeasy lint openapi -s <spec>` | Validate OpenAPI spec |
| `speakeasy suggest operation-ids -s <spec>` | AI suggestions for operation IDs |
| `speakeasy overlay apply -s <spec> -o <overlay>` | Apply overlay to spec |
| `speakeasy overlay validate -o <overlay>` | Validate overlay file |
| `speakeasy merge -s <specs...> -o <output>` | Merge multiple specs |

## Plugin Configuration

### plugin.json

```json
{
  "name": "speakeasy",
  "version": "1.0.0",
  "description": "SDK generation and OpenAPI tooling with Speakeasy CLI",
  "skills": "../skills/"
}
```

The `name` field sets the namespace prefix for all skills (e.g., `speakeasy:start-new-sdk-project`).

### Adding a New Skill to the Plugin

Skills are auto-discovered from the `skills/` directory. Just create the directory and SKILL.md file.

## PR Guidelines

When submitting changes:

1. **Create a branch** - Don't push directly to master
2. **Write clear commit messages** - Describe what changed and why
3. **Update README.md** if adding new skills
4. **Test before submitting** - Verify skills work as expected
