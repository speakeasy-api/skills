# CLAUDE.md

Claude-specific instructions for working on the Speakeasy Agent Skills repository.

## Quick Reference

```bash
# Create a new skill
mkdir skills/{skill-name}
# Then create skills/{skill-name}/SKILL.md using the template

# Test a skill locally
cp -r skills/{skill-name} ~/.claude/skills/

# Validate skill format
npx skills validate ./skills/{skill-name}
```

## Working on This Repository

### Creating a New Skill

1. **Create directory**: `mkdir skills/{skill-name}` (use kebab-case)
2. **Copy template**: `cp templates/SKILL.template.md skills/{skill-name}/SKILL.md`
3. **Edit the skill**: Update frontmatter `name` and `description`, fill in sections
4. **Reference existing skills** in `skills/` for examples of the pattern

### Modifying Existing Skills

1. **Read the skill first** - Understand current behavior before changing
2. **Preserve frontmatter** - `name` and `description` are required
3. **Check related skills** - Changes may affect linked skills
4. **Keep under 500 lines** - Large skills waste context

### Running Speakeasy Commands

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
- Decision Framework table
- Anti-Patterns section
- Related Skills links

## Plugin Configuration

### Namespace

All skills are namespaced under `speakeasy:` via `.claude-plugin/plugin.json`:

```json
{
  "name": "speakeasy",
  "skills": "../skills/"
}
```

Skills appear as `speakeasy:skill-name` in Claude Code.

### Adding Skills

Skills are auto-discovered. Just create the directory and SKILL.md.

## Testing Skills

### Local Testing

```bash
# Copy to Claude's skills directory
cp -r skills/{skill-name} ~/.claude/skills/

# Reload Claude Code and test trigger phrases
```

### Validation

```bash
npx skills validate ./skills/{skill-name}
```

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

## File Reference

| File | Purpose |
|------|---------|
| `skills/*/SKILL.md` | Skill definitions |
| `templates/SKILL.template.md` | Template for new skills |
| `.claude-plugin/plugin.json` | Plugin manifest (namespace) |
| `README.md` | End-user documentation |
| `AGENTS.md` | General agent guidance |
| `CLAUDE.md` | This file |
