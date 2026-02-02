---
name: extract-openapi-django
description: >-
  Use when extracting OpenAPI from Django REST Framework using drf-spectacular.
  Covers installation, configuration, ViewSet documentation, and Speakeasy
  extensions. Triggers on "Django OpenAPI", "DRF OpenAPI", "Django SDK",
  "drf-spectacular".
license: Apache-2.0
---

# extract-openapi-django

Extract an OpenAPI specification from Django REST Framework using drf-spectacular.

## When to Use

- User has a Django REST Framework app
- User wants to generate an SDK from Django
- User says: "Django OpenAPI", "DRF OpenAPI", "drf-spectacular"

## Installation

```bash
pip install drf-spectacular
```

## Configuration

**settings.py:**

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'My API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SERVERS': [
        {'url': 'https://api.example.com', 'description': 'Production'},
    ],
}
```

## Extraction

```bash
# YAML output
python manage.py spectacular --file openapi.yaml

# JSON output
python manage.py spectacular --format openapi-json --file openapi.json
```

## Adding Speakeasy Extensions

Add global extensions via `SPECTACULAR_SETTINGS`:

```python
SPECTACULAR_SETTINGS = {
    # ...
    'EXTENSIONS_TO_SCHEMA_FUNCTION': lambda generator, request, public: {
        'x-speakeasy-retries': {
            'strategy': 'backoff',
            'backoff': {
                'initialInterval': 500,
                'maxInterval': 60000,
                'exponent': 1.5,
            },
            'statusCodes': ['5XX'],
        }
    }
}
```

For per-operation extensions, use `@extend_schema`:

```python
from drf_spectacular.utils import extend_schema, OpenApiExample

class BookViewSet(viewsets.ModelViewSet):
    @extend_schema(
        operation_id='listBooks',
        extensions={
            'x-speakeasy-group': 'books',
            'x-speakeasy-name-override': 'list'
        }
    )
    def list(self, request):
        ...
```

## Documenting ViewSets

```python
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(description='List all books'),
    create=extend_schema(description='Create a book'),
    retrieve=extend_schema(description='Get a book by ID'),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

## Post-Extraction

```bash
speakeasy lint openapi -s openapi.yaml
speakeasy quickstart -s openapi.yaml -t typescript -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
