# Flask OpenAPI Extraction

Detailed guide for extracting OpenAPI specs from Flask applications using flask-openapi3 or apispec.

## Option 1: flask-openapi3 (Recommended)

### Installation

```bash
pip install flask-openapi3
```

### Setup

```python
from flask_openapi3 import OpenAPI, Info, Server

info = Info(
    title="My API",
    version="1.0.0",
    description="API description with **markdown** support"
)

servers = [
    Server(url="https://api.example.com", description="Production"),
    Server(url="https://staging.example.com", description="Staging"),
]

app = OpenAPI(__name__, info=info, servers=servers)
```

### Extraction

```bash
# Runtime endpoint (default)
curl http://localhost:5000/openapi/openapi.json > openapi.json

# Or YAML
curl http://localhost:5000/openapi/openapi.yaml > openapi.yaml
```

### Script-Based Extraction

```python
# extract_openapi.py
import json
from app import app

with open("openapi.json", "w") as f:
    json.dump(app.api_doc, f, indent=2)
```

### Route Documentation

```python
from flask_openapi3 import OpenAPI
from pydantic import BaseModel, Field

class BurgerPath(BaseModel):
    id: str = Field(..., description="Burger ID")

class BurgerQuery(BaseModel):
    limit: int = Field(20, description="Page size", ge=1, le=100)
    offset: int = Field(0, description="Page offset", ge=0)

class Burger(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Burger name", max_length=100)
    price: float = Field(..., description="Price in USD", gt=0)
    description: str | None = Field(None, description="Optional description")

class CreateBurgerRequest(BaseModel):
    name: str = Field(..., description="Burger name", max_length=100)
    price: float = Field(..., description="Price in USD", gt=0)
    description: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Classic Burger",
                "price": 9.99,
                "description": "A delicious classic burger"
            }
        }

@app.get(
    "/burgers",
    tags=["burgers"],
    summary="List burgers",
    description="Returns a paginated list of all burgers",
    operation_id="listBurgers"
)
def list_burgers(query: BurgerQuery):
    pass

@app.get(
    "/burgers/<id>",
    tags=["burgers"],
    summary="Get burger",
    operation_id="getBurger"
)
def get_burger(path: BurgerPath):
    pass

@app.post(
    "/burgers",
    tags=["burgers"],
    summary="Create burger",
    operation_id="createBurger"
)
def create_burger(body: CreateBurgerRequest):
    pass
```

### Response Documentation

```python
from flask_openapi3 import OpenAPI
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    message: str
    code: str

@app.get(
    "/burgers/<id>",
    responses={
        200: Burger,
        404: ErrorResponse
    }
)
def get_burger(path: BurgerPath):
    pass
```

## Option 2: apispec with Marshmallow

### Installation

```bash
pip install apispec apispec-webframeworks marshmallow
```

### Setup

```python
from flask import Flask
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

app = Flask(__name__)

spec = APISpec(
    title="My API",
    version="1.0.0",
    openapi_version="3.0.3",
    info={"description": "API description with **markdown** support"},
    servers=[
        {"url": "https://api.example.com", "description": "Production"},
        {"url": "https://staging.example.com", "description": "Staging"},
    ],
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)
```

### Schema Definition

```python
from marshmallow import Schema, fields

class BurgerSchema(Schema):
    """Burger representation."""
    id = fields.Str(metadata={"description": "Unique identifier"})
    name = fields.Str(required=True, metadata={"description": "Burger name"})
    price = fields.Float(required=True, metadata={"description": "Price in USD"})
    description = fields.Str(metadata={"description": "Optional description"})

class CreateBurgerSchema(Schema):
    """Create burger request."""
    name = fields.Str(required=True, metadata={"description": "Burger name"})
    price = fields.Float(required=True, metadata={"description": "Price in USD"})
    description = fields.Str(metadata={"description": "Optional description"})

# Register schemas
spec.components.schema("Burger", schema=BurgerSchema)
spec.components.schema("CreateBurger", schema=CreateBurgerSchema)
```

### Route Documentation

```python
@app.get("/burgers")
def list_burgers():
    """List burgers.
    ---
    get:
      tags:
        - burgers
      summary: List burgers
      operationId: listBurgers
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
          description: Page size
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
          description: Page offset
      responses:
        200:
          description: List of burgers
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Burger'
    """
    pass

# Register with spec
with app.test_request_context():
    spec.path(view=list_burgers)
```

### Extraction

```python
# extract_openapi.py
import json
from app import app, spec

# Register all views
with app.test_request_context():
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            spec.path(view=app.view_functions[rule.endpoint])

with open("openapi.json", "w") as f:
    json.dump(spec.to_dict(), f, indent=2)
```

## Speakeasy Extensions

### With flask-openapi3

```python
from flask_openapi3 import OpenAPI

# Global extensions via custom OpenAPI
class CustomOpenAPI(OpenAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def api_doc(self):
        doc = super().api_doc
        doc["x-speakeasy-retries"] = {
            "strategy": "backoff",
            "backoff": {
                "initialInterval": 500,
                "maxInterval": 60000,
                "exponent": 1.5
            },
            "statusCodes": ["5XX", "429"]
        }
        return doc

app = CustomOpenAPI(__name__, info=info)

# Per-operation extensions
@app.get(
    "/burgers",
    openapi_extensions={
        "x-speakeasy-group": "burgers",
        "x-speakeasy-name-override": "list"
    }
)
def list_burgers():
    pass
```

### With apispec

```python
@app.get("/burgers")
def list_burgers():
    """List burgers.
    ---
    get:
      operationId: listBurgers
      x-speakeasy-group: burgers
      x-speakeasy-name-override: list
      x-speakeasy-retries:
        strategy: backoff
        backoff:
          initialInterval: 500
          maxInterval: 60000
          exponent: 1.5
        statusCodes:
          - "5XX"
          - "429"
    """
    pass
```

### Pagination Extension

```python
@app.get(
    "/burgers",
    openapi_extensions={
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
def list_burgers(query: BurgerQuery):
    pass
```

## Authentication

### flask-openapi3

```python
from flask_openapi3 import OpenAPI, HTTPBearer, APIKey

jwt_security = HTTPBearer()
api_key_security = APIKey(name="X-API-Key", in_="header")

app = OpenAPI(
    __name__,
    info=info,
    security_schemes={
        "bearer-auth": jwt_security,
        "api-key": api_key_security
    }
)

# Apply globally
app.security = [{"bearer-auth": []}]

# Or per-route
@app.get("/protected", security=[{"bearer-auth": []}])
def protected_route():
    pass

@app.get("/public", security=[])
def public_route():
    pass
```

### apispec

```python
spec.components.security_scheme(
    "bearer-auth",
    {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
)

spec.components.security_scheme(
    "api-key",
    {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
    }
)
```

## File Upload

```python
from flask_openapi3 import OpenAPI, FileStorage
from pydantic import BaseModel

class UploadForm(BaseModel):
    file: FileStorage

@app.post("/upload", tags=["files"])
def upload_file(form: UploadForm):
    """Upload a file."""
    pass
```

## Tags

```python
from flask_openapi3 import OpenAPI, Tag, ExternalDocumentation

tags = [
    Tag(
        name="burgers",
        description="Burger operations",
        externalDocs=ExternalDocumentation(
            description="Learn more",
            url="https://example.com/docs/burgers"
        )
    ),
    Tag(name="orders", description="Order management")
]

app = OpenAPI(__name__, info=info, tags=tags)
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Pydantic v2 compatibility | Use flask-openapi3>=3.0.0 for Pydantic v2 |
| Missing schemas | Ensure models inherit from BaseModel |
| Wrong operation IDs | Add explicit `operation_id` parameter |
| Security not showing | Configure `security_schemes` in app init |
