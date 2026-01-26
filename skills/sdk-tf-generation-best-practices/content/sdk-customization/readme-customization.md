---
short_description: "Customize SDK READMEs with branding, examples, and domain-specific content"
long_description: |
  Guide for creating excellent SDK READMEs that combine auto-generated sections with custom
  branding, authentication guides, and domain-specific examples. Covers gen.yaml configuration,
  README injection points, and patterns from production SDKs like Square.
source:
  repo: "speakeasy-sdks/square-typescript-sdk, clerk/clerk-sdk-java"
  path: "README.md"
  ref: "analysis-2025-12-11"
  last_reconciled: "2025-12-11"
related:
  - "plans/sdk-generation.md"
  - "sdk-languages/typescript.md"
  - "sdk-languages/java.md"
---

# SDK README Customization

Speakeasy auto-generates comprehensive READMEs with sections for installation, usage, authentication, error handling, and more. This guide shows how to customize these READMEs with branding, domain-specific content, and enhanced examples.

## README Structure Overview

Generated READMEs follow a standard structure with injection points for customization:

```markdown
<div align="center">
    <img src="logo.png">           <!-- Custom branding -->
    <h1>SDK Name</h1>
    <p>Tagline</p>                  <!-- Custom -->
    <a href="docs">Badges</a>       <!-- Custom -->
</div>

<!-- Start Summary [summary] -->
## Summary
Auto-generated from OpenAPI info section
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
Auto-generated navigation
<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation
Auto-generated package manager instructions
<!-- End SDK Installation [installation] -->

<!-- Custom sections can be inserted here -->

<!-- Start Authentication [security] -->
## Authentication
Auto-generated from security schemes
<!-- End Authentication [security] -->

<!-- Custom authentication guide here -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage
Auto-generated from examples
<!-- End SDK Example Usage [usage] -->

<!-- Additional sections... -->
```

## Customization via gen.yaml

### Basic Branding Configuration

```yaml
# .speakeasy/gen.yaml
generation:
  sdkClassName: Square
  usageSnippets:
    optionalPropertyRendering: withExample
    sdkInitStyle: constructor

  # README-specific settings
  auth:
    oAuth2ClientCredentialsEnabled: true
    hoistGlobalSecurity: true

typescript:
  version: 1.0.0
  packageName: square
  author: Square
```

### Additional Files Configuration

Add custom content that appears in the generated README:

```yaml
# .speakeasy/gen.yaml
generation:
  additionalDocs:
    - path: AUTHENTICATION.md      # Custom auth guide
    - path: MIGRATION.md           # Migration guide
    - path: CONTRIBUTING.md        # Contribution guidelines
```

## Custom Header Section

Add branding, tagline, and badges before the auto-generated content:

```markdown
<div align="center">
    <img width="200px" src="https://avatars.githubusercontent.com/u/82592?s=200&v=4">
    <h1>Square TypeScript SDK</h1>
    <p><strong>Powering all the ways you do business.</strong></p>
    <p>Work smarter, automate for efficiency, and open up new revenue streams.</p>
    <a href="https://developer.squareup.com/docs"><img src="https://img.shields.io/static/v1?label=Docs&message=API Ref&color=4c2cec&style=for-the-badge" /></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" /></a>
</div>
```

### Badge Examples

| Badge Type | Example |
|------------|---------|
| Documentation | `![Docs](https://img.shields.io/static/v1?label=Docs&message=API%20Ref&color=4c2cec&style=for-the-badge)` |
| License | `![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)` |
| NPM Version | `![npm](https://img.shields.io/npm/v/square?style=for-the-badge)` |
| Build Status | `![Build](https://img.shields.io/github/actions/workflow/status/org/repo/ci.yml?style=for-the-badge)` |

## Custom Authentication Section

After the auto-generated `<!-- End Authentication [security] -->` section, add domain-specific authentication guidance:

### Example: OAuth Flow Documentation

```markdown
### Obtaining an Access Token

There are two types of access token:

**Personal access token** - Provides unrestricted API access to resources in your account.

**OAuth access token** - Provides authenticated and scoped API access to resources in other accounts.

#### Personal Access Tokens

> [!NOTE]
> If needed, follow the steps in [Get Started](https://developer.example.com/docs/get-started) to create an account.

To get a personal access token:

1. Sign in to the [Developer Dashboard](https://developer.example.com/apps)
2. In the left pane, choose Credentials
3. At the top of the page, choose Production
4. In the Production Access token box, choose Show and copy your token

![Personal Access Tokens](https://example.com/token-screenshot.png)

#### OAuth Access Token - *Code Flow*

```typescript
import { randomBytes } from 'crypto';
import type { Scopes } from "square/models/components";

const RequestedScopes: Scopes[] = ['PAYMENTS_READ', 'PAYMENTS_WRITE'];

function createAuthorizationUrl() {
  const clientId = process.env.APP_ID;
  const state = randomBytes(16).toString('hex');

  const authUrl = `https://connect.example.com/oauth2/authorize?` +
    `client_id=${encodeURIComponent(clientId)}` +
    `&scope=${RequestedScopes.join('+')}` +
    `&redirect_uri=${encodeURIComponent(redirectUrl)}` +
    `&state=${state}`;

  return authUrl;
}
```
```

## Custom Usage Examples

Enhance the auto-generated usage section with real-world scenarios:

### Example: Domain-Specific Workflow

```markdown
### Creating a Payment

```typescript
import { Square } from "square";

const square = new Square({
  accessToken: process.env["SQUARE_ACCESS_TOKEN"] ?? "",
});

async function createPayment() {
  const result = await square.payments.create({
    sourceId: "ccof:GaJGNaZa8x4OgDJn4GB",
    idempotencyKey: crypto.randomUUID(),
    amountMoney: {
      amount: 1000,  // Amount in smallest currency unit (cents)
      currency: "USD",
    },
    customerId: "W92WH6P11H4Z77CTET0RNTGFW8",
    locationId: "L88917AVBK2S5",
    note: "Coffee order",
  });

  console.log(`Payment ID: ${result.payment?.id}`);
}
```
```

## Development Section

Add maturity level and contribution guidelines:

```markdown
# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage to a specific package version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation.

We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release.

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
```

## Production README Patterns

### Pattern 1: Square SDK (Comprehensive)

**Key features:**
- Centered header with logo, tagline, badges
- Detailed OAuth flow documentation with code examples
- Server selection for sandbox vs production
- Custom HTTP client hooks documentation
- Standalone functions for tree-shaking

**Structure:**
```
Header (branding)
└── Summary (auto-generated)
└── Table of Contents (auto-generated)
└── Installation (auto-generated)
└── Requirements (links to RUNTIMES.md)
└── Authentication (auto + custom OAuth guide)
└── Example Usage (auto-generated)
└── Available Resources (auto-generated)
└── Error Handling (auto-generated)
└── Server Selection (auto-generated)
└── Custom HTTP Client (auto-generated)
└── Standalone Functions (auto-generated)
└── Retries (auto-generated)
└── Debugging (auto-generated)
└── Development (custom maturity + contributions)
```

### Pattern 2: Clerk Java SDK (Spring Boot Focus)

**Key features:**
- Authentication helpers documentation
- Spring Boot integration examples
- Multi-token type support (session, API key, M2M, OAuth)
- Request authentication workflow

**Structure:**
```
Header (branding)
└── Summary
└── Installation (Gradle + Maven)
└── Authentication (with request validation helpers)
└── SDK Example Usage
└── Available Resources (expandable details)
└── Error Handling
└── Server Selection
└── Retries
└── Debugging
└── Development
```

### Pattern 3: Terraform Provider README

**Key features:**
- Provider configuration block
- Resource and data source documentation
- Import examples
- Registry badges

**Structure:**
```
Header (Terraform Registry badge)
└── Requirements
└── Provider Configuration
└── Resources
└── Data Sources
└── Import
└── Development
```

## Section Markers Reference

These HTML comment markers define auto-generated sections that Speakeasy maintains:

| Marker | Content |
|--------|---------|
| `<!-- Start Summary [summary] -->` | API description from OpenAPI info |
| `<!-- Start Table of Contents [toc] -->` | Navigation links |
| `<!-- Start SDK Installation [installation] -->` | Package manager instructions |
| `<!-- Start Requirements [requirements] -->` | Runtime requirements |
| `<!-- Start Authentication [security] -->` | Security scheme documentation |
| `<!-- Start SDK Example Usage [usage] -->` | Basic usage examples |
| `<!-- Start Available Resources and Operations [operations] -->` | API method listing |
| `<!-- Start Error Handling [errors] -->` | Error types and handling |
| `<!-- Start Server Selection [server] -->` | Server URL configuration |
| `<!-- Start Custom HTTP Client [http-client] -->` | HTTP customization |
| `<!-- Start Standalone functions [standalone-funcs] -->` | Tree-shakeable functions |
| `<!-- Start Retries [retries] -->` | Retry configuration |
| `<!-- Start Debugging [debug] -->` | Debug logging |

**Important:** Content between `<!-- Start ... -->` and `<!-- End ... -->` is auto-generated and will be overwritten. Add custom content **outside** these markers.

## Best Practices

### Do's

1. **Add branding at the top** - Logo, tagline, and badges before auto-generated content
2. **Enhance authentication docs** - Add step-by-step guides for obtaining tokens
3. **Include real-world examples** - Domain-specific code samples beyond basic usage
4. **Document OAuth flows** - Visual diagrams and complete code examples
5. **Add migration guides** - For major version upgrades
6. **Include contribution guidelines** - Clear path for community involvement

### Don'ts

1. **Don't edit between markers** - Content will be overwritten
2. **Don't duplicate auto-generated content** - It creates maintenance burden
3. **Don't omit maturity warnings** - Users need to know stability level
4. **Don't skip error handling examples** - Show practical exception handling

---

## Pre-defined TODO List

When customizing an SDK README, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Add branding header (logo, tagline, badges) | Adding branding header |
| 2 | Review auto-generated summary for accuracy | Reviewing auto-generated summary |
| 3 | Create custom authentication guide | Creating custom authentication guide |
| 4 | Add OAuth flow documentation if applicable | Adding OAuth flow documentation |
| 5 | Add domain-specific usage examples | Adding domain-specific usage examples |
| 6 | Document environment variable conventions | Documenting environment variables |
| 7 | Add server selection guidance (sandbox vs production) | Adding server selection guidance |
| 8 | Include migration guide if upgrading | Including migration guide |
| 9 | Add maturity/stability section | Adding maturity section |
| 10 | Add contribution guidelines | Adding contribution guidelines |

**Usage:**
```
TodoWrite([
  {content: "Add branding header (logo, tagline, badges)", status: "pending", activeForm: "Adding branding header"},
  {content: "Review auto-generated summary for accuracy", status: "pending", activeForm: "Reviewing auto-generated summary"},
  {content: "Create custom authentication guide", status: "pending", activeForm: "Creating custom authentication guide"},
  {content: "Add OAuth flow documentation if applicable", status: "pending", activeForm: "Adding OAuth flow documentation"},
  {content: "Add domain-specific usage examples", status: "pending", activeForm: "Adding domain-specific usage examples"},
  {content: "Document environment variable conventions", status: "pending", activeForm: "Documenting environment variables"},
  {content: "Add server selection guidance (sandbox vs production)", status: "pending", activeForm: "Adding server selection guidance"},
  {content: "Include migration guide if upgrading", status: "pending", activeForm: "Including migration guide"},
  {content: "Add maturity/stability section", status: "pending", activeForm: "Adding maturity section"},
  {content: "Add contribution guidelines", status: "pending", activeForm: "Adding contribution guidelines"}
])
```

**Conditional steps:**
- Step 4 (OAuth): Only for APIs using OAuth authentication
- Step 7 (Server selection): Only for APIs with sandbox/production environments
- Step 8 (Migration): Only for major version upgrades

**Nested workflows:**
- For SDK generation, see `plans/sdk-generation.md`
- For language-specific patterns, see `sdk-languages/*.md`
