# FastAPI OpenAPI Extraction

Detailed guide for extracting and customizing OpenAPI specs from FastAPI applications.

## Extraction Methods

### Script-Based (No Server Needed)

```python
# extract_openapi.py
import json
import sys
sys.path.insert(0, ".")
from main import app  # Adjust to your app's entry point

with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)
```

```bash
python extract_openapi.py
```

This only requires FastAPI and Pydantic - no ASGI server, database, or `.env` setup.

### Runtime Endpoint

```bash
# Start server
uvicorn main:app --reload

# Fetch spec
curl http://localhost:8000/openapi.json > openapi.json
```

### Factory Pattern

```python
# extract_openapi.py
import json
from myapp import create_app

app = create_app()
with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)
```

## Application Metadata

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    version="1.0.0",
    summary="Short description",
    description="Detailed API description with **markdown** support",
    servers=[
        {"url": "https://api.example.com", "description": "Production"},
        {"url": "https://staging.example.com", "description": "Staging"},
    ]
)
```

## Operation IDs

FastAPI generates verbose operation IDs by default. Customize them:

### Custom ID Function (Global)

```python
from fastapi import FastAPI, APIRoute

def custom_generate_unique_id(route: APIRoute) -> str:
    # Convert "read_burger" to "readBurger"
    words = route.name.split("_")
    return words[0] + "".join(w.title() for w in words[1:])

app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
```

### Per-Operation

```python
@app.get("/burgers/{id}", operation_id="getBurger")
def read_burger(id: int):
    pass
```

## Tags and Grouping

```python
tags_metadata = [
    {
        "name": "burgers",
        "description": "Burger operations",
        "externalDocs": {
            "description": "Learn more",
            "url": "https://example.com/docs/burgers"
        }
    },
    {
        "name": "orders",
        "description": "Order management"
    }
]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/burgers", tags=["burgers"])
def list_burgers():
    pass

@app.post("/orders", tags=["orders"])
def create_order():
    pass
```

## Response Models

### Basic Response

```python
from pydantic import BaseModel

class Burger(BaseModel):
    id: int
    name: str
    price: float

@app.get("/burgers/{id}", response_model=Burger)
def get_burger(id: int):
    pass
```

### Multiple Response Types

```python
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

class ErrorResponse(BaseModel):
    message: str = Field(description="Error message")
    code: str = Field(description="Error code")

@app.get(
    "/burgers/{id}",
    response_model=Burger,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Burger not found"
        },
        422: {
            "model": ErrorResponse,
            "description": "Validation error"
        }
    }
)
def get_burger(id: int):
    pass
```

## Request Bodies

```python
from pydantic import BaseModel, Field

class CreateBurger(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Classic Burger"])
    price: float = Field(..., gt=0, examples=[9.99])
    description: str | None = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Classic Burger",
                "price": 9.99,
                "description": "A delicious classic burger"
            }
        }

@app.post("/burgers", response_model=Burger)
def create_burger(burger: CreateBurger):
    pass
```

## Webhooks

```python
from pydantic import BaseModel

class OrderEvent(BaseModel):
    order_id: int
    status: str
    timestamp: str

@app.webhooks.post("order-status-changed", operation_id="onOrderStatusChanged")
def webhook_order_status(body: OrderEvent):
    """
    Triggered when an order status changes.
    The server sends a POST request with order details.
    """
    pass
```

## Speakeasy Extensions

### Global Retries

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
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
        "statusCodes": ["5XX", "429"],
        "retryConnectionErrors": True
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Per-Operation Extensions

```python
@app.get(
    "/burgers",
    openapi_extra={
        "x-speakeasy-group": "burgers",
        "x-speakeasy-name-override": "list",
        "x-speakeasy-retries": {
            "strategy": "backoff",
            "backoff": {
                "initialInterval": 500,
                "maxInterval": 60000,
                "exponent": 1.5
            },
            "statusCodes": ["5XX", "429"]
        }
    }
)
def list_burgers():
    pass
```

### Pagination

```python
@app.get(
    "/burgers",
    openapi_extra={
        "x-speakeasy-pagination": {
            "type": "offsetLimit",
            "inputs": [
                {"name": "offset", "in": "parameters", "type": "offset"},
                {"name": "limit", "in": "parameters", "type": "limit"}
            ],
            "outputs": {
                "results": "$.data",
                "numPages": "$.meta.total_pages"
            }
        }
    }
)
def list_burgers(offset: int = 0, limit: int = 20):
    pass
```

## Security

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, APIKeyHeader

# Bearer token
bearer_scheme = HTTPBearer()

@app.get("/protected", dependencies=[Depends(bearer_scheme)])
def protected_route():
    pass

# API Key
api_key_header = APIKeyHeader(name="X-API-Key")

@app.get("/api-protected")
def api_protected(api_key: str = Depends(api_key_header)):
    pass
```

## Scalar API Documentation

Alternative to Swagger UI:

```python
from scalar_fastapi import get_scalar_api_reference

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title + " - Scalar"
    )
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Circular imports | Use `TYPE_CHECKING` guard or lazy imports |
| Missing response model | Add `response_model` parameter to route |
| Generic operation IDs | Use `generate_unique_id_function` |
| No examples | Add `examples` to Pydantic fields |
