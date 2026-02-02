---
short_description: Extract OpenAPI from Django REST Framework using drf-spectacular
long_description: Django REST Framework requires drf-spectacular for OpenAPI generation. This guide covers installation, ViewSet documentation, schema customization, and extending with decorators.
source:
  repo: "speakeasy-api/speakeasy.com"
  path: "src/content/openapi/frameworks/django.mdx"
  ref: "af7c36a9ec957336fb799151a4e5af3ae293831e"
  last_reconciled: "2025-12-11"
---

# Django OpenAPI Extraction

Django REST Framework requires `drf-spectacular` package for OpenAPI generation.

## Installation

```bash
pip install drf-spectacular
```

## Configuration

**settings.py**:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'drf_spectacular',
    'books',  # your app
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Library API',
    'DESCRIPTION': 'A simple API for managing books in a library',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Local Development server'},
        {'url': 'https://api.example.com', 'description': 'Production server'},
    ],
    'TAGS': [
        {'name': 'books', 'description': 'Book operations'},
    ],
    'EXTENSIONS_TO_SCHEMA_FUNCTION': lambda generator, request, public: {
        'x-speakeasy-retries': {
            'strategy': 'backoff',
            'backoff': {
                'initialInterval': 500,
                'maxInterval': 60000,
                'maxElapsedTime': 3600000,
                'exponent': 1.5,
            },
            'statusCodes': ['5XX'],
            'retryConnectionErrors': True,
        }
    }
}
```

**urls.py**:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('books.urls')),
]
```

## Model Definition

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_year = models.IntegerField()
```

## Serializer

```python
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_year']
```

## ViewSet with Customization

```python
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse

@extend_schema_view(
    list=extend_schema(
        summary="List all books",
        description="Get a list of all books in the library.",
        responses={200: BookSerializer(many=True)},
        tags=["books"],
    ),
    retrieve=extend_schema(
        summary="Get a specific book",
        description="Retrieve details for a specific book by its ID.",
        responses={
            200: BookSerializer,
            404: OpenApiResponse(description="Book not found"),
        },
        tags=["books"],
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @extend_schema(
        summary="Find books by the same author",
        description="Returns all books written by the same author as the specified book.",
        responses={
            200: BookSerializer(many=True),
            404: OpenApiResponse(
                description="Book not found",
                examples=[
                    OpenApiExample(
                        "Error Response",
                        value={"error": "Book not found"},
                        status_codes=["404"],
                    )
                ]
            )
        },
        tags=["books", "authors"],
        parameters=[
            OpenApiParameter(
                name="sort",
                description="Sort order for the books",
                required=False,
                type=str,
                enum=["title", "published_year"],
            ),
        ],
        examples=[
            OpenApiExample(
                "Book list example",
                value=[
                    {
                        "id": 1,
                        "title": "The Great Gatsby",
                        "author": "F. Scott Fitzgerald",
                        "published_year": 1925
                    }
                ],
                response_only=True,
                status_codes=["200"],
            )
        ],
        extensions={
            "x-speakeasy-retries": {
                "strategy": "backoff",
                "backoff": {
                    "initialInterval": 500,
                    "maxInterval": 60000,
                    "maxElapsedTime": 3600000,
                    "exponent": 1.5,
                },
                "statusCodes": ["5XX"],
                "retryConnectionErrors": True,
            }
        }
    )
    @action(detail=True, methods=['get'])
    def author_books(self, request, pk=None):
        book = self.get_object()
        author_books = Book.objects.filter(author=book.author).exclude(id=book.id)
        serializer = self.get_serializer(author_books, many=True)
        return Response(serializer.data)
```

## OpenAPI Generation

```bash
python manage.py spectacular --file openapi.yaml
```

## Migration and Server

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Access:
- API: `http://127.0.0.1:8000/api/books/`
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- OpenAPI Schema: `http://127.0.0.1:8000/api/schema/`

## Validation

```bash
speakeasy validate openapi -s openapi.yaml
```

## SDK Generation

```bash
speakeasy quickstart --schema openapi.yaml --target python --out-dir ./sdk
```

## Reference

- drf-spectacular: https://drf-spectacular.readthedocs.io
- Django REST Framework: https://www.django-rest-framework.org

---

## Pre-defined TODO List

When extracting OpenAPI from Django REST Framework, initialize your TODO list with:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Verify Django REST Framework app exists | Verifying Django REST Framework app exists |
| 2 | Install drf-spectacular package | Installing drf-spectacular package |
| 3 | Configure drf-spectacular in settings.py | Configuring drf-spectacular in settings.py |
| 4 | Create serializers for models | Creating serializers for models |
| 5 | Create ViewSets with @extend_schema decorators | Creating ViewSets with @extend_schema decorators |
| 6 | Generate OpenAPI document with spectacular | Generating OpenAPI document with spectacular |
| 7 | Validate spec with speakeasy validate | Validating spec with speakeasy validate |

**Usage:**
```
TodoWrite([
  {content: "Verify Django REST Framework app exists", status: "pending", activeForm: "Verifying Django REST Framework app exists"},
  {content: "Install drf-spectacular package", status: "pending", activeForm: "Installing drf-spectacular package"},
  {content: "Configure drf-spectacular in settings.py", status: "pending", activeForm: "Configuring drf-spectacular in settings.py"},
  {content: "Create serializers for models", status: "pending", activeForm: "Creating serializers for models"},
  {content: "Create ViewSets with @extend_schema decorators", status: "pending", activeForm: "Creating ViewSets with @extend_schema decorators"},
  {content: "Generate OpenAPI document with spectacular", status: "pending", activeForm: "Generating OpenAPI document with spectacular"},
  {content: "Validate spec with speakeasy validate", status: "pending", activeForm: "Validating spec with speakeasy validate"}
])
```

**Nested workflows:**
- For validation issues, see `spec-first/validation.md`
- For SDK generation after extraction, see `plans/sdk-generation.md`

