# CLI Gaps for AI Tooling Compatibility

Analysis of Speakeasy CLI and `npx skills` for AI agent compatibility.

## Critical Issues Found in Skills

### 1. `speakeasy overlay create` - Does Not Exist

**File:** `skills/create-openapi-overlay/SKILL.md`

**Current documentation:**
```bash
speakeasy overlay create -s <spec-path> -o <output-path>
```

**Reality:** This command does not exist. Available overlay subcommands are:
- `speakeasy overlay compare` - Compare two specs and output an overlay
- `speakeasy overlay validate` - Validate an overlay file
- `speakeasy overlay apply` - Apply an overlay to a spec

**Fix needed:** Update skill to show creating overlays manually or use `overlay compare` to generate diffs.

---

### 2. ~~`speakeasy status --output` - Flag Does Not Exist~~ ✅ FIXED

**Status:** Fixed in latest CLI. The `--output` flag now supports `summary`, `console`, and `json` formats.

---

### 3. `npx skills validate` - Does Not Exist

**File:** `CLAUDE.md`

**Current documentation:**
```bash
npx skills validate ./skills/{skill-name}
```

**Reality:** The `npx skills` CLI does not have a `validate` command. Available commands are:
- `init` - Initialize a skill
- `add` - Add a skill package
- `check` - Check for updates
- `update` - Update skills
- `generate-lock` - Generate lock file

**CLI Enhancement Request:** Add a `validate` command to verify skill format/frontmatter.

---

### 4. `merge-openapi-specs` Syntax - Minor Discrepancy

**File:** `skills/merge-openapi-specs/SKILL.md`

**Current documentation:**
```bash
speakeasy merge -o <output-path> <spec1> <spec2> [spec3...]
```

**Actual CLI syntax:**
```bash
speakeasy merge -s path/to/spec1.yaml -s path/to/spec2.yaml -o output.yaml
```

The `-s` flag is required for each schema file.

---

## CLI Enhancement Recommendations for AI Tooling

### High Priority

#### 1. Consistent `--output` Flag

**Current state:** Some commands have `--output` (e.g., `run`, `quickstart`), others don't (e.g., `status`, `lint`).

**Recommendation:** Add `--output json|console|summary` to all commands for machine-readable output.

| Command | Has --output | Recommended |
|---------|-------------|-------------|
| `speakeasy run` | ✅ Yes | - |
| `speakeasy quickstart` | ✅ Yes | - |
| `speakeasy status` | ✅ Yes | - |
| `speakeasy lint openapi` | ❌ No | Add `--output json` |
| `speakeasy suggest` | ❌ No | Add `--output json` |
| `speakeasy overlay` | ❌ No | Add `--output json` |

#### 2. JSON Output for Lint Results

**Current state:** `speakeasy lint openapi` outputs human-readable text with ANSI colors.

**Recommendation:** Add `--output json` flag for structured error/warning data:
```json
{
  "errors": [{"path": "$.paths./users.get", "code": "missing-operationid", "message": "..."}],
  "warnings": [...],
  "hints": [...]
}
```

This would allow AI agents to programmatically process and fix issues.

#### 3. Non-Interactive Mode Flags

**Current state:** Some commands have `--non-interactive` or `-y/--auto-yes`, inconsistently applied.

**Recommendation:** Standardize `--non-interactive` and `-y` flags across all commands.

| Command | Has Non-Interactive | Notes |
|---------|---------------------|-------|
| `speakeasy run` | ✅ `-y, --auto-yes` | Works |
| `speakeasy lint openapi` | ✅ `--non-interactive` | Works |
| `speakeasy quickstart` | ❌ | Prompts for input |
| `speakeasy suggest` | ❌ | May prompt |
| `speakeasy auth` | ❌ | Interactive login |

### Medium Priority

#### 4. Exit Codes for Scripting

**Recommendation:** Document and standardize exit codes:
- `0` - Success
- `1` - General error
- `2` - Validation errors (lint)
- `3` - Authentication error
- `4` - Network error

#### 5. Environment Variable Documentation

**Current state:** `SPEAKEASY_API_KEY` is documented, others may exist but aren't well-documented.

**Recommendation:** Document all supported env vars for headless/CI use:
- `SPEAKEASY_API_KEY`
- `SPEAKEASY_WORKSPACE_ID` (if exists)
- `NO_COLOR` (disable ANSI colors)
- `SPEAKEASY_LOG_LEVEL`

#### 6. `speakeasy overlay create` Command

**Recommendation:** Add `speakeasy overlay create` to scaffold an overlay file:
```bash
speakeasy overlay create -s openapi.yaml -o overlay.yaml
# Creates empty overlay template targeting the spec
```

### Lower Priority

#### 7. Skill Validation Tool

**Recommendation:** Add `npx skills validate` command to verify:
- Valid YAML frontmatter with required `name` and `description`
- Markdown structure
- Referenced commands exist
- Links are valid

#### 8. Machine-Readable Help

**Recommendation:** Add `--help-json` flag to output command structure as JSON for programmatic parsing.

---

## `npx skills` CLI Issues

### 1. Flag Handling Bug

**Issue:** `npx skills init --help` creates a directory named `--help` instead of showing help.

**Expected:** Should display help text for the `init` command.

**Workaround:** Use `npx skills --help` for general help.

### 2. Missing Validation Command

**Issue:** No way to validate skill format before publishing.

**Recommendation:** Add `skills validate [path]` to check:
- Frontmatter format (`name`, `description` required)
- Markdown validity
- Section structure

---

## Summary Table

| Issue | Severity | Type | Owner |
|-------|----------|------|-------|
| `overlay create` missing | High | Skill Bug | skills |
| ~~`status --output` missing~~ | ~~High~~ | ~~Skill Bug~~ | ✅ Fixed in CLI |
| `npx skills validate` missing | Medium | Doc Bug + CLI Gap | skills repo + skills CLI |
| `merge` syntax | Low | Skill Bug | skills |
| JSON output for lint | High | CLI Enhancement | speakeasy CLI |
| Consistent --output flags | Medium | CLI Enhancement | speakeasy CLI (partially done) |
| Non-interactive standardization | Medium | CLI Enhancement | speakeasy CLI |
| Skills flag handling | Low | CLI Bug | npx skills |

---

## Next Steps

1. **Immediate:** Fix skill documentation bugs (this repo)
2. **File issues:** Report CLI enhancement requests to speakeasy CLI repo
3. **File issues:** Report `npx skills` bugs to skills CLI repo
