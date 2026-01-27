---
short_description: "Generate production-ready SDKs from OpenAPI specifications"
long_description: |
  Step-by-step guide for generating SDKs from OpenAPI/Swagger specs using the Speakeasy CLI.
  Covers installation, authentication, quickstart workflow, language selection, and SDK
  iteration using Studio.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/docs/sdks/create-client-sdks.mdx"
  ref: "aed058705f8de5772cba0fd389707cfd4d0752f7"
  last_reconciled: "2025-12-11"
related:
  - "../sdk-overview.md"
  - "../sdk-concepts.md"
  - "../CLI_REFERENCE.md"
---

# Generate SDKs from OpenAPI

This page documents using the Speakeasy CLI to generate SDKs from OpenAPI / Swagger specs.

For a more UI-based experience, use the Speakeasy app: https://app.speakeasy.com/editor/onboarding

## Install the Speakeasy CLI

After signing up, install the Speakeasy CLI using one of the following methods:

**CHOOSE ONE** installation method:

**Option 1: Homebrew (macOS)**
```bash
brew install speakeasy-api/tap/speakeasy
```

**Option 2: Script Installation (macOS and Linux)**
```bash
curl -fsSL https://go.speakeasy.com/cli-install.sh | sh
```

**Option 3: Winget (Windows)**
```bash
winget install speakeasy
```

**Option 4: Chocolatey (Windows)**
```bash
choco install speakeasy
```

For manual installation, download the latest release from the releases page (https://github.com/speakeasy-api/speakeasy/releases), extract the binary, and add it to the system path.

---

## Speakeasy Quickstart

For first-time SDK generation, run `speakeasy quickstart`.

**For agents and automation (recommended):**

```bash
speakeasy quickstart --skip-interactive --output console -s spec.yaml -t python -o ./sdk
```

> **Flag reference:**
> - `-s, --schema` — OpenAPI spec (see schema sources below)
> - `-t, --target` — Language target (see [supported targets](#choose-target-language))
> - `-o, --out-dir` — Output directory
> - `-n, --name` — SDK name (avoids interactive prompt)
> - `-p, --package-name` — Package name (avoids interactive prompt)
> - `--skip-interactive` — Skip browser auth and interactive prompts (requires `SPEAKEASY_API_KEY`)
> - `--output console` — Structured output for agent/automation consumption
>
> **Schema sources for `-s`:**
>
> | Format | Syntax | Example |
> |--------|--------|---------|
> | Local file | File path | `./api/openapi.yaml` |
> | URL | HTTP(S) URL | `https://api.example.com/openapi.json` |
> | Registry source | `source-name` | `my-api` |
> | Registry source (tagged) | `source-name@tag` | `my-api@latest` |
> | Registry source (fully qualified) | `org/workspace/source@tag` | `acme/prod/my-api@v2` |
>
> **Interactive mode:** Run `speakeasy quickstart` with no flags for the guided wizard (opens browser for auth).

### Authentication and account creation

The CLI will prompt for authentication with a Speakeasy account. A browser window will open to select a workspace to associate with the CLI. Workspaces can be changed later if required.

If there's no existing account, the CLI will prompt to create one.

New accounts start with a 14-day free trial of Speakeasy's business tier, to enable users to try out every SDK generation feature. At the end of the trial, accounts will revert to the free tier. No credit card is required.

Free accounts can continue to generate one SDK with up to 50 API methods free of charge. Please refer to the pricing page (https://www.speakeasy.com/pricing) for updated information on each pricing tier.

### Upload an OpenAPI document

After authentication, the system prompts for an OpenAPI document.

Provide either a link to a remote hosted OpenAPI document, or a relative path to a local file in one of the supported formats:

| Spec Format | Supported |
|-------------|-----------|
| OpenAPI 3.0 | Yes |
| OpenAPI 3.1 | Yes |
| JSON Schema | Yes |

> **Tip:** If the spec is in an unsupported format, convert it using the Speakeasy CLI:
> ```bash
> speakeasy openapi transform convert-swagger -s swagger2.yaml -o openapi.yaml
> ```
> For Postman collections, use the `postman2openapi` CLI tool.

### Remote Spec Sources (Production Pattern)

For SDKs that need to stay in sync with a live API, configure `workflow.yaml` to fetch specs directly from URLs instead of local files:

```yaml
# .speakeasy/workflow.yaml
workflowVersion: 1.0.0
speakeasyVersion: latest
sources:
  my-api:
    inputs:
      - location: https://api.example.com/openapi.json  # Live API spec URL
    registry:
      location: registry.speakeasyapi.dev/org/workspace/source-name
targets:
  python-sdk:
    target: python
    source: my-api
    publish:
      pypi:
        token: $pypi_token
    codeSamples:
      output: codeSamples.yaml
      registry:
        location: registry.speakeasyapi.dev/org/workspace/code-samples-python
```

**Benefits of remote spec fetching:**
- Automatic daily regeneration catches API changes
- No manual spec file management required
- Registry stores versioned history of all specs
- CI/CD can trigger on spec changes

**Considerations:**
- API spec endpoint must be publicly accessible (or use authentication)
- Consider pinning to specific versions for stability in production
- Combine with scheduled GitHub Actions for automatic updates

**Example CI/CD workflow for daily regeneration:**

```yaml
# .github/workflows/sdk_generation.yaml
name: Generate
on:
  workflow_dispatch:
    inputs:
      force:
        description: Force generation of SDKs
        type: boolean
        default: false
  schedule:
    - cron: 0 0 * * *  # Daily at midnight
jobs:
  generate:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/workflow-executor.yaml@v15
    with:
      force: ${{ github.event.inputs.force }}
      mode: pr
      speakeasy_version: latest
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      pypi_token: ${{ secrets.PYPI_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
```

> **Pattern Source:** Extracted from [dub-python](https://github.com/dubinc/dub-python) SDK

### Code Samples Generation

Configure automatic code samples generation that can be integrated with documentation systems:

```yaml
# In workflow.yaml targets section
targets:
  python-sdk:
    target: python
    source: my-api
    codeSamples:
      output: codeSamples.yaml  # Output file for code samples overlay
      registry:
        location: registry.speakeasyapi.dev/org/workspace/code-samples-python
```

This generates a `codeSamples.yaml` file containing usage examples for each operation:

```yaml
# codeSamples.yaml (auto-generated)
overlay: 1.0.0
info:
  title: CodeSamples overlay for python target
actions:
  - target: $["paths"]["/users"]["get"]
    update:
      x-codeSamples:
        - lang: python
          label: listUsers
          source: |-
            from myapi import MyAPI

            with MyAPI(token="API_KEY") as client:
                res = client.users.list()
                print(res)
```

This overlay can be used to:
- Populate documentation sites with working code examples
- Ensure README examples stay in sync with the SDK
- Provide consistent examples across multiple SDK languages

> **Pattern Source:** Extracted from [dub-python](https://github.com/dubinc/dub-python) SDK

### Select artifact type

After configuring the OpenAPI document, the next step prompt is to choose the type of artifact being generated: SDK or MCP. Select SDK, and a prompt will appear to choose the target language.

> **Note:** Choosing Terraform will default back to the CLI native onboarding. Editor support for Terraform previews coming soon.

### Choose target language

> **Agent instruction:** If the user has not specified a target language, **ask them before proceeding**. Do not assume a default.

For each language, Speakeasy has crafted generators with language experts to be highly idiomatic.

**Supported languages:**
- Python (`python`)
- TypeScript (`typescript`)
- Go (`go`)
- Java (`java`)
- C# (`csharp`)
- Ruby (`ruby`)
- PHP (`php`)
- Swift (`swift`)
- Rust (`rust`)

### Complete the SDK configuration

Speakeasy validates the specifications and generates the SDK after receiving all inputs. The process executes `speakeasy run` to validate, generate, compile, and set up the SDK. A confirmation message displays the generated SDK details upon successful completion.

## Iterating on the SDK with Studio

If the SDK is successfully generated, there will be a prompt asking to open the SDK Studio. The Studio is a web GUI that helps users make look and feel improvements to their SDKs. It uses OpenAPI Overlays to preserve the original OpenAPI specification while allowing users to make changes to the generated SDK.

Saved changes in the Studio automatically trigger a regeneration of the SDK locally.

It is also possible to make changes without the Studio.

## Next Step: Uploading the SDK to GitHub

Once the SDK is ready, upload it to GitHub by following the GitHub setup guide.

## CLI Reference

For agent and automation workflows, use non-interactive mode:

```bash
# Generate SDK (non-interactive)
speakeasy quickstart --skip-interactive --output console -s spec.yaml -t python -o ./sdk

# Validate OpenAPI spec
speakeasy lint openapi -s spec.yaml

# Regenerate from existing configuration
speakeasy run

# Apply overlay to spec
speakeasy overlay apply -s spec.yaml -o overlay.yaml --out modified.yaml

# Convert Swagger 2.0 to OpenAPI 3.x
speakeasy openapi transform convert-swagger -s old.yaml -o new.yaml
```

---

## Advanced: Multi-SDK Monorepos

For organizations with multiple API products, Speakeasy supports monorepo structures where multiple SDKs are generated and managed from a single repository.

### Monorepo Types

| Type | Description | Example |
|------|-------------|---------|
| Multi-Product / Single-Language | Multiple APIs → Multiple SDKs in one language | Codatio Java (9 products) |
| Single-Product / Multi-Language | One API → SDKs in multiple languages | Typical polyglot SDK repo |
| Hybrid | Multiple APIs → Multiple SDKs in multiple languages | Large platform monorepo |

### Shared workflow.yaml Structure

A monorepo uses a single `workflow.yaml` at the repository root to manage multiple sources and targets:

```yaml
# .speakeasy/workflow.yaml
workflowVersion: 1.0.0
speakeasyVersion: latest
sources:
  # Each API product has its own source
  product-a-source:
    inputs:
      - location: https://api.example.com/specs/product-a.yaml
    registry:
      location: registry.speakeasyapi.dev/org/workspace/product-a-source
  product-b-source:
    inputs:
      - location: https://api.example.com/specs/product-b.yaml
    registry:
      location: registry.speakeasyapi.dev/org/workspace/product-b-source
  product-c-source:
    inputs:
      - location: https://api.example.com/specs/product-c.yaml
    registry:
      location: registry.speakeasyapi.dev/org/workspace/product-c-source
targets:
  # Each SDK is a separate target
  product-a-sdk:
    target: java
    source: product-a-source
    output: product-a
    publish:
      java:
        ossrhUsername: $ossrh_username
        ossrhPassword: $ossrh_password
        gpgSecretKey: $java_gpg_secret_key
        gpgPassPhrase: $java_gpg_passphrase
    codeSamples:
      registry:
        location: registry.speakeasyapi.dev/org/workspace/product-a-java-samples
      blocking: false
  product-b-sdk:
    target: java
    source: product-b-source
    output: product-b
    publish:
      java:
        ossrhUsername: $ossrh_username
        ossrhPassword: $ossrh_password
        gpgSecretKey: $java_gpg_secret_key
        gpgPassPhrase: $java_gpg_passphrase
  product-c-sdk:
    target: java
    source: product-c-source
    output: product-c
```

### Monorepo Directory Structure

```
my-sdk-monorepo/
├── .speakeasy/
│   ├── workflow.yaml         # Shared workflow for all SDKs
│   └── workflow.lock         # Version lock
├── .github/workflows/
│   ├── product-a_generate.yaml   # Per-SDK generation workflow
│   ├── product-a_release.yaml    # Per-SDK release workflow
│   ├── product-b_generate.yaml
│   ├── product-b_release.yaml
│   └── ...
├── product-a/                # SDK for Product A
│   ├── .speakeasy/
│   │   └── gen.yaml          # Product A specific config
│   ├── src/
│   └── build.gradle
├── product-b/                # SDK for Product B
│   ├── .speakeasy/
│   │   └── gen.yaml
│   ├── src/
│   └── build.gradle
├── product-c/                # SDK for Product C
│   └── ...
└── README.md                 # Root documentation
```

### Per-SDK Configuration

Each SDK maintains its own `gen.yaml` with product-specific settings:

```yaml
# product-a/.speakeasy/gen.yaml
configVersion: 2.0.0
generation:
  sdkClassName: ProductA
  telemetryEnabled: true
java:
  version: 1.0.0
  artifactID: product-a
  groupID: io.example
  description: "SDK for Product A API"
```

### CI/CD for Multi-SDK Repos

Use per-SDK workflows with path-based triggers for independent release cycles:

**Generation Workflow** (`product-a_generate.yaml`):

```yaml
name: Generate Product A SDK
on:
  workflow_dispatch:
    inputs:
      force:
        description: Force generation
        type: boolean
        default: false
      set_version:
        description: Optionally set a specific SDK version
        type: string
jobs:
  generate:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/workflow-executor.yaml@v15
    with:
      force: ${{ github.event.inputs.force }}
      mode: pr
      set_version: ${{ github.event.inputs.set_version }}
      speakeasy_version: latest
      target: product-a-sdk   # Specific target from workflow.yaml
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
```

**Release Workflow** (`product-a_release.yaml`):

```yaml
name: Release Product A SDK
on:
  push:
    paths:
      - product-a/RELEASES.md   # Only triggers on this SDK's RELEASES.md
    branches:
      - main
jobs:
  publish:
    uses: speakeasy-api/sdk-generation-action/.github/workflows/sdk-publish.yaml@v15
    secrets:
      github_access_token: ${{ secrets.GITHUB_TOKEN }}
      speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}
      ossrh_username: ${{ secrets.OSSRH_USERNAME }}
      ossrh_password: ${{ secrets.OSSRH_PASSWORD }}
      java_gpg_secret_key: ${{ secrets.JAVA_GPG_SECRET_KEY }}
      java_gpg_passphrase: ${{ secrets.JAVA_GPG_PASSPHRASE }}
```

**Benefits of per-SDK workflows:**
- Independent release cycles for each SDK
- Changes to one SDK don't rebuild others
- Clear audit trail via `RELEASES.md` per SDK
- Minimal CI/CD execution time

### Registry-Based Source Management

For large organizations, use the Speakeasy registry to version and manage spec sources:

```yaml
sources:
  my-api:
    inputs:
      - location: https://raw.githubusercontent.com/org/specs/main/api.yaml
    registry:
      location: registry.speakeasyapi.dev/org/workspace/my-api-source
```

The registry provides:
- Content-addressable versioning via SHA256 digests
- Tags for semantic versioning (e.g., `3.0.0`, `latest`)
- History of all spec versions
- Digest pinning for reproducible builds

The `workflow.lock` file records the exact versions used:

```yaml
speakeasyVersion: 1.462.2
sources:
  my-api-source:
    sourceNamespace: my-api-source
    sourceRevisionDigest: sha256:abc123...
    sourceBlobDigest: sha256:def456...
    tags:
      - latest
      - 3.0.0
```

> **Pattern Source:** Extracted from [codatio/client-sdk-java](https://github.com/codatio/client-sdk-java) - production multi-SDK monorepo

---

## Code Samples Registry

Speakeasy can automatically generate and store code samples in the registry for use in documentation, developer portals, and API references.

### Configuration

```yaml
targets:
  my-sdk:
    target: python
    source: my-api
    codeSamples:
      output: codeSamples.yaml      # Local output file
      registry:
        location: registry.speakeasyapi.dev/org/workspace/sdk-code-samples
      blocking: false               # Async generation
```

### Configuration Options

| Option | Description |
|--------|-------------|
| `output` | Local file path for generated code samples overlay |
| `registry.location` | Registry path for storing code samples |
| `blocking: true` | Generation waits for code samples to complete |
| `blocking: false` | Code samples generated asynchronously (recommended) |

### Usage Patterns

**Non-blocking (Recommended):** Code samples are generated asynchronously after SDK generation completes. This speeds up the main generation workflow.

```yaml
codeSamples:
  registry:
    location: registry.speakeasyapi.dev/org/workspace/samples
  blocking: false
```

**Blocking:** Useful when downstream processes need code samples immediately.

```yaml
codeSamples:
  output: codeSamples.yaml
  blocking: true
```

> **Pattern Source:** Extracted from [codatio/client-sdk-java](https://github.com/codatio/client-sdk-java)

---

## Post-Generation Validation

After generating an SDK, consider whether the OpenAPI spec accurately represents the live API. This is especially important when the spec source is untrusted.

### When to Validate Post-Generation

| Spec Source | Trust Level | Validation Recommended |
|-------------|-------------|------------------------|
| You wrote it | High | Static validation only |
| Auto-generated from code | Medium | Consider contract testing |
| Third-party API | Low | Contract testing recommended |
| Converted from Swagger 2.0 | Medium | Contract testing recommended |
| Unknown origin / inherited | Low | Contract testing strongly recommended |

### Validation Decision Tree

```
SDK Generated Successfully
        │
        ├─ Is the spec source authoritative?
        │    │
        │    ├─ YES (you control the API and spec)
        │    │    └─ Done. Consider integration tests.
        │    │       → sdk-testing/integration-testing.md
        │    │
        │    └─ NO (third-party, auto-generated, or unknown)
        │         │
        │         ├─ Do you have API access + credentials?
        │         │    │
        │         │    ├─ YES → Run contract tests
        │         │    │        → sdk-testing/contract-testing.md
        │         │    │
        │         │    └─ NO → Document assumption that spec is accurate
        │         │            Monitor for ResponseValidationError in production
        │         │
        │         └─ Are users reporting ResponseValidationError?
        │              └─ YES → Contract testing required
        │                       → sdk-testing/contract-testing.md
```

### Contract Testing Quick Start

If contract testing is appropriate:

```bash
# Clone the contract testing agent
git clone https://github.com/speakeasy-api/speakeasy-contract-testing-agent.git
cd speakeasy-contract-testing-agent
npm install

# Create config.json for your SDK
cat > config.json << 'EOF'
{
  "apiKey": "your-api-key",
  "dir": "/absolute/path/to/generated/sdk",
  "language": "python",
  "sdkMethods": [
    "sdk.resources.list()",
    "sdk.resources.create()",
    "sdk.users.get()"
  ]
}
EOF

# Run contract tests
npm run start -- config.json --limit 10
```

### Handling Contract Test Failures

If contract tests reveal `ResponseValidationError`:

1. **Review the mismatch** - Check which field/type differs
2. **Determine the fix**:
   - If spec is wrong → Update the spec directly
   - If spec is read-only → Create an overlay to fix types
3. **Regenerate SDK** with `speakeasy run`
4. **Re-run contract tests** to verify

**Example overlay for type fixes:**

```yaml
# type-fixes.yaml
overlay: 1.0.0
info:
  title: Fix type mismatches found by contract testing
actions:
  - target: $.components.schemas.Response.properties.count
    update:
      type: string  # API returns string, not integer
  - target: $.components.schemas.User.properties.metadata
    update:
      nullable: true  # API sometimes returns null
```

> **Full guide:** See `../sdk-testing/contract-testing.md` for comprehensive contract testing documentation.

---

## Pre-defined TODO List

When executing this workflow, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Speakeasy CLI is installed | Verifying Speakeasy CLI installation |
| 2 | Authenticate with Speakeasy account | Authenticating with Speakeasy account |
| 3 | Locate or extract OpenAPI specification | Locating or extracting OpenAPI specification |
| 4 | Validate OpenAPI specification | Validating OpenAPI specification |
| 5 | Fix validation errors if present | Fixing validation errors if present |
| 6 | Ask user for target SDK language (if not specified) | Selecting target SDK language |
| 7 | Run speakeasy quickstart | Running speakeasy quickstart |
| 8 | Verify SDK compilation succeeds | Verifying SDK compilation succeeds |
| 9 | Review generated SDK structure | Reviewing generated SDK structure |
| 10 | Enable Spring Boot starter (Java only) | Enabling Spring Boot starter |
| 11 | Implement SDK hooks if needed | Implementing SDK hooks |
| 12 | Add custom helper code if needed | Adding custom helper code |
| 13 | Customize README with branding | Customizing README with branding |
| 14 | Add custom authentication guide to README | Adding custom authentication guide |
| 15 | Add domain-specific usage examples | Adding domain-specific usage examples |
| 16 | Set up interface generation for testing | Setting up interface generation |
| 17 | Configure mock generation | Configuring mock generation |
| 18 | Set up integration test infrastructure | Setting up integration test infrastructure |
| 19 | Write initial integration tests | Writing initial integration tests |
| 20 | Configure CI/CD for daily regeneration | Configuring CI/CD for daily regeneration |
| 21 | Document SDK output location | Documenting SDK output location |

**Usage:**
```
TodoWrite([
  {content: "Verify Speakeasy CLI is installed", status: "pending", activeForm: "Verifying Speakeasy CLI installation"},
  {content: "Authenticate with Speakeasy account", status: "pending", activeForm: "Authenticating with Speakeasy account"},
  {content: "Locate or extract OpenAPI specification", status: "pending", activeForm: "Locating or extracting OpenAPI specification"},
  {content: "Validate OpenAPI specification", status: "pending", activeForm: "Validating OpenAPI specification"},
  {content: "Fix validation errors if present", status: "pending", activeForm: "Fixing validation errors if present"},
  {content: "Ask user for target SDK language (if not specified)", status: "pending", activeForm: "Selecting target SDK language"},
  {content: "Run speakeasy quickstart", status: "pending", activeForm: "Running speakeasy quickstart"},
  {content: "Verify SDK compilation succeeds", status: "pending", activeForm: "Verifying SDK compilation succeeds"},
  {content: "Review generated SDK structure", status: "pending", activeForm: "Reviewing generated SDK structure"},
  {content: "Enable Spring Boot starter (Java only)", status: "pending", activeForm: "Enabling Spring Boot starter"},
  {content: "Implement SDK hooks if needed", status: "pending", activeForm: "Implementing SDK hooks"},
  {content: "Add custom helper code if needed", status: "pending", activeForm: "Adding custom helper code"},
  {content: "Customize README with branding", status: "pending", activeForm: "Customizing README with branding"},
  {content: "Add custom authentication guide to README", status: "pending", activeForm: "Adding custom authentication guide"},
  {content: "Add domain-specific usage examples", status: "pending", activeForm: "Adding domain-specific usage examples"},
  {content: "Set up interface generation for testing", status: "pending", activeForm: "Setting up interface generation"},
  {content: "Configure mock generation", status: "pending", activeForm: "Configuring mock generation"},
  {content: "Set up integration test infrastructure", status: "pending", activeForm: "Setting up integration test infrastructure"},
  {content: "Write initial integration tests", status: "pending", activeForm: "Writing initial integration tests"},
  {content: "Configure CI/CD for daily regeneration", status: "pending", activeForm: "Configuring CI/CD for daily regeneration"},
  {content: "Document SDK output location", status: "pending", activeForm: "Documenting SDK output location"}
])
```

**Nested workflows:**

- **Step 3 (Extract OpenAPI)**: If extracting from code, read the appropriate framework guide:
  - FastAPI: `code-first/fastapi.md` - nest its TODO list under step 3
  - Express: `code-first/express.md` - nest its TODO list under step 3
  - Spring Boot: `code-first/spring-boot.md` - nest its TODO list under step 3
  - Django: `code-first/django.md` - nest its TODO list under step 3

- **Step 5 (Fix validation errors)**: If errors occur, read:
  - `spec-first/validation.md` - nest its TODO list under step 5
  - Specific error guides as needed (security-schemes.md, pagination.md, etc.)

- **Step 10 (Spring Boot starter)**: For Java SDKs targeting Spring Boot applications:
  - `sdk-languages/java.md` - Spring Boot Integration section
  - Covers: `generateSpringBootStarter: true`, configuration properties, bean injection

- **Step 11 (SDK hooks)**: For cross-cutting concerns:
  - `sdk-languages/java.md` - SDK Hooks section (BeforeRequest, AfterSuccess, AfterError)
  - Common use cases: API version headers, correlation IDs, logging, rate limit handling

- **Step 12 (Custom helpers)**: For authentication utilities and domain-specific code:
  - `sdk-languages/java.md` - Custom Helper Code section
  - Patterns: Request state modeling, multi-token verification, auth entry points

- **Step 13-15 (README customization)**: For polished developer experience:
  - `sdk-customization/readme-customization.md` - full README customization guide
  - Covers: branding headers, badges, OAuth flow documentation, domain examples
  - Pattern sources: Square TypeScript SDK, Clerk Java SDK

- **Step 11-17 (SDK hooks, interfaces, mocks)**: For language-specific patterns, read:
  - Go: `sdk-languages/go.md` - hooks, interface generation, mock configuration
  - Java: `sdk-languages/java.md` - Spring Boot, hooks, custom helpers, Maven publishing
  - Python: `sdk-languages/python.md` - async patterns, type safety

- **Step 18-19 (Integration tests)**: For test infrastructure:
  - `sdk-testing/integration-testing.md` - patterns for integration tests
  - Includes SDK factory, environment helpers, cleanup patterns

- **Step 20 (CI/CD)**: For automated spec sync and regeneration:
  - Configure `workflow.yaml` with remote spec URL
  - Set up daily scheduled generation via GitHub Actions
  - Use `mode: pr` for review-based regeneration

**Note on conditional steps:**
- Step 5 only applies if step 4 reveals validation errors
- If no errors in step 4, mark step 5 as completed immediately
- Step 3 varies based on whether you have an existing spec or need to extract from code
- Step 10 only applies to Java SDKs targeting Spring Boot applications
- Steps 13-15 (README) are recommended for production SDKs
- Steps 11-19 are optional based on SDK maturity requirements
