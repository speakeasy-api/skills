# Handoff: Remove Trivial Skills

## Context

PR #10 (`feat/skill-parity-gen-2368`) consolidated and expanded skills from 13 to 16. On review, 5 of the remaining granular skills are too trivial — they wrap a single CLI command that an AI can discover from `speakeasy <command> --help`. Skills should provide guidance an AI doesn't already have or can't easily infer.

## Skills to Remove (5)

| Skill | Why trivial |
|-------|------------|
| `configure-authentication` | Just `speakeasy auth login` or `export SPEAKEASY_API_KEY`. Any AI figures this out from `--help` or error messages. |
| `check-workspace-status` | One command: `speakeasy status --output json`. Self-explanatory. |
| `merge-openapi-specs` | One command: `speakeasy merge -s a -s b -o out`. The `--help` output covers it. |
| `regenerate-sdk` | One command: `speakeasy run`. The flags are all discoverable. |
| `validate-openapi-spec` | One command: `speakeasy lint openapi -s spec.yaml`. The output itself categorizes errors/warnings/hints. |

## Skills to Keep (11)

| Skill | Why valuable |
|-------|------------|
| `start-new-sdk-project` | Entry point skill. Documents registry source syntax (`org/workspace/source@tag`), `--skip-interactive` for agents, supported targets. Borderline but worth keeping as the "front door". |
| `diagnose-generation-failure` | Decision framework (overlay-fixable vs spec-fix vs ask-user) that can't be inferred from CLI help. |
| `writing-openapi-specs` | Speakeasy-specific best practices for codegen-friendly specs. Not discoverable from CLI. |
| `manage-openapi-overlays` | Overlay format, JSONPath targeting, `x-speakeasy-*` extensions — proprietary knowledge. |
| `improve-sdk-naming` | `x-speakeasy-group`/`x-speakeasy-name-override` extensions + suggest commands. |
| `generate-terraform-provider` | Entity annotations, CRUD mapping — complex proprietary workflow. |
| `extract-openapi-from-code` | 8 framework-specific extraction methods. |
| `customize-sdk-hooks` | Hook types, registration patterns, preserved files. |
| `setup-sdk-testing` | Arazzo format, contract testing, mock server. |
| `generate-mcp-server` | MCP overlays, scopes, deployment patterns. |
| `customize-sdk-runtime` | `x-speakeasy-retries`, `x-speakeasy-timeout`, `x-speakeasy-pagination`. |

## What to Do

### 1. Delete the 5 skill directories

```bash
rm -rf skills/configure-authentication
rm -rf skills/check-workspace-status
rm -rf skills/merge-openapi-specs
rm -rf skills/regenerate-sdk
rm -rf skills/validate-openapi-spec
```

### 2. Inline essential info from deleted skills into remaining skills

The deleted skills contained some useful snippets that other skills previously referenced. These were already inlined during the Phase 3 standalone work (PR #10), so most references are already handled. Double-check that no remaining skill references the deleted skill names.

Key info to preserve (already inlined in most places):
- **Auth**: `speakeasy auth login` or `export SPEAKEASY_API_KEY="<key>"` — appears in Prerequisites sections of skills that need it
- **Lint command**: `speakeasy lint openapi --non-interactive -s <spec>` — appears in `diagnose-generation-failure` and post-extraction steps in `extract-openapi-from-code`
- **Run command**: `speakeasy run --output console` — appears in multiple skills already

### 3. Update README.md

Remove these rows from the skill table:
- `speakeasy:configure-authentication`
- `speakeasy:check-workspace-status`
- `speakeasy:merge-openapi-specs`
- `speakeasy:regenerate-sdk`
- `speakeasy:validate-openapi-spec`

Update the directory count from 16 to 11.

### 4. Update meta-skill Related Skills section

In `skills/sdk-tf-generation-best-practices/SKILL.md`, remove these from `## Related Skills`:
- Any references to the 5 deleted skills

### 5. Grep for stale references

```bash
grep -r "configure-authentication\|check-workspace-status\|merge-openapi-specs\|regenerate-sdk\|validate-openapi-spec" skills/ --include="*.md" -l
```

Replace any found references with inline guidance.

### 6. Update TODO.md

Add a note about this follow-up cleanup.

### 7. Amend PR #10 or create a new PR

Either amend the existing commit on branch `feat/skill-parity-gen-2368` (PR #10 hasn't been merged yet) or create a follow-up PR. Amending is cleaner if the PR is still in review.

Branch: `feat/skill-parity-gen-2368`
PR: https://github.com/speakeasy-api/skills/pull/10
Linear: GEN-2368

### 8. Final skill count

After this work: **11 granular skills + 1 meta-skill** (down from the original 13, then 16, now 11).

## Principle for Future Skill Decisions

**Keep a skill if it provides Speakeasy-proprietary knowledge that an AI can't infer from `speakeasy --help` output or general programming knowledge.** Delete if it's just wrapping a single CLI command with obvious flags.
