# Speakeasy Agent Skills

A collection of [Agent Skills](https://agentskills.io/) for SDK generation and OpenAPI tooling with the [Speakeasy CLI](https://speakeasy.com/).

## Installation

```bash
npx skills add speakeasy-api/agent-skills
```

## Available Skills

| Skill | Use When... |
|-------|-------------|
| `speakeasy:start-new-sdk-project` | You have an OpenAPI spec and want to generate an SDK |
| `speakeasy:regenerate-sdk` | Your spec changed and you need to regenerate |
| `speakeasy:validate-openapi-spec` | Checking if spec is valid, running `speakeasy lint` |
| `speakeasy:get-ai-suggestions` | SDK method names are ugly, wanting to improve operation IDs |
| `speakeasy:check-workspace-status` | Asking what targets/sources are configured |
| `speakeasy:create-openapi-overlay` | Need to customize SDK without editing source spec |
| `speakeasy:apply-openapi-overlay` | Applying an overlay file to a spec |
| `speakeasy:merge-openapi-specs` | Combining multiple OpenAPI specs |
| `speakeasy:diagnose-generation-failure` | SDK generation failed, seeing "Step Failed: Workflow" |
| `speakeasy:fix-validation-errors-with-overlays` | Have lint errors but can't modify source spec |
| `speakeasy:improve-operation-ids` | SDK methods have names like `GetApiV1Users` |
| `speakeasy:configure-authentication` | Setting up Speakeasy auth in CI/CD or non-interactive environments |

## Key Principles

1. **Don't auto-fix everything** - Distinguish between:
   - Small issues (naming, descriptions) → Fix with overlays
   - Structural issues (invalid refs) → Ask the user
   - Design issues (auth, API structure) → Produce strategy document

2. **AI-friendly output** - Use `speakeasy run --output console` for structured output, pipe to `grep`/`tail` to reduce context

3. **Overlay over modify** - Never modify source specs directly. Overlays make patches portable across spec versions.

4. **Grouped SDK methods** - Guide users toward `sdk.users.list()` pattern using `x-speakeasy-group` + `x-speakeasy-name-override`

## Directory Structure

```
speakeasy-api/agent-skills/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── start-new-sdk-project/
│   │   └── SKILL.md
│   ├── regenerate-sdk/
│   │   └── SKILL.md
│   └── ... (12 skills total)
├── README.md
└── LICENSE
```

## Supported Agents

These skills follow the [Agent Skills specification](https://agentskills.io/specification) and work with:

- [Claude Code](https://claude.ai/code)
- [Cursor](https://cursor.sh/)
- [GitHub Copilot](https://github.com/features/copilot)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- And [15+ other platforms](https://agentskills.io/)

## License

Apache-2.0
