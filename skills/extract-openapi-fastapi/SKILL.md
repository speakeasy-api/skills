---
name: extract-openapi-fastapi
description: >-
  Use when extracting OpenAPI from a FastAPI application. Covers script-based
  extraction, operation ID customization, Speakeasy extensions, and common
  lint fixes. Triggers on "FastAPI OpenAPI", "extract from FastAPI",
  "FastAPI SDK", "FastAPI spec".
license: Apache-2.0
---

# extract-openapi-fastapi

Extract an OpenAPI specification from a FastAPI application without running the server.

## When to Use

- User has a FastAPI app and needs an OpenAPI spec
- User wants to generate an SDK from FastAPI code
- User says: "FastAPI OpenAPI", "extract from FastAPI", "FastAPI SDK"

## Extraction Method

FastAPI generates OpenAPI at runtime. Extract without starting the server:

```python
# extract_openapi.py
import json
import sys
sys.path.insert(0, ".")
from main import app  # adjust import path

with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)
```

```bash
python extract_openapi.py
```

For factory pattern apps:

```python
from main import create_app
app = create_app()
print(json.dumps(app.openapi()))
```

## Customizing Operation IDs

FastAPI default IDs are verbose (`read_burger_burger__burger_id__get`). Fix with:

```python
from fastapi import FastAPI, APIRoute

def custom_id(route: APIRoute) -> str:
    words = route.name.split("_")
    return words[0] + "".join(w.title() for w in words[1:])

app = FastAPI(generate_unique_id_function=custom_id)
```

Or per-operation:

```python
@app.get("/burger/{id}", operation_id="getBurger")
def get_burger(id: int): ...
```

## Adding Speakeasy Extensions

```python
@app.get(
    "/items",
    openapi_extra={
        "x-speakeasy-retries": {
            "strategy": "backoff",
            "backoff": {"initialInterval": 500, "maxInterval": 60000, "exponent": 1.5},
            "statusCodes": ["5XX", "429"]
        },
        "x-speakeasy-group": "items",
        "x-speakeasy-name-override": "list"
    }
)
def list_items(): ...
```

For global extensions, customize `app.openapi()`:

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema["x-speakeasy-retries"] = {"strategy": "backoff", ...}
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
```

## Common Lint Warnings

| Warning | Cause | Fix |
|---------|-------|-----|
| `operation-tag-defined` | Router tags not in global list | Add `openapi_tags` to `FastAPI()` |
| `operation-operationId` | Verbose IDs | Use `generate_unique_id_function` |

## Post-Extraction

```bash
# Validate
speakeasy lint openapi -s openapi.json

# Generate SDK
speakeasy quickstart -s openapi.json -t python -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
- `start-new-sdk-project` - Generate SDK
