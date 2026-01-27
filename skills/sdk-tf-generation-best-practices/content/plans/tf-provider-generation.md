---
short_description: Generate Terraform providers from OpenAPI specifications
long_description: |
  Complete guide for generating Terraform providers from OpenAPI documents using Speakeasy.
  Covers prerequisites, entity annotations, CRUD mapping, documentation, and best practices
  for modeling and naming Terraform resources.
source:
  repo: "speakeasy-api/speakeasy.com, Kong/terraform-provider-konnect, Kong/terraform-provider-konnect-beta"
  path: "src/content/docs/terraform/create-terraform.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Generate a Terraform Provider from an OpenAPI Document

Terraform is an infrastructure-as-code tool that uses providers to manage cloud infrastructure through API calls. Creating and maintaining Terraform providers, which are typically written in Go, requires specialized skills and frequent updates to keep up with API changes.

Speakeasy simplifies creating and maintaining Terraform providers by generating providers from OpenAPI documents. This eliminates the need for Go expertise, keeps providers up-to-date, and reduces the complexity of developing and maintaining providers for cloud environments.

For supported features and limitations, review the Terraform guides in this agent-context folder and validate against your target API spec.

## Prerequisites

Creating a Terraform provider with Speakeasy requires:

- The Speakeasy CLI
- An API spec in a supported format:

| Spec format | Supported |
|-------------|-----------|
| OpenAPI 3.0 | Yes |
| OpenAPI 3.1 | Yes |
| JSON Schema | Yes |
| Postman Collection | Not yet |

> **Tip:** If you are using an unsupported spec format, convert it first:
> - Swagger 2.0 to OpenAPI 3.x: `speakeasy openapi transform convert-swagger -s swagger2.yaml -o openapi.yaml`
> - Postman to OpenAPI: use the `postman2openapi` CLI tool

## Add Annotations

> **Tip:** Before annotating, use `yq`/`jq` to inspect the spec structure—don't read or paste the entire file into context:
> ```bash
> # List all paths to find candidate CRUD endpoints
> yq '.paths | keys' spec.yaml
> # Inspect a specific path
> yq '.paths["/pet"]' spec.yaml
> # List all schema names to identify entities
> yq '.components.schemas | keys' spec.yaml
> # Find existing x-speakeasy-entity annotations
> yq '.. | select(has("x-speakeasy-entity")) | .x-speakeasy-entity' spec.yaml
> ```
> See `INDEX.md#working-with-large-openapi-documents` for more examples.

Use the `x-speakeasy-entity` annotation to specify objects to be included as Terraform entities in the provider.

```yaml
paths:
  /pet:
    post:
      ...
      x-speakeasy-entity-operation: Pet#create
      ...
components:
  schemas:
    Pet:
      x-speakeasy-entity: Pet
      ...
```

Terraform usage:

```hcl
resource "petstore_pet" "myPet" {
  ...
}
```

Speakeasy infers Terraform types from the JSON Schema, focusing on the semantics of the `CREATE` and `UPDATE` requests and responses. No specific Terraform types need to be defined in the OpenAPI document.

1. **Required vs optional:** If a property is required in the `CREATE` request body, it's marked as `Required: true`; otherwise, it's `Optional: true`.
2. **Computed properties:** Properties that appear in a response body but are absent from the `CREATE` request are marked as `Computed: true`. This indicates that Terraform will compute the properties' values.
3. **The `ForceNew` property:** If a property exists in the `CREATE` request but is not present in the `UPDATE` request, it's labeled `ForceNew`.
4. **Enum validation:** When an attribute is defined as an enum, Speakeasy configures a `Validator` for runtime type checks. This ensures that all request properties precisely match one of the enumerated values.
5. **`READ`, `UPDATE`, and `DELETE` dependencies**: Every parameter essential for `READ`, `UPDATE`, or `DELETE` operations must either be part of the `CREATE` API response body or be consistently required in the `CREATE` API request. This ensures that all necessary parameters are available for these operations.

> **Tip:** Use additional `x-speakeasy` annotations to customize the provider as necessary.

## Enhance Generated Documentation

Speakeasy helps you autogenerate documentation using the HashiCorp `terraform-plugin-docs` tools and packages. For best results, we recommend that you:

1. **Include descriptions:** Ensure the OpenAPI document contains detailed descriptions of resources, attributes, and operations. Clear and concise descriptions help understand the purpose and use of each component.
2. **Provide examples:** Use examples in the OpenAPI document to illustrate how resources and attributes should be configured. Speakeasy leverages these examples to generate usage snippets for reference when starting with the provider.

The Swagger Petstore generates a usage snippet for the pet resource similar to the following:

```hcl
"petstore_pet" "my_pet" {
    id   = 10
    name = "doggie"
    photo_urls = [
        "...",
    ]
}
```

## Generate a Terraform Provider

Run the Speakeasy `quickstart` command:

```bash
speakeasy quickstart
```

Follow the wizard prompts (spec path, output location, and target = `terraform`).

After completing the quickstart, regenerate the Terraform provider at any point by running:

```bash
speakeasy run
```

> **Note:** Use `--auto-yes` (`-y`) to auto-confirm prompts in non-interactive environments.

## Building Against Remote APIs

For providers built against third-party APIs (like Opal, PlanetScale, or other SaaS platforms), configure your workflow to fetch the OpenAPI spec directly from the API vendor:

### Remote API Workflow Configuration

```yaml
# .speakeasy/workflow.yaml
workflowVersion: 1.0.0
speakeasyVersion: latest
sources:
  vendor-api:
    inputs:
      - location: https://api.vendor.com/openapi.yaml  # Remote spec
    overlays:
      - location: terraform_overlay.yaml               # Local customizations
    output: openapi.yaml                               # Merged output
targets:
  vendor-provider:
    target: terraform
    source: vendor-api
```

### Maintaining Overlays for Remote APIs

When your API vendor updates their spec, use `speakeasy overlay compare` to identify changes:

```bash
# See what changed in the remote API
speakeasy overlay compare \
    --before https://api.vendor.com/openapi.yaml \
    --after terraform_overlay.yaml \
    --out overlay-diff.yaml
```

**Makefile integration:**

```makefile
.PHONY: overlay-diff
overlay-diff:
	speakeasy overlay compare \
		--before https://api.vendor.com/openapi.yaml \
		--after terraform_overlay.yaml \
		--out overlay-diff.yaml

.PHONY: speakeasy
speakeasy:
	speakeasy run
```

This pattern ensures your provider always builds against the latest API spec while preserving your Terraform-specific customizations in the overlay.

## Guidance on Modeling Entities

### Repository Naming

Name the provider and GitHub repository `terraform-provider-XXX`, where `XXX` becomes the short name of the provider, also known as the **provider type name**.

The provider type name should preferably be `[a-z][a-z0-9]`, although hyphens and underscores are also valid and can be included in the name if necessary.

### Entity Naming

When naming entities that you want Speakeasy to convert to Terraform resources, use PascalCase to ensure the names are translated to Terraform's underscore naming. For list endpoints, pluralize the PascalCase name.

### Modeling Entities

First, find the list operation for an API entity or resource. Usually, it is a `GET` on `/something`. Annotate the list operation with `x-speakeasy-entity-operation: XXX#read`.

Now, find the CREATE, READ, UPDATE, and DELETE (CRUD) operations for an API resource. Usually, these take the form of a `POST` on `/something` and operations on `/something/{id}`. Annotate the CRUD operations with `x-speakeasy-entity-operation: XXX#create`.

Ensure the CREATE response returns data. Some API frameworks don't output it, even though they generally have to return data such as an identifier for the resource.

Finally, check whether the `GET` (not list) read response includes an extra data property or similar element between the root of the response schema and the actual data. If the `GET` read response does have an additional data property, add the `x-speakeasy-entity: XXX` annotation to the object beneath that data property (not on the data itself). Most APIs use a shared `component`, which is often the best place for entity annotation.

## Frequently Asked Questions

### Do the generated Terraform providers support importing resources?

Yes, generated Terraform providers support importing resources. However, certain prerequisites and considerations must be taken into account:

**Prerequisites**

1. **API specification:** Ensure the OpenAPI document defines an annotated and type-complete API operation for reading each resource. Tag the operation with `x-speakeasy-entity-operation: MyEntity#read`.
2. **Complete `READ` operation:** Attributes of a resource not defined in the `READ` API are set to `null` by Terraform during the import process.

**Simple keys**

A simple key is a single required ID field that is directly exposed to `terraform import` operations. For example, if the `pet` resource has a single `id` field, the import command will look like this:

```bash
terraform import petstore_pet.my_pet my_pet_id
```

**Handling composite keys**

Speakeasy natively supports the direct import of resources with multiple ID fields. Speakeasy generates code that enables import functionality by requiring users to provide a JSON-encoded object with all necessary parameters. In addition to generating documentation, Speakeasy generates appropriate error messages to be displayed if the proper syntax is not followed.

**Import composite keys by block**

An import block allows you to import a resource into the Terraform state by generating the corresponding Terraform configuration. Using a composite key, the import block will look like this:

```hcl
import {
  id = jsonencode({
    primary_key_one: "9cedad30-2a8a-40f7-9d65-4fabb04e54ff"
    primary_key_two: "e20c40a0-40e8-49ac-b5d0-6e2f41f9e66f"
  })
  to = my_test_resource.my_example
}
```

Then generate the configuration:

```bash
terraform plan -generate-config-out=generated.tf
```

**Import composite keys using the CLI**

To import a resource with composite keys using the Terraform CLI, use the `terraform import` command:

```bash
terraform import my_test_resource.my_example '{ "primary_key_one": "9cedad30-2a8a-40f7-9d65-4fabb04e54ff", "primary_key_two": "e20c40a0-40e8-49ac-b5d0-6e2f41f9e66f" }'
```

---

## Pre-defined TODO List

When executing this workflow, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Speakeasy CLI is installed | Verifying Speakeasy CLI installation |
| 2 | Authenticate with Speakeasy account | Authenticating with Speakeasy account |
| 3 | Prepare OpenAPI specification for Terraform | Preparing OpenAPI specification for Terraform |
| 4 | Add x-speakeasy-entity annotations to schemas | Adding x-speakeasy-entity annotations to schemas |
| 5 | Add x-speakeasy-entity-operation annotations to operations | Adding x-speakeasy-entity-operation annotations to operations |
| 6 | Map CRUD operations (create, read, update, delete) | Mapping CRUD operations |
| 7 | Structure overlays (base + terraform + per-entity) | Structuring overlay files |
| 8 | Configure async polling for long-running operations | Configuring async polling |
| 9 | Configure JQ transforms for complex request bodies | Configuring JQ transforms |
| 10 | Add custom security scheme for user-friendly auth naming | Adding custom security scheme |
| 11 | Configure x-speakeasy-conflicts-with for mutual exclusion | Configuring field conflicts |
| 12 | Add custom types if needed (e.g., RFC3339 dates) | Adding custom types |
| 13 | Configure schemaless fields for plugin configs | Configuring schemaless fields |
| 14 | Validate OpenAPI specification | Validating OpenAPI specification |
| 15 | Create GitHub repository for provider | Creating GitHub repository for provider |
| 16 | Generate GPG signing key for releases | Generating GPG signing key for releases |
| 17 | Configure repository secrets for GPG | Configuring repository secrets for GPG |
| 18 | Run speakeasy quickstart for Terraform | Running speakeasy quickstart for Terraform |
| 19 | Verify provider compilation succeeds | Verifying provider compilation succeeds |
| 20 | Review generated provider structure | Reviewing generated provider structure |
| 21 | Set up acceptance test infrastructure | Setting up acceptance test infrastructure |
| 22 | Create examples/use-cases directory | Creating use-cases examples |
| 23 | Add use-case example test harness | Adding example test harness |
| 24 | Add resource sweepers for test cleanup | Adding resource sweepers |
| 25 | Configure CI workflow for acceptance tests | Configuring CI for acceptance tests |
| 26 | Add multi-version test matrix (TF 1.10-1.13) | Adding multi-version test matrix |
| 27 | Configure GoReleaser workflow | Configuring GoReleaser workflow |
| 28 | Register provider with Terraform Registry | Registering provider with Terraform Registry |

**Usage:**
```javascript
TodoWrite([
  {content: "Verify Speakeasy CLI is installed", status: "pending", activeForm: "Verifying Speakeasy CLI installation"},
  {content: "Authenticate with Speakeasy account", status: "pending", activeForm: "Authenticating with Speakeasy account"},
  {content: "Prepare OpenAPI specification for Terraform", status: "pending", activeForm: "Preparing OpenAPI specification for Terraform"},
  {content: "Add x-speakeasy-entity annotations to schemas", status: "pending", activeForm: "Adding x-speakeasy-entity annotations to schemas"},
  {content: "Add x-speakeasy-entity-operation annotations to operations", status: "pending", activeForm: "Adding x-speakeasy-entity-operation annotations to operations"},
  {content: "Map CRUD operations (create, read, update, delete)", status: "pending", activeForm: "Mapping CRUD operations"},
  {content: "Structure overlays (base + terraform + per-entity)", status: "pending", activeForm: "Structuring overlay files"},
  {content: "Configure async polling for long-running operations", status: "pending", activeForm: "Configuring async polling"},
  {content: "Configure JQ transforms for complex request bodies", status: "pending", activeForm: "Configuring JQ transforms"},
  {content: "Add custom security scheme for user-friendly auth naming", status: "pending", activeForm: "Adding custom security scheme"},
  {content: "Configure x-speakeasy-conflicts-with for mutual exclusion", status: "pending", activeForm: "Configuring field conflicts"},
  {content: "Add custom types if needed (e.g., RFC3339 dates)", status: "pending", activeForm: "Adding custom types"},
  {content: "Configure schemaless fields for plugin configs", status: "pending", activeForm: "Configuring schemaless fields"},
  {content: "Validate OpenAPI specification", status: "pending", activeForm: "Validating OpenAPI specification"},
  {content: "Create GitHub repository for provider", status: "pending", activeForm: "Creating GitHub repository for provider"},
  {content: "Generate GPG signing key for releases", status: "pending", activeForm: "Generating GPG signing key for releases"},
  {content: "Configure repository secrets for GPG", status: "pending", activeForm: "Configuring repository secrets for GPG"},
  {content: "Run speakeasy quickstart for Terraform", status: "pending", activeForm: "Running speakeasy quickstart for Terraform"},
  {content: "Verify provider compilation succeeds", status: "pending", activeForm: "Verifying provider compilation succeeds"},
  {content: "Review generated provider structure", status: "pending", activeForm: "Reviewing generated provider structure"},
  {content: "Set up acceptance test infrastructure", status: "pending", activeForm: "Setting up acceptance test infrastructure"},
  {content: "Create examples/use-cases directory", status: "pending", activeForm: "Creating use-cases examples"},
  {content: "Add use-case example test harness", status: "pending", activeForm: "Adding example test harness"},
  {content: "Add resource sweepers for test cleanup", status: "pending", activeForm: "Adding resource sweepers"},
  {content: "Configure CI workflow for acceptance tests", status: "pending", activeForm: "Configuring CI for acceptance tests"},
  {content: "Add multi-version test matrix (TF 1.10-1.13)", status: "pending", activeForm: "Adding multi-version test matrix"},
  {content: "Configure GoReleaser workflow", status: "pending", activeForm: "Configuring GoReleaser workflow"},
  {content: "Register provider with Terraform Registry", status: "pending", activeForm: "Registering provider with Terraform Registry"}
])
```

**Nested workflows:**

- **Step 3 (Prepare OpenAPI)**: See `spec-first/validation.md` for OpenAPI validation sub-steps
- **Step 4-6 (Entity annotations)**: See `terraform/crud-mapping.md` for CRUD annotation details
- **Step 7-8 (Overlays & Polling)**: See `terraform/customization.md` for advanced overlay workflows, multi-overlay organization, and async polling
- **Step 9-11 (JQ transforms, Security, Conflicts)**: See `terraform/customization.md` for JQ transforms, custom security schemes, and x-speakeasy-conflicts-with
- **Step 12-13 (Custom types & Schemaless)**: See `terraform/customization.md` for custom type implementation and jsonencode pattern
- **Step 21-26 (Testing)**: See `terraform/testing-guide.md` for acceptance testing patterns, use-case examples, and multi-version testing
- **Step 27-28 (Publishing)**: See `terraform/publishing.md` for registry publishing sub-steps

**Conditional steps:**
- Step 8 (Polling): Only needed for resources with async provisioning
- Step 9 (JQ transforms): Only needed when API request format differs significantly from TF schema
- Step 10 (Custom security): Only needed to rename default auth fields (e.g., username/password to domain-specific names)
- Step 11 (Conflicts): Only needed for mutually exclusive field combinations
- Step 12 (Custom types): Only needed for semantic equality (e.g., RFC3339 dates)
- Step 13 (Schemaless): Only needed for plugin/policy systems with variable schemas

**Note:** This workflow assumes you have a valid OpenAPI specification. If you need to extract OpenAPI from code first, see the `code-first/` guides before starting this workflow.

---

## Beta Provider Pattern

Large APIs often benefit from maintaining separate **stable** and **beta** Terraform providers. This pattern allows early access to new features while maintaining stability guarantees for production users. Kong demonstrates this with `terraform-provider-konnect` (stable) and `terraform-provider-konnect-beta`.

### When to Use Beta Providers

| Scenario | Recommendation |
|----------|----------------|
| API features in preview/beta | Beta provider |
| Breaking changes to existing resources | Beta provider first |
| Experimental API endpoints | Beta provider |
| Production-ready features | Stable provider |
| Critical infrastructure resources | Stable provider |

### Repository Structure

Maintain two separate repositories with distinct package names:

```
terraform-provider-{name}/           # Stable provider
├── gen.yaml                         # packageName: {name}
├── openapi.yaml                     # Stable API spec
└── .speakeasy/workflow.yaml

terraform-provider-{name}-beta/      # Beta provider
├── gen.yaml                         # packageName: {name}-beta
├── openapi.yaml                     # Beta API spec (different endpoints)
└── .speakeasy/workflow.yaml
```

### Configuration Differences

**Stable provider (gen.yaml):**
```yaml
terraform:
  version: 3.4.2              # Semantic versioning, major bumps for breaking changes
  packageName: konnect
  author: kong
  baseErrorName: KonnectError
```

**Beta provider (gen.yaml):**
```yaml
terraform:
  version: 0.13.0             # 0.x versioning signals beta status
  packageName: konnect-beta   # Different package name
  author: kong
  baseErrorName: KonnectBetaError
```

### User Experience

Users can install both providers simultaneously:

```hcl
terraform {
  required_providers {
    # Stable provider for production resources
    konnect = {
      source = "kong/konnect"
    }
    # Beta provider for preview features
    konnect-beta = {
      source = "kong/konnect-beta"
    }
  }
}

provider "konnect" {
  personal_access_token = var.konnect_token
}

provider "konnect-beta" {
  personal_access_token = var.konnect_token
}

# Use stable provider for production
resource "konnect_gateway_control_plane" "prod" {
  name = "production"
}

# Use beta provider for preview features
resource "konnect-beta_mesh_control_plane" "preview" {
  provider = konnect-beta
  name     = "mesh-preview"
}
```

### Shared Code Libraries

For code reuse between stable and beta providers, extract shared functionality into a separate Go module:

```yaml
# gen.yaml - additionalDependencies for shared code
terraform:
  additionalDependencies:
    github.com/YourOrg/shared-speakeasy/customtypes: v0.2.5
    github.com/YourOrg/shared-speakeasy/planmodifiers/arbitrary_json: v0.0.1
    github.com/YourOrg/shared-speakeasy/planmodifiers/suppress_zero_null: v0.0.1
    github.com/YourOrg/shared-speakeasy/tfbuilder: v0.0.5
```

**Shared module structure:**
```
shared-speakeasy/
├── customtypes/
│   └── kumalabels/          # Custom Terraform types
├── planmodifiers/
│   ├── arbitrary_json/      # JSON handling modifiers
│   └── suppress_zero_null/  # Null suppression logic
├── tfbuilder/               # Test configuration builders
└── hooks/
    └── mesh_defaults/       # Default value injection
```

### Graduation Process

When beta features become stable:

1. **Copy entity definitions** from beta OpenAPI to stable OpenAPI
2. **Run generation** on both providers
3. **Add migration guide** in stable provider changelog
4. **Deprecate** beta resources after stable version is released
5. **Remove** deprecated beta resources after grace period

### Rename Script Pattern

Kong provides a `rename-provider.sh` script for scenarios where beta resources need to be used with stable resource names (useful for testing migrations):

```bash
#!/bin/bash
# rename-provider.sh - Rename beta resources to stable naming

# Update resource type names in Go files
find internal/provider -type f -name "*_resource.go" | \
  xargs sed -i.bak -e 's/resp.TypeName = req.ProviderTypeName + "/resp.TypeName = "konnect/'

# Update example files
find examples/resources -type f -name "*.tf" | \
  xargs sed -i.bak -e 's/konnect-beta_/konnect_/'

# Add provider = konnect-beta to examples
find examples/resources -type f -name "*.tf" | grep -v "provider.tf" | \
  xargs sed -i.bak -e '1a\
  provider = konnect-beta
'

# Rename example directories
for i in $(find examples -type d -name "konnect-beta*"); do
  RENAMED=$(echo $i | sed 's/konnect-beta/konnect/')
  mv $i $RENAMED
done

# Cleanup backup files
find . -type f -name '*.bak' -delete
```

### Version Numbering

| Provider | Version Pattern | Breaking Changes |
|----------|-----------------|------------------|
| Stable | `x.y.z` (semver) | Major version bump |
| Beta | `0.y.z` | Any version bump |

Beta providers use `0.x` versioning to signal that breaking changes may occur without major version bumps, following Terraform provider conventions.

---

## Feedback

If you encountered issues while following this workflow — such as an annotation that did not behave as documented, a missing CRUD mapping pattern, or unclear entity modeling instructions — submit feedback:

```bash
speakeasy agent feedback -m "Description of the issue" --context-path "plans/tf-provider-generation.md"
```
