<div align="center">
 <a href="https://www.speakeasy.com/" target="_blank">
  <img width="1500" height="500" alt="Speakeasy Agent Skills" src="https://github.com/user-attachments/assets/7afc209b-3e03-46ea-a29c-50221f7aca4d" />
 </a>
 <br />
 <br />
  <div>
   <a href="https://speakeasy.com/docs/create-client-sdks/" target="_blank"><b>Docs Quickstart</b></a>&nbsp;&nbsp;//&nbsp;&nbsp;<a href="https://go.speakeasy.com/slack" target="_blank"><b>Join us on Slack</b></a>
  </div>
 <br />

 <br />

[![LW24 participant](https://img.shields.io/badge/featured-LW24-8957E5.svg?style=flat-square&labelColor=0D1117&logo=data:image/svg%2bxml;base64,PHN2ZyB3aWR0aD0iMzYwIiBoZWlnaHQ9IjM2MCIgdmlld0JveD0iMCAwIDM2MCAzNjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+IDxyZWN0IHdpZHRoPSI2MCIgaGVpZ2h0PSIzMDAiIGZpbGw9IndoaXRlIi8+IDxyZWN0IHg9IjYwIiB5PSIzMDAiIHdpZHRoPSIxMjAiIGhlaWdodD0iNjAiIGZpbGw9IndoaXRlIi8+IDxyZWN0IHg9IjI0MCIgeT0iMzAwIiB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIGZpbGw9IndoaXRlIi8+IDxyZWN0IHg9IjMwMCIgd2lkdGg9IjYwIiBoZWlnaHQ9IjMwMCIgZmlsbD0id2hpdGUiLz4gPHJlY3QgeD0iMTgwIiB3aWR0aD0iNjAiIGhlaWdodD0iMzAwIiBmaWxsPSJ3aGl0ZSIvPiA8L3N2Zz4=)](https://launchweek.dev/lw/2024/mega#participants)
  
</div>

<hr />
<br />

# Speakeasy Agent Skills

A collection of [Agent Skills](https://agentskills.io/) for SDK generation and OpenAPI tooling with the [Speakeasy CLI](https://speakeasy.com/).

## Installation

```bash
npx skills add speakeasy-api/skills
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
| `speakeasy:sdk-tf-generation-best-practices` | Need best practices for SDK/Terraform generation, customization, testing, or OpenAPI management |

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
speakeasy-api/skills/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── start-new-sdk-project/
│   │   └── SKILL.md
│   ├── regenerate-sdk/
│   │   └── SKILL.md
│   └── ... (13 skills total)
├── templates/
│   └── SKILL.template.md
├── AGENTS.md              # Contributor guidance for AI agents
├── CLAUDE.md              # Claude-specific contributor guidance
├── README.md
└── LICENSE
```

## Contributing

See [AGENTS.md](./AGENTS.md) for guidance on creating and maintaining skills.

## Supported Agents

These skills follow the [Agent Skills specification](https://agentskills.io/specification) and work with:

- [Claude Code](https://claude.ai/code)
- [Cursor](https://cursor.sh/)
- [GitHub Copilot](https://github.com/features/copilot)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- And [15+ other platforms](https://agentskills.io/)

## License

Apache-2.0
