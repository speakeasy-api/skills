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

## Completed: Skill Parity & Consolidation (GEN-2368)

Achieved parity between granular skills and the `sdk-tf-generation-best-practices` meta-skill.

### Changes Made

**Consolidated (5 skills → 2):**
- `create-openapi-overlay` + `apply-openapi-overlay` + `fix-validation-errors-with-overlays` → `manage-openapi-overlays`
- `get-ai-suggestions` + `improve-operation-ids` → `improve-sdk-naming`

**New skills (6):**
- `generate-terraform-provider` — TF provider generation, CRUD mapping, publishing
- `extract-openapi-from-code` — Code-first OpenAPI extraction for 8 frameworks
- `customize-sdk-hooks` — SDK lifecycle hooks (user-agent, telemetry, HMAC auth)
- `setup-sdk-testing` — Contract testing, Arazzo workflows, integration tests
- `generate-mcp-server` — MCP server generation for AI assistant integration
- `customize-sdk-runtime` — Retries, timeouts, pagination, server selection, error handling

**Standalone:** All skills had cross-references removed and essential info inlined.

**Final count:** 11 skills + 1 meta-skill (was 16; removed 5 trivial CLI-wrapper skills)

### Trivial Skills Removed (HANDOFF.md cleanup)

Removed 5 skills that just wrapped single CLI commands discoverable via `--help`:
- `configure-authentication` — just `speakeasy auth login` or `export SPEAKEASY_API_KEY`
- `check-workspace-status` — just `speakeasy status --output json`
- `merge-openapi-specs` — just `speakeasy merge -s a -s b -o out`
- `regenerate-sdk` — just `speakeasy run`
- `validate-openapi-spec` — just `speakeasy lint openapi -s spec.yaml`

Essential info (auth commands, lint/run commands) was already inlined into remaining skills during Phase 3 standalone work.

## Future Enhancements (from consensus analysis)

Recommendations from PAL MCP consensus analysis on skill structure:

### Medium Priority

1. **Add formal parameter schemas** to skills (machine-readable)
2. **Add preconditions/postconditions** for predictable behavior
3. **Add idempotency flags** (safe to run multiple times?)

### Lower Priority

4. **Consider dual-layer structure**: machine-readable manifest + human-readable prose
5. **Evaluate tool-agnostic design** across different AI platforms

## Files to Reference

- `templates/SKILL.template.md` - Template for new skills
- `AGENTS.md` - Contributor guidance
- `CLAUDE.md` - Claude-specific guidance
- Existing skills in `skills/` as examples
