---
name: extract-openapi-flask
description: >-
  Use when extracting OpenAPI from Flask using flask-smorest or apispec.
  Triggers on "Flask OpenAPI", "flask-smorest", "Flask SDK", "Flask API spec".
license: Apache-2.0
---

# extract-openapi-flask

Extract an OpenAPI specification from Flask using flask-smorest or apispec.

## When to Use

- User has a Flask application with flask-smorest or apispec
- User wants to generate an SDK from Flask
- User says: "Flask OpenAPI", "flask-smorest", "Flask SDK"

## Using flask-smorest

### Installation

```bash
pip install flask-smorest
```

### Extraction

```bash
flask openapi write openapi.json
```

Or programmatically:

```python
import json
from myapp import create_app

app = create_app()
with app.app_context():
    spec = app.extensions['flask-smorest'].spec
    print(json.dumps(spec.to_dict()))
```

## Using apispec

```python
import json
from myapp import create_app, spec

app = create_app()
with app.app_context():
    with open("openapi.json", "w") as f:
        json.dump(spec.to_dict(), f, indent=2)
```

## Adding Speakeasy Extensions

Modify the spec after generation:

```python
spec_dict = spec.to_dict()
spec_dict['x-speakeasy-retries'] = {
    'strategy': 'backoff',
    'statusCodes': ['5XX']
}

# Per-operation
spec_dict['paths']['/items']['get']['x-speakeasy-group'] = 'items'
```

Or use an overlay file for cleaner separation.

## Post-Extraction

```bash
speakeasy lint openapi -s openapi.json
speakeasy quickstart -s openapi.json -t python -o ./sdk
```

## Related Skills

- `configure-speakeasy-extensions` - Add x-speakeasy-* extensions
- `manage-openapi-overlays` - Fix issues via overlay
