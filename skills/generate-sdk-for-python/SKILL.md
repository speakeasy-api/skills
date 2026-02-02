---
name: generate-sdk-for-python
description: >-
  Use when generating a Python SDK with Speakeasy. Covers gen.yaml configuration,
  async patterns, Pydantic models, hooks, custom code regions, and PyPI publishing.
  Triggers on "Python SDK", "generate Python", "python client", "PyPI publishing",
  "async Python SDK", "pydantic models".
license: Apache-2.0
---

# Generate SDK for Python

Configure and generate idiomatic Python SDKs with Speakeasy, featuring Pydantic models, async/sync methods, and type annotations.

## When to Use

- Generating a new Python SDK from an OpenAPI spec
- Configuring Python-specific gen.yaml options
- Setting up async patterns (method-based vs constructor-based)
- Adding SDK hooks for custom behavior
- Publishing to PyPI
- User says: "Python SDK", "generate Python client", "PyPI", "async SDK"

## Quick Start

**Always use `speakeasy quickstart`** for new SDK projects:

```bash
speakeasy quickstart --skip-interactive --output console \
  -s openapi.yaml -t python -n "MySDK" -p "my-sdk"
```

> ⚠️ **Never use `speakeasy generate sdk`** - it does not create `.speakeasy/workflow.yaml`, which is required for maintainable SDK development and `speakeasy run` regeneration.

## Essential gen.yaml Configuration

```yaml
python:
  version: 1.0.0
  packageName: "my-sdk"        # PyPI package name
  authors: ["Your Name"]

  # Async pattern: "both" (default) or "split"
  asyncMode: both              # sdk.method() and sdk.method_async()
  # asyncMode: split           # SDK() and AsyncSDK() constructors

  # Method signatures
  maxMethodParams: 4           # Parameters before request object
  flattenRequests: true

  # Type safety
  responseFormat: flat
  clientServerStatusCodesAsErrors: true
```

## Key Features

| Feature | Configuration |
|---------|--------------|
| Pydantic models | Automatic - all models use Pydantic |
| TypedDict support | Automatic - enables dict-style calls |
| Async methods | `asyncMode: both` or `split` |
| Custom hooks | `enableCustomCodeRegions: true` |
| Open enums | Via overlay (see overlays skill) |

## Async Patterns

**Method-based (default):**
```python
sdk = MySDK(api_key="...")
result = sdk.users.list()           # sync
result = await sdk.users.list_async() # async
```

**Constructor-based (`asyncMode: split`):**
```python
sdk = MySDK(api_key="...")          # sync client
async_sdk = AsyncMySDK(api_key="...") # async client
result = await async_sdk.users.list()
```

## SDK Hooks

Enable with `enableCustomCodeRegions: true`. Create hooks in `src/myapi/_hooks/`:

```python
# src/myapi/_hooks/custom_header.py
from .types import BeforeRequestContext, BeforeRequestHook
import httpx

class CustomHeaderHook(BeforeRequestHook):
    def before_request(self, ctx: BeforeRequestContext, req: httpx.Request):
        req.headers["X-Custom"] = "value"
        return req
```

Register in `_hooks/registration.py`:
```python
def init_hooks(hooks):
    hooks.register_before_request_hook(CustomHeaderHook())
```

## Common Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `packageManager` | uv | `uv` or `poetry` |
| `envVarPrefix` | "" | Prefix for env var config |
| `baseErrorName` | SDKError | Base exception class name |
| `enumFormat` | enum | `enum` or `union` |

## Publishing to PyPI

1. Configure `packageName` and `version` in gen.yaml
2. Build: `uv build` or `poetry build`
3. Publish: `uv publish` or `poetry publish`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ResponseValidationError` | API response doesn't match spec - use contract testing |
| Builtin name conflicts | Add to `allowedRedefinedBuiltins: [id, type, object]` |
| Async pagination blocking | Enable `fixFlags.asyncPaginationSep2025: true` |

## Related Skills

- `start-new-sdk-project` - Initial SDK setup
- `customize-sdk-hooks` - Detailed hook implementation
- `setup-sdk-testing` - Testing patterns
- `manage-openapi-overlays` - Spec customization
