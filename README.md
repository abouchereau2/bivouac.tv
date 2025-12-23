# Bivouac.tv

> The basecamp for adventure, nature & extreme sports documentaries

Discover, rate, and share your favorite outdoor documentaries. Find where to watch climbing, skiing, surfing, and wildlife films across Netflix, Arte, YouTube, and more.

## Tech Stack

**Backend:**
- Django 5.x with Django REST Framework
- PostgreSQL + Redis
- JWT Authentication (dj-rest-auth + allauth)
- uv for dependency management

**Frontend:**
- Vue.js 3 (Composition API + TypeScript)
- Vite + Tailwind CSS v4
- Pinia for state management
- pnpm for package management

## Project Structure

```
bivouac.tv/
├── api/                    # Django REST API
│   ├── apps/
│   │   ├── documentaries/  # Core documentary models
│   │   ├── users/          # User profiles & auth
│   │   ├── reviews/        # Ratings & reviews
│   │   └── submissions/    # User submissions
│   ├── config/
│   │   └── settings/       # Split settings (base/dev/prod)
│   └── pyproject.toml
├── web/                    # Vue.js frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   └── services/
│   └── package.json
├── docker-compose.yml      # PostgreSQL + Redis
└── Makefile               # Development commands
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for PostgreSQL/Redis)
- [uv](https://docs.astral.sh/uv/) - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [pnpm](https://pnpm.io/) - `npm install -g pnpm`

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/bivouac.tv.git
cd bivouac.tv

# Install all dependencies
make install

# Start database services
make db

# Run migrations
make migrate

# Create a superuser
make superuser

# Start development servers
make dev
```

The API will be available at `http://localhost:8000` and the frontend at `http://localhost:5173`.

## Development Commands

```bash
# Start both servers (API + Web)
make dev

# Start only API server
make api

# Start only web server
make web

# Database commands
make db          # Start PostgreSQL + Redis
make db-stop     # Stop database services
make migrate     # Run migrations
make migrations  # Create new migrations
make shell       # Django shell

# Code quality
make lint        # Run linters
make format      # Format code
make test        # Run tests
make test-cov    # Run tests with coverage
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/documentaries/` | List documentaries (with filters) |
| `GET /api/documentaries/{slug}/` | Documentary details |
| `GET /api/documentaries/featured/` | Featured documentaries |
| `GET /api/documentaries/sports/` | List sports |
| `GET /api/documentaries/platforms/` | List platforms |
| `POST /api/auth/login/` | Login |
| `POST /api/auth/registration/` | Register |
| `GET /api/reviews/` | List reviews |
| `POST /api/submissions/` | Submit a documentary |

## Environment Variables

### API (`api/.env`)

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://bivouac:bivouac@localhost:5432/bivouac
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Web (`web/.env`)

```env
VITE_API_URL=http://localhost:8000/api
```

## License

MIT
