# Python SDK Configuration

Detailed gen.yaml configuration options for Python SDKs.

## gen.yaml Configuration

```yaml
python:
  version: 1.0.0
  packageName: "my-sdk"

  # Async patterns
  asyncMode: both                   # both, split, or sync-only

  # Package management
  packageManager: uv                # uv or poetry

  # Environment variables
  envVarPrefix: "MY_SDK_"           # Prefix for env config

  # Method signatures
  maxMethodParams: 4
  flatteningOrder: parameters-first
```

## Package Structure

```
src/
└── my_sdk/
    ├── __init__.py        # Package exports
    ├── _client.py         # SDK client class
    ├── _hooks/            # Custom hooks (preserved)
    │   └── registration.py
    ├── models/
    │   ├── operations/    # Request/response models
    │   ├── shared/        # Shared Pydantic models
    │   └── errors.py      # Error classes
    └── _utils/            # Internal utilities
```

## Async Mode Options

### `asyncMode: both` (Default)

Same client, sync and async methods:

```python
from my_sdk import MySDK

sdk = MySDK(api_key="...")

# Sync
user = sdk.users.get("123")

# Async
user = await sdk.users.get_async("123")
```

### `asyncMode: split`

Separate client classes:

```python
from my_sdk import MySDK, AsyncMySDK

# Sync client
sdk = MySDK(api_key="...")
user = sdk.users.get("123")

# Async client
async_sdk = AsyncMySDK(api_key="...")
user = await async_sdk.users.get("123")
```

### `asyncMode: sync-only`

No async support (smaller package):

```python
from my_sdk import MySDK

sdk = MySDK(api_key="...")
user = sdk.users.get("123")  # Only sync available
```

## Pydantic Models

All models use Pydantic for validation:

```python
from my_sdk.models import User, CreateUserRequest

# Type-safe requests
request = CreateUserRequest(
    name="Alice",
    email="alice@example.com"
)

# Response validation
user: User = sdk.users.create(request)
print(user.id, user.created_at)  # Typed attributes
```

### Model Serialization

```python
# To dict
user_dict = user.model_dump()

# To JSON
user_json = user.model_dump_json()

# From dict
user = User.model_validate({"id": "123", "name": "Alice"})
```

## Package Manager Options

### uv (Recommended)

```yaml
python:
  packageManager: uv
```

```bash
# Install
uv pip install my-sdk

# Publish
uv publish
```

### poetry

```yaml
python:
  packageManager: poetry
```

```bash
# Install
poetry add my-sdk

# Publish
poetry publish
```

## Environment Variable Configuration

With `envVarPrefix: "MY_SDK_"`:

```python
# Reads MY_SDK_API_KEY from environment
sdk = MySDK()

# Or explicit
sdk = MySDK(api_key="...")
```

Supported env vars:
- `{PREFIX}API_KEY` - API key authentication
- `{PREFIX}SERVER_URL` - Custom server URL
- `{PREFIX}TIMEOUT` - Request timeout (seconds)

## Runtime Configuration

```python
from my_sdk import MySDK
from my_sdk.utils import BackoffStrategy, RetryConfig

sdk = MySDK(
    # Authentication
    api_key="...",

    # Server selection
    server="production",           # Named server from spec
    server_url="https://api.example.com",  # Custom URL

    # Timeouts
    timeout_ms=30000,

    # Retries
    retry_config=RetryConfig(
        strategy="backoff",
        backoff=BackoffStrategy(
            initial_interval=500,
            max_interval=60000,
            exponent=1.5,
            max_elapsed_time=300000,
        ),
        retry_connection_errors=True,
    ),
)

# Per-call overrides
user = sdk.users.create(
    data,
    timeout_ms=60000,
    retries=RetryConfig(strategy="none"),
)
```

## Error Handling

```python
from my_sdk.models.errors import SDKError, APIError

try:
    user = sdk.users.get("invalid-id")
except APIError as e:
    # Server returned error status
    print(f"Status: {e.status_code}")
    print(f"Body: {e.body}")
    print(f"Headers: {e.headers}")
except SDKError as e:
    # Network, timeout, or other SDK error
    print(f"SDK error: {e.message}")
```

## Pagination

For paginated endpoints with `x-speakeasy-pagination`:

```python
# Auto-iterate all pages
for user in sdk.users.list(limit=50):
    print(user.name)

# Async iteration
async for user in sdk.users.list_async(limit=50):
    print(user.name)

# Manual pagination
page = sdk.users.list(limit=50)
while page:
    for user in page.data:
        print(user.name)
    page = page.next()
```

## Streaming Responses

For SSE endpoints:

```python
# Sync streaming
for event in sdk.chat.complete(message="Hello"):
    print(event.content)

# Async streaming
async for event in sdk.chat.complete_async(message="Hello"):
    print(event.content)
```

## Custom Hooks

Create hooks in `src/my_sdk/_hooks/registration.py`:

```python
from .types import Hooks

def init_hooks(hooks: Hooks) -> None:
    @hooks.before_request
    def add_headers(request):
        request.headers["X-Custom-Header"] = "value"
        return request

    @hooks.after_response
    def log_response(response, request):
        print(f"{request.method} {request.url}: {response.status_code}")
        return response

    @hooks.on_error
    def handle_error(error, request):
        print(f"Error: {error}")
        raise error
```

## Extending the SDK

Add custom utilities in a sidecar package:

```python
# my_sdk_utils/helpers.py
from my_sdk import MySDK

def create_configured_client() -> MySDK:
    return MySDK(
        api_key=os.environ["API_KEY"],
        server="production",
        timeout_ms=30000,
    )

def batch_create_users(sdk: MySDK, users: list[dict]) -> list:
    return [sdk.users.create(u) for u in users]
```

## Debugging

```python
import logging

# Enable SDK debug logging
logging.getLogger("my_sdk").setLevel(logging.DEBUG)

# Or per-request
sdk = MySDK(debug=True)
```

## Type Hints

Full type hint support for IDEs:

```python
from my_sdk import MySDK
from my_sdk.models import User

sdk = MySDK(api_key="...")

# IDE knows return type
user: User = sdk.users.get("123")
user.name  # Autocomplete works
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Async pagination blocking | Enable `fixFlags.asyncPaginationSep2025: true` |
| Pydantic validation errors | Check server responses match OpenAPI spec |
| Import errors | Ensure correct Python version (3.9+) |
| SSL certificate errors | Set `verify_ssl=False` (dev only) |
| Timeout errors | Increase `timeout_ms` or per-call override |

## Publishing to PyPI

```bash
# Build
uv build
# or: poetry build

# Publish
uv publish
# or: poetry publish
```

Ensure `pyproject.toml` has:
- `name` - Package name
- `version` - Current version
- `description` - Package description
- `readme` - Path to README
