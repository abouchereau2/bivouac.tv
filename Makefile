# ============================================
# Bivouac.tv - Development Makefile
# ============================================

.PHONY: help install dev api web db migrate shell test lint format clean

# Default target
help:
	@echo "Bivouac.tv Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  make install     Install all dependencies (api + web)"
	@echo ""
	@echo "Development:"
	@echo "  make dev         Start both API and web servers"
	@echo "  make api         Start Django API server only"
	@echo "  make web         Start Vue.js dev server only"
	@echo ""
	@echo "Database:"
	@echo "  make db          Start PostgreSQL and Redis containers"
	@echo "  make db-stop     Stop database containers"
	@echo "  make migrate     Run Django migrations"
	@echo "  make migrations  Create new migrations"
	@echo "  make shell       Open Django shell"
	@echo "  make superuser   Create a superuser"
	@echo ""
	@echo "Quality:"
	@echo "  make test        Run tests"
	@echo "  make lint        Run linters"
	@echo "  make format      Format code"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       Remove generated files"

# ============================================
# Setup
# ============================================

install: install-api install-web

install-api:
	@echo "Installing API dependencies..."
	cd api && uv sync --all-extras

install-web:
	@echo "Installing web dependencies..."
	cd web && pnpm install

# ============================================
# Development servers
# ============================================

dev:
	@echo "Starting development servers..."
	@make -j2 api web

api:
	@echo "Starting Django API server..."
	cd api && uv run python manage.py runserver

web:
	@echo "Starting Vue.js dev server..."
	cd web && pnpm dev

# ============================================
# Database
# ============================================

db:
	@echo "Starting database services..."
	docker compose up -d db redis

db-stop:
	@echo "Stopping database services..."
	docker compose down

migrate:
	@echo "Running migrations..."
	cd api && uv run python manage.py migrate

migrations:
	@echo "Creating migrations..."
	cd api && uv run python manage.py makemigrations

shell:
	@echo "Opening Django shell..."
	cd api && uv run python manage.py shell_plus

superuser:
	@echo "Creating superuser..."
	cd api && uv run python manage.py createsuperuser

# ============================================
# Quality
# ============================================

test:
	@echo "Running tests..."
	cd api && uv run pytest

test-cov:
	@echo "Running tests with coverage..."
	cd api && uv run pytest --cov --cov-report=html

lint:
	@echo "Running linters..."
	cd api && uv run ruff check .
	cd web && pnpm lint 2>/dev/null || true

format:
	@echo "Formatting code..."
	cd api && uv run ruff format .
	cd api && uv run ruff check --fix .

typecheck:
	@echo "Type checking..."
	cd api && uv run mypy .
	cd web && pnpm vue-tsc --noEmit

# ============================================
# Build
# ============================================

build-web:
	@echo "Building frontend..."
	cd web && pnpm build

# ============================================
# Cleanup
# ============================================

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf api/htmlcov 2>/dev/null || true
	rm -rf web/dist 2>/dev/null || true
