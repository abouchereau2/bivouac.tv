# Bivouac.tv API

Django REST API for Bivouac.tv - the basecamp for adventure, nature & extreme sports documentaries.

## Quick Start

```bash
# Install dependencies
uv sync --dev

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run development server
uv run python manage.py runserver
```

## Project Structure

```
api/
├── apps/
│   ├── documentaries/   # Core documentary models and API
│   ├── users/           # User profiles and authentication
│   ├── reviews/         # Ratings and reviews
│   └── submissions/     # User-submitted documentaries
├── config/
│   ├── settings/
│   │   ├── base.py      # Shared settings
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   └── wsgi.py
└── pyproject.toml
```

## Commands

```bash
# Linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy .

# Testing
uv run pytest
uv run pytest --cov

# Django management
uv run python manage.py <command>
```
