---
short_description: "Introduction to Speakeasy SDKs and API tooling platform"
long_description: |
  Overview of Speakeasy's platform for generating production-ready SDKs, Terraform providers,
  and API documentation from OpenAPI specifications. Includes workflow architecture and setup
  instructions for getting started with SDK generation.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/docs/sdks/introduction.mdx"
  ref: "aed058705f8de5772cba0fd389707cfd4d0752f7"
  last_reconciled: "2025-12-11"
related:
  - "plans/sdk-generation.md"
  - "sdk-concepts.md"
  - "CLI_REFERENCE.md"
---

# Introduction to Speakeasy SDKs

Speakeasy helps teams build great developer experiences for their APIs.

The platform provides the tools, workflows, and infrastructure to generate and manage high-quality SDKs, Terraform providers, and API documentation directly from OpenAPI specs.

With Speakeasy, teams can go from an OpenAPI definition to a fully versioned, type-safe SDK in minutes, complete with publishing, CI/CD, and changelog automation.

## Why APIs matter

APIs are a powerful force for innovation. One team solves a problem, exposes an API, and every engineer (or AI agent) benefits from their work. That means more time spent tackling new problems, and less time reinventing the wheel.

The problem is that most APIs are bad.

The tools and practices for building quality, reliable APIs haven't kept pace with the central role APIs play in modern software development.

That's the problem Speakeasy exists to solve.

## Generate with Speakeasy

Speakeasy can generate:

- **SDKs** - Production-ready client libraries in multiple languages
- **Terraform Providers** - Infrastructure as code for API resources
- **API Documentation** - Reference docs with code samples
- **MCP Servers** - Tools for LLM and agent interactions

## Before you begin

### Sign up

Sign up for a free Speakeasy account at https://app.speakeasy.com.

New accounts start with a 14-day free trial of Speakeasy's business tier, enabling users to try out every SDK generation feature. At the end of the trial, accounts will revert to the free tier. No credit card is required.

Free accounts can continue to generate one SDK with up to 50 API methods free of charge.

### Install the Speakeasy CLI

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

## Workflow

![Speakeasy Reference Architecture](/assets/docs/ref-architecture.png)

The platform is built to be OpenAPI-native, no proprietary DSLs to cause lock-in. From OpenAPI specs, the platform enables generation of SDKs, API documentation, agent tools and more.

To make it seamless, native CI/CD workflows automate updates, from backend changes through to SDK release management.

## Support

Speakeasy operates as an extension of customers' API platform teams. Dedicated support helps with sensitive releases and provides feedback on API design and best practices.

---

## Pre-defined TODO List

When getting started with Speakeasy SDKs, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Sign up for Speakeasy account | Signing up for account |
| 2 | Install Speakeasy CLI | Installing Speakeasy CLI |
| 3 | Authenticate CLI with account | Authenticating CLI |
| 4 | Prepare or obtain OpenAPI specification | Preparing OpenAPI specification |
| 5 | Review workflow architecture | Reviewing workflow architecture |
| 6 | Understand source and target concepts | Understanding core concepts |

**Usage:**
```
TodoWrite([
  {content: "Sign up for Speakeasy account", status: "pending", activeForm: "Signing up for account"},
  {content: "Install Speakeasy CLI", status: "pending", activeForm: "Installing Speakeasy CLI"},
  {content: "Authenticate CLI with account", status: "pending", activeForm: "Authenticating CLI"},
  {content: "Prepare or obtain OpenAPI specification", status: "pending", activeForm: "Preparing OpenAPI specification"},
  {content: "Review workflow architecture", status: "pending", activeForm: "Reviewing workflow architecture"},
  {content: "Understand source and target concepts", status: "pending", activeForm: "Understanding core concepts"}
])
```

**Nested workflows:**
- For generating SDKs, see `plans/sdk-generation.md`
- For detailed concepts, see `sdk-concepts.md`

