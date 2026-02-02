---
short_description: Extract OpenAPI from FastAPI applications
long_description: FastAPI automatically generates OpenAPI documents from Python code. This guide covers customization techniques for better SDK generation including operation IDs, tags, webhooks, retries, and authentication.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/fastapi.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# FastAPI OpenAPI Extraction

FastAPI generates OpenAPI documents automatically from route definitions and Pydantic models. While the default output works, customization improves SDK quality.

## OpenAPI Extraction Method

FastAPI provides built-in OpenAPI generation:

```python
from fastapi import FastAPI

app = FastAPI()

# Access OpenAPI document at runtime
openapi_schema = app.openapi()
```

The document is available at `/openapi.json` by default when the app runs.

### Script-Based Extraction (No Server Needed)

If you can't easily start the server (missing dependencies, no virtualenv, etc.), extract the spec directly with a one-off script:

```python
import json, sys
sys.path.insert(0, ".")
from main import app  # adjust import to match your app's entry point

with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)
```

```bash
python extract_openapi.py
```

> **Tip:** This only requires FastAPI and Pydantic installed — no ASGI server, no database connections, no `.env` setup. Use this as the **first approach** when the server can't be started.

## Installation

No additional packages required - FastAPI includes OpenAPI generation.

## Basic Configuration

### Application Metadata

```python
from fastapi import FastAPI

app = FastAPI(
    title="APItizing Burger API",
    version="0.1.0",
    summary="A simple API to manage burgers and orders",
    description="This API is used to manage burgers and orders in a restaurant"
)
```

### Server Configuration

```python
app = FastAPI(
    servers=[
        {"url": "http://127.0.0.1:8000", "description": "Local server"},
        {"url": "https://api.example.com", "description": "Production server"}
    ]
)
```

### Scalar API Documentation

Alternative to Swagger UI with better SDK integration:

```python
from scalar_fastapi import get_scalar_api_reference

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title + " - Scalar"
    )
```

## Route Customization

### Operation IDs

FastAPI's default operation IDs are verbose. Customize them:

**Method 1: Custom ID function**

```python
from fastapi import FastAPI, APIRoute

def convert_snake_case_to_camel_case(string: str) -> str:
    words = string.split("_")
    return words[0] + "".join(word.title() for word in words[1:])

def custom_generate_unique_id_function(route: APIRoute) -> str:
    return convert_snake_case_to_camel_case(route.name)

app = FastAPI(
    generate_unique_id_function=custom_generate_unique_id_function
)
```

**Method 2: Per-operation ID**

```python
@app.get("/burger/{burger_id}", operation_id="readBurger")
def read_burger(burger_id: int):
    pass
```

### Tags and Tag Metadata

```python
tags_metadata = [
    {
        "name": "burger",
        "description": "Operations related to burgers",
        "externalDocs": {
            "description": "Burger external docs",
            "url": "https://en.wikipedia.org/wiki/Hamburger"
        }
    }
]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/burger/{burger_id}", tags=["burger"])
def read_burger(burger_id: int):
    return {"burger_id": burger_id}
```

### Typed Responses

```python
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

class ResponseMessage(BaseModel):
    message: str = Field(description="The response message")

OPENAPI_RESPONSE_BURGER_NOT_FOUND = {
    "model": ResponseMessage,
    "description": "Burger not found"
}

@app.get(
    "/burger/{burger_id}",
    response_model=BurgerOutput,
    responses={404: OPENAPI_RESPONSE_BURGER_NOT_FOUND},
    tags=["burger"]
)
def read_burger(burger_id: int):
    for burger in burgers_db:
        if burger.id == burger_id:
            return burger
    return JSONResponse(
        status_code=404,
        content={"message": f"Burger with id {burger_id} does not exist"}
    )
```

## Webhooks

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Order(BaseModel):
    id: int
    note: str

@app.webhooks.post(
    "order-status-changed",
    operation_id="webhookOrderStatusChanged"
)
def webhook_order_status_changed(body: Order):
    """
    When an order status is changed, this webhook will be triggered.

    The server will send a POST request with the order details to the webhook URL.
    """
    pass
```

## Speakeasy Extensions

### Retries (Global)

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes
    )

    openapi_schema["x-speakeasy-retries"] = {
        "strategy": "backoff",
        "backoff": {
            "initialInterval": 500,
            "maxInterval": 60000,
            "maxElapsedTime": 3600000,
            "exponent": 1.5
        },
        "statusCodes": ["5XX"],
        "retryConnectionErrors": True
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Retries (Per-Operation)

```python
@app.get(
    "/burger/",
    openapi_extra={
        "x-speakeasy-retries": {
            "strategy": "backoff",
            "backoff": {
                "initialInterval": 500,
                "maxInterval": 60000,
                "maxElapsedTime": 3600000,
                "exponent": 1.5
            },
            "statusCodes": ["5XX"],
            "retryConnectionErrors": True
        }
    }
)
def list_burgers():
    return []
```

## Authentication

```python
from fastapi.security import APIKeyHeader

API_KEY = "your-apitizing-api-key"

header_scheme = APIKeyHeader(
    name=API_KEY,
    auto_error=True,
    description="API Key for the Burger listing API",
    scheme_name="api_key"
)

@app.get("/burger/", tags=["burger"])
def list_burgers(key: str = Depends(header_scheme)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return [BurgerOutput(**burger_data.dict()) for burger_data in burgers_db]
```

## Form Data and File Uploads

### Form Data

FastAPI correctly documents form data endpoints with `application/x-www-form-urlencoded` content type:

```python
from fastapi import Form
from typing import Annotated

@app.post("/burger/create/")
async def create_burger_form(
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    price: Annotated[float, Form()]
):
    """Create a new burger using form data"""
    return {
        "name": name,
        "description": description,
        "price": price
    }
```

The generated OpenAPI will show:

```yaml
requestBody:
  content:
    application/x-www-form-urlencoded:
      schema:
        type: object
        properties:
          name:
            type: string
          description:
            type: string
          price:
            type: number
        required:
          - name
          - description
          - price
```

### File Uploads

File uploads are documented with `multipart/form-data` content type:

```python
from fastapi import File, UploadFile

@app.post("/burger/image/")
async def upload_burger_image(
    burger_id: Annotated[int, Form()],
    image: Annotated[UploadFile, File()]
):
    """Upload an image for a burger"""
    contents = await image.read()
    return {
        "burger_id": burger_id,
        "filename": image.filename,
        "content_type": image.content_type,
        "size": len(contents)
    }
```

### Advanced Form Validation

Combine Pydantic models with Form for validation:

```python
from pydantic import BaseModel, Field

class BurgerFormData(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=200)
    price: float = Field(..., gt=0, le=100)

@app.post("/burger/create/validated/")
async def create_burger_validated(
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    price: Annotated[float, Form()]
):
    burger_data = BurgerFormData(
        name=name,
        description=description,
        price=price
    )
    return burger_data
```

## Common Issues

### Datetime Serialization

> **Note:** Pydantic datetime serialization is not timezone-aware by default. Use `AwareDatetime` for RFC 3339 compliance:

```python
from pydantic.types import AwareDatetime

class Event(BaseModel):
    timestamp: AwareDatetime
```

### Poor Operation IDs

Default: `read_burger_burger__burger_id__get`
After customization: `readBurger`

Use custom ID generation or per-operation IDs to fix this.

## Common FastAPI Lint Warnings

When running `speakeasy lint openapi` on a FastAPI-generated spec, you may see warnings that are specific to how FastAPI generates OpenAPI docs. These are **non-blocking** — SDK generation will still succeed.

| Warning | Cause | Fix |
|---------|-------|-----|
| `operation-tag-defined` — tag "X" is not defined at the global level | FastAPI `APIRouter(tags=["X"])` sets tags per-router but doesn't add them to the global `tags` array | Add `openapi_tags` metadata to the `FastAPI()` constructor (see [Tags and Tag Metadata](#tags-and-tag-metadata)) |
| `operation-operationId` — operationId is verbose | FastAPI default IDs like `read_burger_burger__burger_id__get` | Use `custom_generate_unique_id_function` or per-route `operation_id=` |

**Quick fix for missing global tags:**

```python
# Collect all tags used in routers and define them globally
app = FastAPI(
    openapi_tags=[
        {"name": "users", "description": "User operations"},
        {"name": "orders", "description": "Order operations"},
        # ... add all tags used in your APIRouters
    ]
)
```

> **Note:** These warnings don't block SDK generation. Fix them for a cleaner spec, or ignore them if you're prototyping.

## Validation Command

```bash
speakeasy lint openapi -s openapi.yaml
```

## Next Steps

After extracting the OpenAPI document:

1. Save it to a file (usually at `/openapi.json` endpoint)
2. Run `speakeasy lint openapi -s openapi.yaml`
3. Generate SDK: `speakeasy quickstart --skip-interactive --output console -s openapi.yaml -t python -o ./sdk`
4. Set up CI/CD automation for SDK regeneration

## Reference

- FastAPI docs: https://fastapi.tiangolo.com
- Pydantic models: https://docs.pydantic.dev
- OpenAPI operations: `/docs` endpoint in running app

---

## Pre-defined TODO List

When executing this workflow, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Locate FastAPI application file | Locating FastAPI application file |
| 2 | Verify FastAPI and Pydantic are installed | Verifying FastAPI and Pydantic installation |
| 3 | Check application metadata configuration | Checking application metadata configuration |
| 4 | Extract OpenAPI spec (script or server — see below) | Extracting OpenAPI spec |
| 5 | Save OpenAPI spec to file | Saving OpenAPI spec to file |
| 6 | Validate spec with speakeasy lint | Validating spec with speakeasy lint |
| 7 | Review operation IDs in spec | Reviewing operation IDs in spec |
| 8 | Review tags and descriptions | Reviewing tags and descriptions |

**Usage:**
```
TodoWrite([
  {content: "Locate FastAPI application file", status: "pending", activeForm: "Locating FastAPI application file"},
  {content: "Verify FastAPI and Pydantic are installed", status: "pending", activeForm: "Verifying FastAPI and Pydantic installation"},
  {content: "Check application metadata configuration", status: "pending", activeForm: "Checking application metadata configuration"},
  {content: "Extract OpenAPI spec (script or server)", status: "pending", activeForm: "Extracting OpenAPI spec"},
  {content: "Save OpenAPI spec to file", status: "pending", activeForm: "Saving OpenAPI spec to file"},
  {content: "Validate spec with speakeasy lint", status: "pending", activeForm: "Validating spec with speakeasy lint"},
  {content: "Review operation IDs in spec", status: "pending", activeForm: "Reviewing operation IDs in spec"},
  {content: "Review tags and descriptions", status: "pending", activeForm: "Reviewing tags and descriptions"}
])
```

**Step 4 — Extraction method decision:**
- **Script extraction (preferred):** Use `app.openapi()` in a one-off script. Works without running the server, no ASGI server or database needed. See [Script-Based Extraction](#script-based-extraction-no-server-needed).
- **Server extraction (fallback):** Start the app with `uvicorn main:app`, fetch `/openapi.json`, then stop the server. Use this only if `app.openapi()` fails due to lazy initialization or middleware dependencies.

**Customization sub-workflow (optional):**

If steps 9-10 reveal issues with operation IDs or tags, add these nested customization TODOs:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 11 | Update operation IDs in route decorators | Updating operation IDs in route decorators |
| 12 | Add or improve tags metadata | Adding or improving tags metadata |
| 13 | Configure Speakeasy extensions if needed | Configuring Speakeasy extensions |
| 14 | Restart FastAPI application | Restarting FastAPI application |
| 15 | Re-fetch OpenAPI JSON | Re-fetching OpenAPI JSON |
| 16 | Save updated spec to file | Saving updated spec to file |
| 17 | Re-validate with speakeasy validate | Re-validating with speakeasy validate |

**Common customizations to consider:**
- **Poor operation IDs**: Use `custom_generate_unique_id_function` or per-route `operation_id`
- **Missing tags**: Add `tags=["category"]` to routes and `openapi_tags` metadata to app
- **Retry configuration**: Add `x-speakeasy-retries` via `openapi_extra` or `custom_openapi()`
- **Authentication**: Use FastAPI security schemes (`APIKeyHeader`, `OAuth2`, etc.)
- **Webhooks**: Define with `@app.webhooks.post()`

**Note:** Only execute customization sub-workflow if quality issues are found. If the generated spec is already good, skip steps 11-17.
