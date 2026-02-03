# Django REST Framework OpenAPI Extraction

Detailed guide for extracting OpenAPI specs from Django REST Framework using drf-spectacular.

## Installation

```bash
pip install drf-spectacular
```

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]
```

## Configuration

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'My API',
    'VERSION': '1.0.0',
    'DESCRIPTION': 'API description with **markdown** support',
    'SERVERS': [
        {'url': 'https://api.example.com', 'description': 'Production'},
        {'url': 'https://staging.example.com', 'description': 'Staging'},
    ],
    'CONTACT': {
        'name': 'API Support',
        'email': 'support@example.com',
    },
    'LICENSE': {
        'name': 'MIT',
    },
}
```

## Extraction Command

```bash
# YAML output
python manage.py spectacular --file openapi.yaml

# JSON output
python manage.py spectacular --format openapi-json --file openapi.json
```

## URL Configuration

```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

## ViewSet Customization

### Basic ViewSet

```python
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="List burgers",
        description="Returns a paginated list of all burgers",
        tags=["burgers"]
    ),
    retrieve=extend_schema(
        summary="Get burger",
        description="Returns a single burger by ID",
        tags=["burgers"]
    ),
    create=extend_schema(
        summary="Create burger",
        tags=["burgers"]
    ),
    update=extend_schema(
        summary="Update burger",
        tags=["burgers"]
    ),
    destroy=extend_schema(
        summary="Delete burger",
        tags=["burgers"]
    )
)
class BurgerViewSet(viewsets.ModelViewSet):
    queryset = Burger.objects.all()
    serializer_class = BurgerSerializer
```

### Custom Operation IDs

```python
SPECTACULAR_SETTINGS = {
    # ...
    'OPERATION_ID_GENERATOR': 'myapp.openapi.custom_operation_id',
}

# myapp/openapi.py
def custom_operation_id(auto_id, method, path):
    # Convert "burger_list" to "listBurgers"
    parts = auto_id.split('_')
    if parts[-1] in ('list', 'create', 'retrieve', 'update', 'destroy'):
        action = parts[-1]
        resource = ''.join(p.title() for p in parts[:-1])
        return f"{action}{resource}"
    return auto_id
```

## Serializer Documentation

```python
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

class BurgerSerializer(serializers.ModelSerializer):
    """Burger representation."""

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in USD"
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_formatted_price(self, obj):
        """Price formatted with currency symbol."""
        return f"${obj.price}"

    class Meta:
        model = Burger
        fields = ['id', 'name', 'price', 'description']
```

## Response Customization

### Multiple Response Types

```python
from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(
    responses={
        200: BurgerSerializer,
        404: OpenApiResponse(description="Burger not found"),
        400: OpenApiResponse(description="Invalid request"),
    }
)
def retrieve(self, request, pk=None):
    pass
```

### Inline Schema

```python
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

@extend_schema(
    responses={
        200: inline_serializer(
            name='BurgerStats',
            fields={
                'total_count': serializers.IntegerField(),
                'average_price': serializers.DecimalField(max_digits=10, decimal_places=2),
            }
        )
    }
)
@action(detail=False, methods=['get'])
def stats(self, request):
    pass
```

## Request Body

```python
from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    request=BurgerCreateSerializer,
    examples=[
        OpenApiExample(
            'Classic Burger',
            value={
                'name': 'Classic Burger',
                'price': '9.99',
                'description': 'A delicious classic burger'
            }
        )
    ]
)
def create(self, request):
    pass
```

## Parameters

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='status',
            type=str,
            enum=['available', 'sold_out'],
            description='Filter by availability status'
        ),
        OpenApiParameter(
            name='min_price',
            type=float,
            description='Minimum price filter'
        ),
    ]
)
def list(self, request):
    pass
```

## Speakeasy Extensions

### Via Settings

```python
SPECTACULAR_SETTINGS = {
    # ...
    'EXTENSIONS_INFO': {
        'x-speakeasy-retries': {
            'strategy': 'backoff',
            'backoff': {
                'initialInterval': 500,
                'maxInterval': 60000,
                'exponent': 1.5
            },
            'statusCodes': ['5XX']
        }
    }
}
```

### Per-Operation

```python
@extend_schema(
    extensions={
        'x-speakeasy-group': 'burgers',
        'x-speakeasy-name-override': 'list',
    }
)
def list(self, request):
    pass
```

## Authentication

```python
# settings.py
SPECTACULAR_SETTINGS = {
    # ...
    'SECURITY': [{'BearerAuth': []}],
    'SECURITY_DEFINITIONS': {
        'BearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        },
        'ApiKeyAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
        }
    }
}
```

## Tags

```python
SPECTACULAR_SETTINGS = {
    # ...
    'TAGS': [
        {'name': 'burgers', 'description': 'Burger operations'},
        {'name': 'orders', 'description': 'Order management'},
    ]
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Missing fields in schema | Add `help_text` to serializer fields |
| Generic operation IDs | Configure custom `OPERATION_ID_GENERATOR` |
| Authentication not showing | Configure `SECURITY_DEFINITIONS` in settings |
| Nested serializers not resolved | Use `@extend_schema_serializer` |
