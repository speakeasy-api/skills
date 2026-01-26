---
short_description: "Python SDK generation guide"
long_description: |
  Comprehensive guide for generating Python SDKs with Speakeasy.
  Includes methodology, feature support, OSS comparison, and language-specific configuration.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/docs/sdks/languages/python/"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Python SDK Generation

> **Note:** For a comparison between the Speakeasy Python SDK and some popular open-source generators, see the OSS Comparison section below.

## SDK Overview

Speakeasy-generated Python SDKs are designed to be best in class, providing a seamless developer experience and full type safety, alongside asynchronous support.

The core Python SDK features include:

- Fully type-annotated classes and methods with full Pydantic models and associated TypedDicts.
- Async and Sync methods for all endpoints.
- Support for streaming uploads and downloads.
- Support for Server-Sent Events (SSE) with automatic method overloads for enhanced type safety.
- Authentication support for OAuth flows and support for standard security mechanisms (HTTP Basic, application tokens, etc.).
- Optional pagination support for supported APIs.
- Optional support for retries in every operation.
- Complex number types including big integers and decimals.
- Date and date/time types using RFC3339 date formats.
- Custom type enums using strings and integers (including Open Enums).
- Union types and combined types.

### Python Package Structure

```
src/
  {Package Name}/
    {SDK Class Name}.py
    ...
    models/
      shared/
        ...
      operations/
        ...
      ...
    utils/
      ...
docs/
  ...
setup.py
...
```

By default, `uv` handles Python dependencies and packaging, but users can configure `poetry` instead via the `packageManager` option.

## Python Type Safety

Modern Python uses type hints to improve code readability and so do Speakeasy-generated Python SDKs! Speakeasy-generated Python SDKs expose type annotations for developers to perform type checks at runtime and increase type safety, we also employ Pydantic models to ensure that the data passed to and from the SDK is valid at runtime.

### The generated models

Speakeasy uses `pydantic` for all generated models to correctly serialize and deserialize objects; whether the objects are passed as query parameters, path parameters, or request bodies. Metadata based on the definitions provided by the OpenAPI document are appended to fields.

For example, this is the generated class for the Drink component:

```python
class Drink(BaseModel):
    name: str
    r"""The name of the drink."""
    price: float
    r"""The price of one unit of the drink in US cents."""
    type: Optional[DrinkType] = None
    r"""The type of drink."""
    stock: Optional[int] = None
    r"""The number of units of the drink in stock, only available when authenticated."""
    product_code: Annotated[Optional[str], pydantic.Field(alias="productCode")] = None
    r"""The product code of the drink, only available when authenticated."""
```

Python also generates matching `TypedDict` classes for each model, which can be used to pass in dictionaries to the SDK methods without the need to import the model classes.

```python
class DrinkTypedDict(TypedDict):
    name: str
    r"""The name of the drink."""
    price: float
    r"""The price of one unit of the drink in US cents."""
    type: NotRequired[DrinkType]
    r"""The type of drink."""
    stock: NotRequired[int]
    r"""The number of units of the drink in stock, only available when authenticated."""
    product_code: NotRequired[str]
    r"""The product code of the drink, only available when authenticated."""
```

which allows methods to be called one of two ways:

```python
res = s.orders.create_order(drinks=[
    {
        "type": bar.OrderType.INGREDIENT,
        "product_code": "AC-A2DF3",
        "quantity": 138554,
    },
])
```

or

```python
res = s.orders.create_order(drinks=[
    Drink(
        type=bar.OrderType.INGREDIENT,
        product_code="AC-A2DF3",
        quantity=138554,
    ),
])
```

## Server-Sent Events (SSE) with type safety

Python SDKs automatically generate method overloads for Server-Sent Events operations when the `inferSSEOverload` configuration is enabled (default: `true`). This feature provides enhanced type safety by creating separate method signatures for streaming and non-streaming responses.

When an operation meets the following criteria, Speakeasy will generate overloaded methods:
- The operation has a required request body
- The request body contains a `stream` field (boolean type)
- The operation has exactly two responses: one `text/event-stream` and one `application/json`

```python
# Non-streaming method - returns JSON response object
response = s.chat.create(prompt="Hello world", stream=False)
print(response.content)  # Fully typed ChatResponse

# Streaming method - returns SSE event iterator
stream = s.chat.create(prompt="Hello world", stream=True)
for event in stream:
    print(event.data)  # Fully typed ChatEvent
```

This eliminates the need for runtime type checking and provides better IDE support with accurate type hints for both streaming and non-streaming use cases.

## Async vs Sync Methods

Speakeasy-generated Python SDKs provide both synchronous and asynchronous methods for all endpoints. The SDK uses the `httpx` library for making HTTP requests, which supports both synchronous and asynchronous requests.

Synchronous:

```python
res = s.orders.create_order(drinks=[
    Drink(
        type=bar.OrderType.INGREDIENT,
        product_code="AC-A2DF3",
        quantity=138554,
    ),
])
```

Asynchronous:

```python
res = await s.orders.create_order_async(drinks=[
    Drink(
        type=bar.OrderType.INGREDIENT,
        product_code="AC-A2DF3",
        quantity=138554,
    ),
])
```

> **Note:** Python SDKs can also be configured to use a constructor-based async pattern with separate `AsyncMyAPI` classes. See the asyncMode configuration option below for details.

## HTTP Client

To make API calls, the Python SDK instantiates its own HTTP client using the `Client` class from the `httpx` library. This allows authentication settings to persist across requests and reduce overhead.

## Parameters

If configured, Speakeasy will generate methods with parameters for each parameter defined in the OpenAPI document, as long as the number of parameters is less than or equal to the configured `maxMethodParams` value in the `gen.yaml` file.

If the number of parameters exceeds the configured `maxMethodParams` value or is set to `0`, a request object will be generated for the method to pass in all parameters as a single object.

## Errors

The Python SDK will raise exceptions for any network or invalid request errors.

For unsuccessful responses, if a custom error response is specified in the spec file, the SDK will unmarshal the HTTP response details into the custom error response to be thrown as an exception. When no custom response is specified in the spec, the SDK will throw an `SDKException` with details of the failed response.

```python
import sdk
from sdk.models import errors

s = sdk.SDK()
res = None
try:
    res = s.errors.status_get_x_speakeasy_errors(status_code=385913)
except errors.StatusGetXSpeakeasyErrorsResponseBody as e:
    # handle exception
except errors.SDKError as e:
    # handle exception

if res is not None:
    # handle response
    pass
```

### ResponseValidationError

A `ResponseValidationError` is a special error that occurs when the server returns a **successful response** (2xx status) but the response body doesn't match the SDK's expected types. This typically indicates a mismatch between the OpenAPI spec and the actual API implementation.

```python
from sdk.models import errors

try:
    res = sdk.resources.get(id="123")
except errors.ResponseValidationError as e:
    # Server returned 200 OK, but response doesn't match expected schema
    # This is a spec/API mismatch, not an API error
    print(f"Type mismatch: {e}")
    print(f"Raw response: {e.raw_response}")
except errors.SDKError as e:
    # Server returned an error status code
    print(f"API error: {e}")
```

**Common causes of ResponseValidationError:**
- API returns a field not defined in the spec
- API returns a different type than expected (e.g., string instead of integer)
- API returns `null` for a field not marked `nullable`
- API returns an enum value not listed in the spec

**If you encounter ResponseValidationError:**
1. Use contract testing to systematically identify all type mismatches: `../sdk-testing/contract-testing.md`
2. Update the OpenAPI spec or create an overlay to fix the types
3. Regenerate the SDK with `speakeasy run`

> **See also:** `../spec-first/validation.md#dynamic-validation-contract-testing` for the validation workflow.

## User Agent Strings

The Python SDK includes a user agent string in all requests. This can be leveraged to track SDK usage amongst broader API usage. The format is as follows:

```
speakeasy-sdk/python {{SDKVersion}} {{GenVersion}} {{DocVersion}} {{PackageName}}
```

Where

- `SDKVersion` is the version of the SDK, defined in `gen.yaml` and released
- `GenVersion` is the version of the Speakeasy generator
- `DocVersion` is the version of the OpenAPI document
- `PackageName` is the name of the package defined in `gen.yaml`

## Known Limitations

The following features have limited or no support in Python SDKs:

| Feature | Status | Notes |
|---------|--------|-------|
| XML requests/responses | ❌ | Not supported |
| `label` & `matrix` path parameter styles | ❌ | Not supported |
| Intersection Types | 🏗️ Partial | |
| `x-www-form-urlencoded` | 🏗️ Partial | Encoding supported, but not non-object types |
| mTLS | 🏗️ Partial | |

All other standard OpenAPI features are fully supported including: OAuth flows, pagination, retries, streaming, SSE, all standard data types, union types, and custom error responses.

## Configuration Options

All Python SDK configuration is managed in the `gen.yaml` file under the `python` section.

### Version and General Configuration

```yaml
python:
  version: 1.2.3
  authors: ["Author Name"]
  packageName: "openapi"
  moduleName: "openapi"
  packageManager: "uv" # or "poetry" to switch to poetry
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| version | true | 0.0.1 | The current version of the SDK. |
| packageName | true | openapi | The distribution name of the PyPI package. See Python Package Metadata. |
| moduleName | false | Same as `packageName` | The name of the module users will import from. Allows using a different name for imports than the package name. PEP 420 implicit namespace packages are supported with period (.) characters, such as `speakeasy.api_client`. Custom code regions will be removed by updating the ModuleName |
| authors | true | ["Speakeasy"] | Authors of the published package. |
| packageManager | false | uv | The package manager to use for dependency management and packaging. Valid options: 'uv' or 'poetry'. Defaults to 'uv' for better performance. |

### Description and URLs

```yaml
python:
  description: "Python Client SDK Generated by Speakeasy."
  homepage: "https://example.com"
  documentationUrl: "https://example.com/docs"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| description | false | "Python Client SDK Generated by Speakeasy." | A short description of the project. |
| homepage | false | null | The URL for the homepage of the project. |
| documentationUrl | false | null | The URL for the project documentation. |

### Different Package and Module Names

You can configure a different name for the PyPI package and the module users will import from:

```yaml
python:
  packageName: "my-package" # Users will install with: pip install my-package
  moduleName: "my_module" # Users will import with: from my_module import SDK
```

This can be useful when you want the package name to follow PyPI conventions (using hyphens) but the module name to follow Python conventions (using underscores).

### Additional Dependencies

```yaml
python:
  additionalDependencies:
    main:
      requests: "^2.25.1"
    dev:
      pytest: "^6.2.1"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| additionalDependencies | false | {} | Add additional dependencies to include in the generated `pyproject.toml` file. |

### Method and Parameter Management

```yaml
python:
  maxMethodParams: 4
  flatteningOrder: "parameters-first"
  methodArguments: "infer-optional-args"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| flattenRequests | false | true | Turn request parameters and body fields into a flat list of method arguments. This takes precedence over maxMethodParams. If there is no request body then maxMethodParams will be respected. |
| maxMethodParams | false | 9999 | Maximum number of parameters before an input object is generated. `0` means input objects are always used. |
| flatteningOrder | false | parameters-first | Determines the ordering of method arguments when flattening parameters and body fields. `parameters-first` or `body-first` |
| methodArguments | false | require-security-and-request | Determines how arguments for SDK methods are generated. |

### Security Configuration

```yaml
python:
  envVarPrefix: "SPEAKEASY"
  flattenGlobalSecurity: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| flattenGlobalSecurity | false | true | Enables inline security credentials during SDK instantiation. |
| envVarPrefix | false | "" | Sets a prefix for environment variables that allows users to configure global parameters and security. |

### Import Management

```yaml
python:
  imports:
    option: "openapi"
    paths:
      callbacks: "models/callbacks"
      errors: "models/errors"
      operations: "models/operations"
      shared: "models/shared"
      webhooks: "models/webhooks"
```

| Field | Required | Default Value | Description |
|-------|----------|---------------|-------------|
| option | false | "openapi" | Defines the type of import strategy. Typically set to `"openapi"`, indicating that the structure is based on the OpenAPI document. |
| paths | false | {} | Customizes where different parts of the SDK (e.g., callbacks, errors, and operations) will be imported from. |

#### Import Paths

| Component | Default Value | Description |
|-----------|---------------|-------------|
| callbacks | models/callbacks | The directory where callback models will be imported from. |
| errors | models/errors | The directory where error models will be imported from. |
| operations | models/operations | The directory where operation models (i.e., API endpoints) will be imported from. |
| shared | models/components | The directory for shared components, such as reusable schemas, and data models imported from the OpenAPI spec. |
| webhooks | models/webhooks | The directory for webhook models, if the SDK includes support for webhooks. |

### Error and Response Handling

```yaml
python:
  clientServerStatusCodesAsErrors: true
  responseFormat: "flat"
  enumFormat: "enum"
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| clientServerStatusCodesAsErrors | false | true | Whether to treat 4XX and 5XX status codes as errors. |
| responseFormat | false | flat | Defines how responses are structured. Options: `envelope`, `envelope-http`, or `flat`. |
| enumFormat | false | enum | Determines how enums are generated. Options: `enum` (Python enums) or `union` (union types). |

### Async Method Configuration

```yaml
python:
  asyncMode: split  # or "both" (default)
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| asyncMode | false | both | Controls how asynchronous methods are generated. `both` (default) uses method-based approach with `_async` suffixes. `split` uses constructor-based approach with separate `AsyncMyAPI` classes. |

The `asyncMode` setting provides two patterns for handling async operations:

**Method-based (`both`, default)**: Every operation has two methods - a synchronous version and an asynchronous version with an `_async` suffix.

```python
sdk = MyAPI(api_key="...")

# Synchronous operations
result = sdk.list_users()

# Asynchronous operations
result = await sdk.list_users_async()
```

**Constructor-based (`split`)**: Separate constructors for synchronous and asynchronous clients. All method names are identical between sync and async versions.

```python
# Synchronous client
sync_sdk = MyAPI(api_key="...")
result = sync_sdk.list_users()

# Asynchronous client
async_sdk = AsyncMyAPI(api_key="...")
result = await async_sdk.list_users()
```

The constructor-based pattern eliminates method name duplication and provides clearer IDE suggestions.

> **Note:** When using `asyncMode: split`, async operations use the `AsyncMyAPI` constructor instead of `_async` method suffixes.

### Server-sent Events Configuration

```yaml
python:
  sseFlatResponse: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| sseFlatResponse | false | true | When enabled, hoists the `data` field content to the top level for server-sent events, eliminating the need to destructure data from yielded items. Consumers can directly access the data without additional parsing. |

### Pytest Configuration

```yaml
python:
  pytestFilterWarnings:
    - error
    - "ignore::DeprecationWarning"
  pytestTimeout: 300
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| pytestFilterWarnings | false | [] | Global pytest filterwarnings configuration value, which are filters to control Python warnings. Use to ignore warnings or raise warnings as errors. Additional reference: https://docs.python.org/3/library/warnings.html#warning-filter |
| pytestTimeout | false | 0 | When value is greater than 0, installs pytest-timeout and sets the global pytest-timeout configuration value, which is the number of seconds before individual tests are timed out. |

### Fix Flags

```yaml
python:
  fixFlags:
    asyncPaginationSep2025: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| asyncPaginationSep2025 | false | true | Disabling not recommended. Fixes async pagination methods to return async next() functions instead of synchronous ones, preventing blocking fetches after the initial API call. |

### Python Builtin Name Handling

When OpenAPI specs use field names that conflict with Python builtins (like `id`, `type`, `object`), use the `allowedRedefinedBuiltins` option to prevent generation failures:

```yaml
python:
  allowedRedefinedBuiltins:
    - id
    - object
    - type
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| allowedRedefinedBuiltins | false | [] | List of Python builtin names that can be redefined in generated code. Use when OpenAPI fields clash with Python reserved words like `id`, `type`, `object`, `list`, `dict`, etc. |

**Common field names requiring this option:**
- `id` - Very common in REST APIs for resource identifiers
- `type` - Often used for discriminator fields or resource types
- `object` - Used in some APIs for generic object references
- `list` - Sometimes used as a field name for collections

> **Pattern Source:** Extracted from [dub-python](https://github.com/dubinc/dub-python) SDK

### Custom Error Hierarchy

Configure branded error classes with `baseErrorName` to create a custom exception hierarchy for your SDK:

```yaml
python:
  baseErrorName: MyAPIError      # Base class for all SDK errors
  defaultErrorName: SDKError     # Generic error when no specific match
```

This generates a hierarchy where all HTTP errors inherit from your base class:

```
MyAPIError (base class)
├── BadRequest (400)
├── Unauthorized (401)
├── Forbidden (403)
├── NotFound (404)
├── Conflict (409)
├── UnprocessableEntity (422)
├── RateLimitExceeded (429)
└── InternalServerError (500)
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| baseErrorName | false | SDKError | Name for the base error class that all HTTP errors inherit from. Use this to create branded exceptions (e.g., `DubError`, `StripeError`). |
| defaultErrorName | false | SDKError | Name for the generic error thrown when no specific error class matches the response. |

**Usage in client code:**

```python
from myapi.models import errors

try:
    res = client.resources.create(...)
except errors.RateLimitExceeded as e:
    print(f"Rate limited: retry after {e.headers.get('Retry-After')}s")
except errors.NotFound as e:
    print(f"Resource not found: {e.message}")
except errors.MyAPIError as e:
    # Catch-all for any API error
    print(f"API error {e.status_code}: {e.message}")
```

Each error class provides:
- `message` - Human-readable error message
- `status_code` - HTTP status code (e.g., 404)
- `headers` - Response headers (useful for rate limit info)
- `body` - Raw response body
- `raw_response` - Full httpx.Response object

> **Pattern Source:** Extracted from [dub-python](https://github.com/dubinc/dub-python) SDK

### Test Generation Configuration

Control test generation behavior with these generation-level flags in `gen.yaml`:

```yaml
generation:
  tests:
    generateTests: true        # Enable test generation
    generateNewTests: false    # Don't add new tests, only update existing
    skipResponseBodyAssertions: false
```

| Combination | Behavior |
|-------------|----------|
| `generateTests: true`, `generateNewTests: true` | Generate all tests, add new tests for new operations |
| `generateTests: true`, `generateNewTests: false` | Update existing tests only, preserve manual/custom tests |
| `generateTests: false` | No test generation |

**Recommended for production SDKs:** `generateTests: true`, `generateNewTests: false`

This combination:
- Enables the test framework setup and fixtures
- Updates existing test files when regenerating
- Preserves any manually-added test cases
- Prevents test churn and unexpected CI changes on each regeneration

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| generateTests | false | false | Enable generation of test files for SDK operations. |
| generateNewTests | false | true | When true, generates new test files for operations that don't have tests. When false, only updates existing test files. |
| skipResponseBodyAssertions | false | false | When true, skips assertions on response body content in generated tests. |

> **Pattern Source:** Extracted from [dub-python](https://github.com/dubinc/dub-python) SDK

### SDK Hooks (Extension Points)

Hooks provide lifecycle callbacks around SDK HTTP calls, enabling custom behavior without modifying generated code. They are the primary extension mechanism for production SDKs.

**Hook Types:**

| Hook Type | Trigger | Use Cases |
|-----------|---------|-----------|
| `BeforeRequestHook` | Before HTTP request sent | Custom headers, authentication, request modification, tracing |
| `AfterSuccessHook` | After successful response | Logging, metrics, response transformation, deprecation warnings |
| `AfterErrorHook` | After error response | Error logging, retry logic, alerting, error transformation |

**Enabling Hooks:**

Hooks require `enableCustomCodeRegions: true` (see next section) to preserve hook files across regenerations:

```yaml
python:
  enableCustomCodeRegions: true
```

**Hook Registration:**

Hooks are registered in `_hooks/registration.py`:

```python
# src/myapi/_hooks/registration.py
from .custom_user_agent import CustomUserAgentHook
from .deprecation_warning import DeprecationWarningHook
from .tracing import TracingHook
from .types import Hooks

def init_hooks(hooks: Hooks):
    """Register custom hooks for the SDK."""
    tracing_hook = TracingHook()

    # Before request hooks
    hooks.register_before_request_hook(CustomUserAgentHook())
    hooks.register_before_request_hook(tracing_hook)

    # After success hooks
    hooks.register_after_success_hook(DeprecationWarningHook())
    hooks.register_after_success_hook(tracing_hook)

    # After error hooks
    hooks.register_after_error_hook(tracing_hook)
```

**Example: Custom User-Agent Hook:**

```python
# src/myapi/_hooks/custom_user_agent.py
from typing import Union
import httpx
from .types import BeforeRequestContext, BeforeRequestHook

class CustomUserAgentHook(BeforeRequestHook):
    def before_request(
        self, hook_ctx: BeforeRequestContext, request: httpx.Request
    ) -> Union[httpx.Request, Exception]:
        request.headers["user-agent"] = "myapi-python/" + request.headers["user-agent"].split(" ")[1]
        return request
```

**Other Hook Signatures:**

```python
# AfterSuccessHook - inspect/modify responses
class MyAfterSuccessHook(AfterSuccessHook):
    def after_success(self, hook_ctx: AfterSuccessContext, response: httpx.Response) -> Union[httpx.Response, Exception]:
        return response

# AfterErrorHook - handle errors, can return modified response/error tuple
class MyAfterErrorHook(AfterErrorHook):
    def after_error(self, hook_ctx: AfterErrorContext, response: Optional[httpx.Response], error: Optional[Exception]) -> Union[Tuple[Optional[httpx.Response], Optional[Exception]], Exception]:
        return response, error
```

> **Pattern Source:** Extracted from [mistralai/client-python](https://github.com/mistralai/client-python)

### Custom Code Regions

Enable custom code preservation across regenerations with `enableCustomCodeRegions`. This is critical for production SDKs that need hooks, custom utilities, or integrations.

```yaml
python:
  enableCustomCodeRegions: true
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| enableCustomCodeRegions | false | false | Preserve custom code in `_hooks/` and `extra/` directories across regenerations. Required for SDK hooks and custom utilities. |

**Recommended Directory Structure:**

```
src/myapi/
├── _hooks/                 # Hook implementations (PRESERVED)
│   ├── __init__.py
│   ├── registration.py     # Hook initialization
│   ├── types.py            # Hook type definitions
│   ├── sdkhooks.py         # Base hook classes
│   ├── custom_user_agent.py
│   ├── deprecation_warning.py
│   └── tracing.py
├── extra/                  # Custom utilities (PRESERVED)
│   ├── __init__.py         # Public exports
│   ├── observability/      # Tracing, metrics
│   │   └── otel.py
│   ├── helpers/            # Custom helper functions
│   ├── struct_chat.py      # Custom response parsing
│   └── tests/              # Tests for custom code
│       └── test_helpers.py
├── models/                 # Generated models (regenerated)
├── sdk.py                  # Generated SDK class (regenerated)
└── ...                     # Other generated files
```

**Regeneration Behavior:**

| Directory | Behavior |
|-----------|----------|
| `_hooks/` | **Preserved** - Never overwritten by regeneration |
| `extra/` | **Preserved** - Never overwritten by regeneration |
| `models/`, `sdk.py`, etc. | **Regenerated** - Overwritten on each `speakeasy run` |

**Best Practices:**

1. **Put hooks in `_hooks/`** - All hook implementations and registration
2. **Put utilities in `extra/`** - Custom parsers, helpers, integrations, observability
3. **Add tests for custom code** - Place in `extra/tests/` with separate CI workflow
4. **Export from `extra/__init__.py`** - Clean public API for custom features
5. **Document custom code** - Add README.md in `extra/` explaining extensions

**CI/CD for Custom Code:**

Add separate workflows for testing and linting custom code:

```yaml
# .github/workflows/test_custom_code.yaml
name: Test Custom Code
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: poetry install --no-interaction
      - name: Run custom code tests
        run: python -m unittest discover -s src/myapi/extra/tests -t src
```

> **Pattern Source:** Extracted from [mistralai/client-python](https://github.com/mistralai/client-python)

### Additional Configuration Options

The following options provide additional control over SDK generation:

```yaml
python:
  enumFormat: union              # Use Union[Literal[...]] instead of Enums
  inputModelSuffix: input        # Suffix for request models
  outputModelSuffix: output      # Suffix for response models
  flattenRequests: true          # Flatten request parameters
```

| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
| enumFormat | false | enum | How enums are generated: `enum` (Python Enum classes) or `union` (Union[Literal[...]] types). |
| inputModelSuffix | false | "" | Suffix appended to request/input model names (e.g., `CreateUserInput`). Prevents naming collisions with response models. |
| outputModelSuffix | false | "" | Suffix appended to response/output model names (e.g., `UserOutput`). |
| flattenRequests | false | true | Flatten request body fields into method parameters. Works with `maxMethodParams` to control signature style. |

**Enum Format Trade-offs:**

| Option | Generated Code | Pros | Cons |
|--------|---------------|------|------|
| `enum` | `class Status(str, Enum): ACTIVE = "active"` | IDE autocomplete, type safety, discoverability | Requires imports, more verbose |
| `union` | `Status = Union[Literal["active"], Literal["inactive"]]` | Simpler, JSON-friendly, no imports needed | Less discoverable in IDE |

**Recommendation:** Use `union` for APIs with many enums or when JSON serialization simplicity is important. Use `enum` when IDE discoverability and type safety are priorities.

**Request Flattening:**

The `flattenRequests` option combined with `maxMethodParams` controls method signatures:

| Configuration | Result |
|---------------|--------|
| `flattenRequests: true`, `maxMethodParams: 15` | Individual parameters up to 15, then request object |
| `flattenRequests: true`, `maxMethodParams: 0` | Always use request object |
| `flattenRequests: false` | Always use request object |

> **Pattern Source:** Extracted from [mistralai/client-python](https://github.com/mistralai/client-python)

---

## Sidecar Utilities Pattern

Add custom utility files alongside generated code. Files in `utils/` with non-generated names are preserved across regeneration:

```
src/myapi/utils/
├── retries.py          # Generated
├── security.py         # Generated
├── oauth_helper.py     # CUSTOM - preserved
└── custom_parser.py    # CUSTOM - preserved
```

| Approach | Use When |
|----------|----------|
| **Sidecar utilities** | New utility functions, OAuth helpers, parsers |
| **Custom code regions** (`_hooks/`, `extra/`) | Modifying SDK behavior, hooks |
| **Overlays** | Modifying OpenAPI spec before generation |

> **Pattern Source:** Extracted from [OpenRouterTeam/python-sdk](https://github.com/OpenRouterTeam/python-sdk)

---

## DevContainers Support

Enable VS Code DevContainers for consistent contributor environments:

```yaml
generation:
  devContainers:
    enabled: true
    schemaPath: .speakeasy/out.openapi.yaml
```

Generates `.devcontainer/` with Python, uv, linting, and testing pre-configured.

---

## Pre-defined TODO List

When configuring a Python SDK generation, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Review Python SDK feature requirements | Reviewing Python SDK feature requirements |
| 2 | Configure gen.yaml for Python target | Configuring gen.yaml for Python target |
| 3 | Set package name and version | Setting package name and version |
| 4 | Configure async mode (method-based or constructor-based) | Configuring async mode |
| 5 | Set maxMethodParams and flattening options | Setting maxMethodParams and flattening options |
| 6 | Configure authentication and security | Configuring authentication and security |
| 7 | Test SDK compilation and type checking | Testing SDK compilation and type checking |
| 8 | Verify async and sync methods work correctly | Verifying async and sync methods |

**Usage:**
```
TodoWrite([
  {content: "Review Python SDK feature requirements", status: "pending", activeForm: "Reviewing Python SDK feature requirements"},
  {content: "Configure gen.yaml for Python target", status: "pending", activeForm: "Configuring gen.yaml for Python target"},
  {content: "Set package name and version", status: "pending", activeForm: "Setting package name and version"},
  {content: "Configure async mode (method-based or constructor-based)", status: "pending", activeForm: "Configuring async mode"},
  {content: "Set maxMethodParams and flattening options", status: "pending", activeForm: "Setting maxMethodParams and flattening options"},
  {content: "Configure authentication and security", status: "pending", activeForm: "Configuring authentication and security"},
  {content: "Test SDK compilation and type checking", status: "pending", activeForm: "Testing SDK compilation and type checking"},
  {content: "Verify async and sync methods work correctly", status: "pending", activeForm: "Verifying async and sync methods"}
])
```

**Nested workflows:**
- See `plans/sdk-generation.md` for the full SDK generation workflow
- See `spec-first/validation.md` for OpenAPI validation before generation
