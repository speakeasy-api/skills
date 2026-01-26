---
short_description: Extract OpenAPI from Flask applications using flask-smorest
long_description: Flask requires flask-smorest package for OpenAPI generation. This guide covers setup, schema definition with marshmallow, and OpenAPI customization for SDK generation.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/flask.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Flask OpenAPI Extraction

Flask does not support OpenAPI generation out-of-the-box. Use `flask-smorest` package.

## Installation

```bash
pip install flask-smorest
```

## Basic Setup

```python
from flask import Flask
from flask_smorest import Api

app = Flask(__name__)
app.config["API_TITLE"] = "Library API"
app.config["API_VERSION"] = "v0.0.1"
app.config["OPENAPI_VERSION"] = "3.1.0"
app.config["OPENAPI_DESCRIPTION"] = "A simple library API"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
```

## Server Configuration

```python
api.spec.options["servers"] = [
    {
        "url": "http://127.0.0.1:5000",
        "description": "Local development server"
    }
]
```

## Schema Definition

Flask-smorest uses marshmallow for schemas:

```python
from marshmallow import Schema, fields

class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    description = fields.Str()
```

## Blueprint Routes

```python
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint("Books", "books", url_prefix="/books", description="Operations on books")

@blp.route("/")
class BookList(MethodView):
    @blp.response(200, BookSchema(many=True))
    @blp.paginate()
    def get(self, pagination_parameters):
        """List all books"""
        query = Book.query
        paginated_books = query.paginate(
            page=pagination_parameters.page,
            per_page=pagination_parameters.page_size,
            error_out=False
        )
        pagination_parameters.item_count = paginated_books.total
        return paginated_books.items

    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def post(self, new_data):
        """Create a new book"""
        book = Book(**new_data)
        db.session.add(book)
        db.session.commit()
        return book
```

## Response Documentation

```python
@blp.response(200, BookSchema(many=True))  # Success response
@blp.response(404, MessageSchema)           # Error response
```

## Pagination

```python
@blp.paginate()
def get(self, pagination_parameters):
    # Access page and page_size
    page = pagination_parameters.page
    per_page = pagination_parameters.page_size
```

## Speakeasy Retries

```python
app.config["API_SPEC_OPTIONS"] = {
    "x-speakeasy-retries": {
        'strategy': 'backoff',
        'backoff': {
            'initialInterval': 500,
            'maxInterval': 60000,
            'maxElapsedTime': 3600000,
            'exponent': 1.5
        },
        'statusCodes': ['5XX'],
        'retryConnectionErrors': True
    }
}
```

## OpenAPI Document Generation

```bash
flask openapi write --format=yaml openapi.yaml
```

## Serving OpenAPI Document

```python
import yaml

@app.route("/openapi.yaml")
def openapi_yaml():
    spec = api.spec.to_dict()
    return app.response_class(
        yaml.dump(spec, default_flow_style=False),
        mimetype="application/x-yaml"
    )
```

## Validation

```bash
speakeasy validate openapi -s openapi.yaml
```

## SDK Generation

```bash
speakeasy quickstart --schema openapi.yaml --target python --out-dir ./sdk
```

## Reference

- flask-smorest: https://flask-smorest.readthedocs.io
- marshmallow: https://marshmallow.readthedocs.io

---

## Pre-defined TODO List

When extracting OpenAPI from Flask, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Flask application exists | Verifying Flask application exists |
| 2 | Install flask-smorest package | Installing flask-smorest package |
| 3 | Configure flask-smorest in application | Configuring flask-smorest in application |
| 4 | Define marshmallow schemas | Defining marshmallow schemas |
| 5 | Create Flask blueprints with documentation | Creating Flask blueprints with documentation |
| 6 | Generate OpenAPI document | Generating OpenAPI document |
| 7 | Validate spec with speakeasy validate | Validating spec with speakeasy validate |

**Usage:**
```
TodoWrite([
  {content: "Verify Flask application exists", status: "pending", activeForm: "Verifying Flask application exists"},
  {content: "Install flask-smorest package", status: "pending", activeForm: "Installing flask-smorest package"},
  {content: "Configure flask-smorest in application", status: "pending", activeForm: "Configuring flask-smorest in application"},
  {content: "Define marshmallow schemas", status: "pending", activeForm: "Defining marshmallow schemas"},
  {content: "Create Flask blueprints with documentation", status: "pending", activeForm: "Creating Flask blueprints with documentation"},
  {content: "Generate OpenAPI document", status: "pending", activeForm: "Generating OpenAPI document"},
  {content: "Validate spec with speakeasy validate", status: "pending", activeForm: "Validating spec with speakeasy validate"}
])
```

**Nested workflows:**
- For validation issues, see `spec-first/validation.md`
- For SDK generation after extraction, see `plans/sdk-generation.md`
