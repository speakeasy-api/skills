# Pending Work

Captured from GEN-2353 session. Hand off to next agent.

## Open PRs

### This Repo (agent-skills)

- **PR #2**: Add contributor-focused docs and skill template
  - URL: https://github.com/speakeasy-api/agent-skills/pull/2
  - Status: Ready for review
  - Branch: `chore/enhance-contributor-docs`

### Speakeasy Repo

- **PR #1820**: Remove migrated Claude Code plugin (cleanup)
  - URL: https://github.com/speakeasy-api/speakeasy/pull/1820
  - Status: Ready for review
  - Branch: `chore/migrate-skills-to-dedicated-repo`
  - Removes `.claude-plugin/`, `plugins/claude-code/`, `skills/` directories
  - Updates README.md to point to this repo

## Linear Issue

- **GEN-2353**: Feature: Setup dedicated Speakeasy Agent Skills repo
  - Status: In Progress
  - Link to close when PRs are merged

## Future Enhancements (from consensus analysis)

Recommendations from PAL MCP consensus analysis on skill structure:

### High Priority

1. **Enhance skill descriptions** with more trigger phrases
2. **Add explicit Inputs/Outputs sections** to skills
3. **Standardize inter-skill links** (Related Skills sections)

### Medium Priority

4. **Add formal parameter schemas** to skills (machine-readable)
5. **Add preconditions/postconditions** for predictable behavior
6. **Add idempotency flags** (safe to run multiple times?)

### Lower Priority

7. **Consider dual-layer structure**: machine-readable manifest + human-readable prose
8. **Evaluate tool-agnostic design** across different AI platforms

## Files to Reference

- `templates/SKILL.template.md` - Template for new skills
- `AGENTS.md` - Contributor guidance
- `CLAUDE.md` - Claude-specific guidance
- Existing skills in `skills/` as examples
