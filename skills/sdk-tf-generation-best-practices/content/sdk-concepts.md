---
short_description: "Core concepts of Speakeasy SDK generation workflows"
long_description: |
  Essential concepts for understanding Speakeasy's SDK generation platform, including
  workflow definitions, sources (OpenAPI specs and overlays), targets (SDKs, docs, providers),
  validation, testing, and versioning.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/docs/sdks/core-concepts.mdx"
  ref: "aed058705f8de5772cba0fd389707cfd4d0752f7"
  last_reconciled: "2025-12-11"
related:
  - "plans/sdk-generation.md"
  - "sdk-overview.md"
  - "CLI_REFERENCE.md"
---

# Core concepts

The core concepts explained on this page are essential to understanding Speakeasy SDKs.

## Generation workflows

A workflow is how the Speakeasy platform defines the process of generating a target from a source. A workflow is defined in a `workflow.yaml` file stored in the root of the target repository in the `.speakeasy` directory. A workflow is run using the `speakeasy run` command.

Workflows can be run locally for fast iteration, or via a set of GitHub Actions for production usage.

![Workflow diagram](/assets/docs/core-concepts.png)

### Sources

A source is one or more OpenAPI documents and OpenAPI overlays merged to create a single OpenAPI document.

- **OpenAPI specification (OAS)** is a widely accepted REST specification for building APIs. An OpenAPI document is a JSON or YAML file that defines the structure of an API. The Speakeasy platform uses OpenAPI documents as the source for generating SDKs and other code.
- **OpenAPI overlay** is a JSON or YAML file used to specify additions, removals, or modifications to an OpenAPI document. Overlays enable users to alter an OpenAPI document without making changes to the original document.

### Targets

A target refers to an SDK, agent tool, docs, or other code generated from sources.

- **SDKs** are available in 8 languages (and growing). Language experts developed each SDK generator to ensure a high level of idiomatic code generation. Supported languages include: python, typescript, go, java, csharp, ruby, php, swift, and rust.
- **Agent tools** are a new surface for interacting with APIs. They provide a way for LLMs and other agentic platforms to interact with APIs. Speakeasy supports MCP server generation.
- **Documentation** is available in the form of an API reference. Generated docs include SDK code snippets for every API method. Code snippets can also be embedded into an existing documentation site.
- **Terraform providers** can be generated from an annotated OpenAPI document. Terraform providers do not map 1:1 with APIs and so annotations are required to specify the Terraform entities and their methods.

### Workflow file syntax

The `workflow.yaml` workflow file is a YAML file that defines the steps of a workflow. The file is broken down into the following sections:

```yaml
workflowVersion: 1.0.0
speakeasyVersion: latest
sources:
  my-source:
    inputs:
      - location: ./openapi.yaml
      - location: ./overlay.yaml
      - location: ./another-openapi.yaml
      - location: ./another-overlay.yaml
      # .... more openapi documents and overlays can be added here
  # more inputs can be added here through `speakeasy configure sources` command
  # ....
  # ....
targets:
  python-sdk:
    target: python
    source: my-source
  # more inputs can be added here through `speakeasy configure targets` command
  # ....
  # ....
```

The workflow file syntax allows for 1:1, 1:N, or N:N mapping of `sources` to `targets`. A common use case for 1:N mapping is setting up a monorepo of SDKs.

### Workflow steps

#### Validation

Validation is the process of checking whether an OpenAPI document is ready for code generation. The Speakeasy platform defines the default validation rules used to validate an OpenAPI document. Validation is done using the `speakeasy validate` command, and validation rules are defined in the `lint.yaml` file.

By default the `validate` CLI command will use the `speakeasy-default` linting ruleset if custom rules are not defined.

#### Linting

Linting is the process of checking an OpenAPI document for errors and style issues. The Speakeasy platform defines the default linting rules used to validate an OpenAPI document. Linting is done using the `speakeasy lint` command, and linting rules are defined in the `lint.yaml` file.

#### Testing

Testing is the process of checking a generated target for errors. The Speakeasy platform generates a test suite for each target, which can be run using the `speakeasy test` command. A test will be created for each operation in the API.

#### Release and versioning

Speakeasy automatically creates releases and versions for target artifacts. The release and version are defined in the `gen.yaml` file and used to track the state of a generation and create a release on the target repository. Releases are used synonymously with GitHub releases, the primary way Speakeasy distributes artifacts.

#### Publishing

Publishing is the process of making a generated target available to the public. The Speakeasy platform generates a package for each target, which can be pushed to the relevant package manager.

---

## Pre-defined TODO List

When learning Speakeasy SDK concepts, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Understand workflow.yaml structure | Understanding workflow.yaml |
| 2 | Learn source configuration (OpenAPI + overlays) | Learning source configuration |
| 3 | Learn target types (SDKs, docs, terraform) | Learning target types |
| 4 | Understand validation and linting | Understanding validation |
| 5 | Learn about release and versioning | Learning about versioning |
| 6 | Review testing capabilities | Reviewing testing capabilities |

**Usage:**
```
TodoWrite([
  {content: "Understand workflow.yaml structure", status: "pending", activeForm: "Understanding workflow.yaml"},
  {content: "Learn source configuration (OpenAPI + overlays)", status: "pending", activeForm: "Learning source configuration"},
  {content: "Learn target types (SDKs, docs, terraform)", status: "pending", activeForm: "Learning target types"},
  {content: "Understand validation and linting", status: "pending", activeForm: "Understanding validation"},
  {content: "Learn about release and versioning", status: "pending", activeForm: "Learning about versioning"},
  {content: "Review testing capabilities", status: "pending", activeForm: "Reviewing testing capabilities"}
])
```

**Nested workflows:**
- For generating SDKs, see `plans/sdk-generation.md`
- For OpenAPI overlays, see `spec-first/overlays.md`
- For validation, see `spec-first/validation.md`

