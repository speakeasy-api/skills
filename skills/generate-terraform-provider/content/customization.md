# Terraform Provider Customization

Advanced customization for Speakeasy-generated Terraform providers.

## Entity Mapping Placement

Where you place `x-speakeasy-entity` affects the resource schema structure.

### Top Level (Nested Properties)

```yaml
Pet:
  x-speakeasy-entity: Pet
  type: object
  properties:
    data:
      type: object
      properties:
        name:
          type: string
```

Results in:
```hcl
resource "provider_pet" "example" {
  data = {
    name = "Buddy"
  }
}
```

### Lower Level (Flattened Properties)

```yaml
Pet:
  type: object
  properties:
    data:
      x-speakeasy-entity: Pet
      type: object
      properties:
        name:
          type: string
```

Results in:
```hcl
resource "provider_pet" "example" {
  name = "Buddy"
}
```

## Multiple API Operations per Resource

Complex resources often require multiple API calls. Use ordering with `#read#1`, `#read#2`, etc.

```yaml
# overlay-group.yaml
overlay: 1.1.0
info:
  title: Group entity overlay
actions:
  # Primary endpoint
  - target: $.paths["/groups/{id}"].get
    update:
      x-speakeasy-entity-operation: Group#read#1

  # Additional data from separate endpoints
  - target: $.paths["/groups/{id}/visibility"].get
    update:
      x-speakeasy-entity-operation: Group#read#2

  - target: $.paths["/groups/{id}/reviewers"].get
    update:
      x-speakeasy-entity-operation: Group#read#3

  # CRUD operations
  - target: $.paths["/groups"].post
    update:
      x-speakeasy-entity-operation: Group#create

  - target: $.paths["/groups/{id}"].put
    update:
      x-speakeasy-entity-operation: Group#update

  - target: $.paths["/groups/{id}"].delete
    update:
      x-speakeasy-entity-operation: Group#delete
```

## Async Operation Polling

For APIs with asynchronous operations, configure polling to wait for completion.

### Basic Polling

```yaml
/task/{id}:
  get:
    x-speakeasy-polling:
      - name: WaitForCompleted
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/status == "completed"
        failureCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/status == "errored"
    x-speakeasy-entity-operation:
      - Task#read
      - entityOperation: Task#create#2
        options:
          polling:
            name: WaitForCompleted
```

### Polling Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `delaySeconds` | Seconds before first poll | 0 |
| `intervalSeconds` | Seconds between polls | 5 |
| `limitCount` | Max poll attempts | 60 |

### Real-World Example: Cluster Provisioning

```yaml
- target: $.paths["/clusters/{id}"].get
  update:
    x-speakeasy-entity-operation:
      - Cluster#read
      - entityOperation: Cluster#create#2
        options:
          polling:
            delaySeconds: 2
            intervalSeconds: 2
            limitCount: 120
            name: WaitForProvisioned
    x-speakeasy-polling:
      - name: WaitForProvisioned
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/status/phase == "PROVISIONED"
        failureCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/status/phase == "FAILED"
```

## Property Customization

### Sensitive Fields

Mark fields that should be hidden in logs and state:

```yaml
components:
  schemas:
    Credentials:
      properties:
        api_key:
          type: string
          x-speakeasy-terraform-sensitive: true
        password:
          type: string
          x-speakeasy-terraform-sensitive: true
```

### Deprecated Fields

```yaml
properties:
  old_field:
    type: string
    deprecated: true
    x-speakeasy-terraform-deprecated-message: "Use new_field instead"
```

### Force Replacement

Force resource recreation when a field changes:

```yaml
properties:
  region:
    type: string
    x-speakeasy-terraform-force-new: true
```

### Computed Fields

Fields that are only in responses (not in create request) are automatically computed. To explicitly mark:

```yaml
properties:
  created_at:
    type: string
    readOnly: true
```

## Provider Configuration

### Environment Variable Support

Configure which fields can be set via environment variables:

```yaml
# gen.yaml
terraform:
  envVarPrefix: "MYAPI"
```

This enables:
- `MYAPI_API_KEY` → `api_key` provider field
- `MYAPI_BASE_URL` → `base_url` provider field

### Custom Provider Attributes

Add provider-level configuration via overlay:

```yaml
actions:
  - target: $.components.securitySchemes.apiKey
    update:
      x-speakeasy-terraform-provider-attribute:
        name: api_key
        description: "API key for authentication"
        sensitive: true
```

## Plan Modification

### Default Values

Set defaults that apply when users don't specify a value:

```yaml
properties:
  timeout:
    type: integer
    default: 30
```

### Use State for Unknown

Preserve previous state value when the new value is unknown:

```yaml
properties:
  computed_field:
    type: string
    x-speakeasy-terraform-plan-modifier: UseStateForUnknown
```

## Validation

### Enum Validation

Enums automatically generate validators:

```yaml
properties:
  status:
    type: string
    enum: ["active", "inactive", "pending"]
```

### Custom Validation Messages

```yaml
properties:
  email:
    type: string
    format: email
    x-speakeasy-terraform-validation-message: "Must be a valid email address"
```

### Conflicting Attributes

```yaml
properties:
  option_a:
    type: string
    x-speakeasy-terraform-conflicts-with:
      - option_b
  option_b:
    type: string
    x-speakeasy-terraform-conflicts-with:
      - option_a
```

## State Upgraders

When schema changes require state migration, create state upgraders in `internal/stateupgraders/`:

```go
// internal/stateupgraders/pet_v0_to_v1.go
package stateupgraders

import (
    "context"
    "github.com/hashicorp/terraform-plugin-framework/resource"
)

func PetV0ToV1() resource.StateUpgrader {
    return resource.StateUpgrader{
        PriorSchema: &priorPetSchemaV0,
        StateUpgrader: func(ctx context.Context, req resource.UpgradeStateRequest, resp *resource.UpgradeStateResponse) {
            // Migration logic
            var priorState map[string]interface{}
            req.State.Get(ctx, &priorState)

            // Transform old_field to new_field
            if old, ok := priorState["old_field"]; ok {
                priorState["new_field"] = old
                delete(priorState, "old_field")
            }

            resp.State.Set(ctx, priorState)
        },
    }
}
```

Register in gen.yaml:

```yaml
terraform:
  stateUpgraders:
    - resource: pet
      version: 0
      upgrader: PetV0ToV1
```

## Data Source vs Resource Control

Explicitly control whether an operation generates a resource, data source, or both:

```yaml
paths:
  /search:
    get:
      x-speakeasy-entity-operation:
        terraform-datasource: Thing#read
        terraform-resource: null  # Don't use for resource
  /things/{id}:
    get:
      x-speakeasy-entity-operation:
        terraform-datasource: null  # Don't auto-generate data source
        terraform-resource: Thing#read
```

## Array Response Wrapping

Terraform requires object-type root schemas. Arrays are automatically wrapped:

```yaml
# API returns array
responses:
  "200":
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: "#/components/schemas/Pet"
```

Access in Terraform:
```hcl
data.provider_pets.data[0].id
```

Custom wrapper name:
```yaml
schema:
  type: array
  x-speakeasy-terraform-array-wrapper: pets
  items:
    $ref: "#/components/schemas/Pet"
```

## Common Patterns

### Idempotent Create/Update

When create and update use the same endpoint:

```yaml
paths:
  /resources:
    put:
      x-speakeasy-entity-operation: Resource#create,update
```

### Partial Updates (PATCH)

```yaml
paths:
  /resources/{id}:
    patch:
      x-speakeasy-entity-operation: Resource#update
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ResourcePatch"
```

### Nested Resources

For parent-child relationships:

```yaml
paths:
  /parents/{parent_id}/children:
    post:
      x-speakeasy-entity-operation: Child#create
  /parents/{parent_id}/children/{id}:
    get:
      x-speakeasy-entity-operation: Child#read
```

The `parent_id` becomes a required, ForceNew attribute.
