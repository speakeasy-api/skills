---
short_description: "Persist custom code changes across SDK regenerations"
long_description: |
  Guide for using the custom code feature to make persistent changes anywhere
  in generated SDKs. Uses 3-way merge to preserve edits through regeneration,
  with Git-based conflict resolution for overlapping changes.
source:
  - repo: "speakeasy-api/speakeasy.com"
    path: "src/content/docs/sdks/customize/code/custom-code/"
    ref: "main"
    last_reconciled: "2025-12-11"
related:
  - "./hooks.md"
  - "../sdk-languages/typescript.md"
  - "../sdk-languages/python.md"
---

# Custom Code

Custom code allows changes anywhere in generated SDKs. Speakeasy automatically preserves those changes across regenerations using a 3-way merge algorithm.

## How it works

Speakeasy preserves manual edits by performing a 3-way merge during generation:

```text
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│      Base        │     │     Current      │     │       New        │
│ Last pristine    │────▶│ Version on disk  │────▶│ Latest generation│
│ generation       │     │ (with edits)     │     │ from Speakeasy   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │     Result       │
                         │ Merged output    │
                         └──────────────────┘
```

If your edits overlap regenerated lines, Speakeasy writes Git-style conflict markers that you must resolve manually.

> **Note:** Custom code requires a Git repository. The feature uses Git under the hood to track and merge changes.

---

## Enabling custom code

### For new SDKs

Add the configuration to `gen.yaml`:

```yaml
# .speakeasy/gen.yaml
configVersion: 2.0.0
generation:
  sdkClassName: MySDK
  persistentEdits:
    enabled: true
```

### For existing SDKs

After you edit a generated file, the next `speakeasy run` may prompt to enable persistent edits and show a diff:

```text
┃ Changes detected in generated SDK files
┃ The following changes were detected in generated SDK files:
┃   M package.json (+2/-1)
┃       --- generated
┃       +++ current
┃       @@ -22,7 +22,8 @@
┃          "scripts": {
┃            "lint": "eslint --cache --max-warnings=0 src",
┃            "build": "tshy",
┃       -    "prepublishOnly": "npm run build"
┃       +    "prepublishOnly": "npm run build",
┃       +    "test:integration": "node ./scripts/integration.js"
┃          },
┃
┃ Would you like to enable custom code preservation?
┃   Yes - Enable custom code
┃ > No - Continue without preserving changes
┃   Don't ask again
```

Select **"Yes - Enable custom code"** to preserve changes.

---

## When to use custom code

### Good use cases

- Adding utility methods to models or SDK classes
- Extending initialization with custom authentication
- Modifying configuration files (package.json, pyproject.toml)
- Adding business logic specific to the domain
- Integration code for internal systems

### When to consider alternatives

| Alternative | When to use |
|-------------|-------------|
| SDK hooks | Lifecycle customization (request/response modification) |
| Custom code regions | Predefined extension areas (Enterprise only) |
| OpenAPI extensions | Generation-time customization |
| Overlays | Spec modifications without touching source |

---

## Common use cases

### Adding utility methods

Add helper methods directly to generated model classes:

```typescript
export class Payment {
  id: string;
  amount: number;
  currency: string;
  status: PaymentStatus;

  // Custom utility method
  toInvoiceItem(): InvoiceItem {
    return {
      description: `Payment ${this.id}`,
      amount: this.amount,
      currency: this.currency,
    };
  }

  needsAction(): boolean {
    return this.status === PaymentStatus.RequiresAction ||
      this.status === PaymentStatus.RequiresConfirmation;
  }
}
```

### Modifying configuration files

Add custom dependencies or scripts:

**TypeScript (package.json):**
```diff
{
  "name": "@mycompany/sdk",
  "version": "1.0.0",
  "dependencies": {
    "axios": "^1.6.0",
    "zod": "^3.22.0",
+   "aws-sdk": "^2.1.0"
  },
  "scripts": {
    "test": "jest",
+   "test:integration": "jest --config=jest.integration.js",
+   "deploy": "npm run build && aws s3 sync dist/ s3://my-bucket"
  }
}
```

**Python (pyproject.toml):**
```diff
[tool.poetry]
name = "mycompany-sdk"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.8"
httpx = ">=0.24.0"
pydantic = "^2.0"
+# Custom dependencies
+boto3 = "^1.28.0"
+redis = "^4.5.0"

[tool.poetry.scripts]
+# Custom scripts
+deploy = "mycompany_sdk.scripts:deploy"
+validate = "mycompany_sdk.scripts:validate"
```

### Extending SDK initialization

Add custom authentication providers or configuration:

```typescript
import { AWSAuth } from "./custom/aws-auth";
import { MetricsCollector } from "./custom/metrics";

export class MySDK {
  private client: HTTPClient;
  private awsAuth?: AWSAuth;
  private metrics?: MetricsCollector;

  constructor(config: SDKConfig) {
    this.client = new HTTPClient(config);

    // Custom initialization logic
    if (config.awsAuth) {
      this.awsAuth = new AWSAuth(config.awsAuth);
      this.client.interceptors.request.use(
        this.awsAuth.signRequest.bind(this.awsAuth)
      );
    }

    if (config.enableMetrics) {
      this.metrics = new MetricsCollector(config.metricsEndpoint);
      this.client.interceptors.response.use(
        this.metrics.recordResponse.bind(this.metrics)
      );
    }
  }
}
```

---

## Handling conflicts

When manual changes and Speakeasy updates modify the same lines, conflict markers appear:

```diff
{
  "name": "petstore",
<<<<<<< Current (local changes)
  "version": "0.0.2-prerelease",
=======
  "version": "0.0.3",
>>>>>>> New (Generated by Speakeasy)
  "dependencies": {
    ...
  }
}
```

### Resolution steps

1. Edit the file to keep the desired code
2. Remove the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Run `speakeasy run --skip-versioning` to finalize the merge
4. Commit the resolved changes

The `--skip-versioning` flag tells Speakeasy to reuse the existing pristine snapshot instead of creating a new one from the conflicted state.

---

## CI/CD integration

Custom code runs non-interactively in CI:

- No prompts appear
- Conflicts cause generation to fail with non-zero exit
- The Speakeasy GitHub Action automatically rolls back if conflicts occur

### Handling conflicts in CI

If conflicts occur during CI generation:

1. CI job fails with error listing conflicted files
2. Pull the changes locally
3. Run `speakeasy run` to reproduce conflicts
4. Resolve conflicts manually
5. Commit and push the resolution
6. CI succeeds on next run

### Full clone requirement

Ensure full clone in CI workflows:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full clone, not shallow
```

---

## Best practices

### Minimize changes to generated files

Keep changes minimal to reduce merge conflicts:

```typescript
// Avoid: Writing complex logic directly in generated files
export class PaymentSDK {
  async createPayment(data: PaymentRequest): Promise<Payment> {
    // 50 lines of custom validation logic mixed in...
    if (!data.amount || data.amount < 0) {
      // ...complex validation...
    }
  }
}

// Better: Import and call external logic
import { validatePayment } from "./custom/validator";

export class PaymentSDK {
  async createPayment(data: PaymentRequest): Promise<Payment> {
    validatePayment(data);  // Only 1 line added
    // Generated code continues unchanged...
  }
}
```

### Add methods instead of modifying existing ones

```typescript
// Avoid: Modifying generated methods
class User {
  getName(): string {
    return this.firstName + " " + this.lastName;  // Changed
  }
}

// Better: Add new methods
class User {
  getName(): string {
    return this.name;  // Untouched
  }

  getFullName(): string {  // Custom addition
    return this.firstName + " " + this.lastName;
  }
}
```

### Document customizations

Create a `CUSTOMIZATIONS.md` file:

```markdown
# SDK Customizations

This SDK has custom code enabled. The following customizations exist:

## Utility Methods
- `Payment.toInvoiceItem()` - Converts payments to invoice format
- `User.getFullName()` - Returns formatted full name

## Custom Dependencies
- `aws-sdk` - For S3 upload functionality
- `redis` - For caching API responses

## Modified Files
- `src/models/payment.ts` - Added utility methods
- `package.json` - Added custom dependencies and scripts
```

### Preserve generated headers

Do not remove generated headers:

```typescript
// Keep these for move detection to work
// Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT.
// @generated-id: a1b2c3d4e5f6
```

---

## Configuration options

```yaml
# .speakeasy/gen.yaml
persistentEdits:
  enabled: true   # Enable custom code
  # enabled: false  # Disable without losing changes
  # enabled: never  # Disable and prevent prompts
```

---

## File tracking

### Generated file headers

Each generated file contains a tracking header:

```typescript
// Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT.
// @generated-id: a1b2c3d4e5f6
```

The `@generated-id` is a deterministic hash based on the file's original path. Speakeasy detects file moves and renames by scanning for this unique ID:

1. File generated at `src/models/user.ts` gets ID based on that path
2. File moved to `src/entities/user.ts`
3. Next generation, Speakeasy scans for the ID at the new location
4. Updates applied to the moved file

### Comment syntax by language

| Language | Comment style |
|----------|---------------|
| Go, Java, JavaScript, TypeScript, C# | `// @generated-id: abc123` |
| Python, Ruby, Shell | `# @generated-id: abc123` |
| HTML, XML | `<!-- @generated-id: abc123 -->` |
| CSS | `/* @generated-id: abc123 */` |

### Files without comment support

Some file types (JSON, binary files) cannot have headers:

- Tracked by path only
- No move detection
- Binary files are replaced entirely on regeneration

---

## Recovery procedures

### Reset a single file

```bash
# Remove custom changes from one file
git checkout HEAD -- src/models/payment.ts

# Regenerate using the same pristine snapshot
speakeasy run --skip-versioning
```

### Reset everything

```bash
# Disable custom code in gen.yaml
# Edit .speakeasy/gen.yaml: enabled: false

# Remove all generated files (adjust pattern for SDK)
find . -name "*.gen.*" -delete

# Regenerate fresh
speakeasy run
```

### Fix duplicate ID warnings

1. Find files with duplicate IDs
2. Remove `@generated-id` line from copied files
3. Let next generation assign new IDs

---

## Custom code vs code regions

| Feature | Custom Code | Code Regions |
|---------|-------------|--------------|
| Availability | All users | Enterprise only |
| Flexibility | Anywhere in SDK | Predefined regions only |
| Merge strategy | 3-way merge | Region preservation |
| Conflict handling | Git-style markers | N/A (regions are isolated) |
| Move detection | Yes (via @generated-id) | No |
| Use case | Full customization | Constrained extension points |

Both features can be used together. Custom code regions provide safe areas for customization, while custom code allows changes anywhere.

---

## Troubleshooting

### "Failed to fetch pristine snapshot"

Remote repository unreachable or CI lacks permission:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Ensure full clone
```

### "Duplicate generated ID detected"

Multiple files have the same `@generated-id`:

- Check if files were copied instead of moved
- Remove duplicate headers from copied files

### "Cannot resolve conflicts automatically"

Manual changes and Speakeasy updates modify the same lines:

1. Open conflicted files
2. Resolve conflicts manually
3. Run `speakeasy run --skip-versioning`
4. Commit the resolution

---

## Pre-defined TODO List

When enabling custom code preservation, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Enable persistentEdits in gen.yaml | Enabling persistent edits |
| 2 | Regenerate SDK with speakeasy run | Regenerating SDK |
| 3 | Identify files needing customization | Identifying files to customize |
| 4 | Make custom changes to SDK files | Making custom changes |
| 5 | Test SDK build and functionality | Testing SDK |
| 6 | Commit changes | Committing changes |

**Usage:**
```javascript
TodoWrite([
  {content: "Enable persistentEdits in gen.yaml", status: "pending", activeForm: "Enabling persistent edits"},
  {content: "Regenerate SDK with speakeasy run", status: "pending", activeForm: "Regenerating SDK"},
  {content: "Identify files needing customization", status: "pending", activeForm: "Identifying files to customize"},
  {content: "Make custom changes to SDK files", status: "pending", activeForm: "Making custom changes"},
  {content: "Test SDK build and functionality", status: "pending", activeForm: "Testing SDK"},
  {content: "Commit changes", status: "pending", activeForm: "Committing changes"}
])
```

## Related documentation

- `./hooks.md` - SDK hooks for lifecycle customization
- `../sdk-languages/typescript.md#custom-code-regions` - TypeScript-specific code regions
- `../sdk-languages/python.md#custom-code-regions` - Python-specific code regions
