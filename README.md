# GeoAlchemy2 Alembic Pydantic FastAPI Demo

A reference implementation demonstrating how to use GeoAlchemy2 with Pydantic, Alembic, FastAPI, PostgreSQL with the PostGIS extension, and Spatialite (for local development).

> **⚠️ Disclaimer:** This repository is for demonstration and learning purposes only. It is not intended for production use without appropriate security hardening and testing.

## Overview

This repository provides a minimal working example of a geospatial API built with:

- **[FastAPI](https://fastapi.tiangolo.com)**: Modern Python web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** + **[GeoAlchemy2](https://geoalchemy-2.readthedocs.io/en/latest/)**: ORM with PostGIS geometry support
- **[Pydantic](https://docs.pydantic.dev/latest/)**: Data validation and serialisation
- **[Alembic](https://alembic.sqlalchemy.org/en/latest/)**: Database migrations
- **[PostgreSQL](https://www.postgresql.org/)** + **[PostGIS](https://postgis.net/)**: Spatial database (production)
- **[SpatiaLite](https://www.gaia-gis.it/fossil/libspatialite/index)**: Spatial SQLite database (local development)
- **[uv](https://docs.astral.sh/uv/)**: Fast Python package manager

## Project Structure
```text
geoalchemy-alembic-fastapi-example/
├── lib/
│   └── mod_spatialite-5.1.0-win-amd64/
│       ├── mod_spatialite.dll
│       └── ... (dependency DLLs)
├── src/
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 0249d898dac8_init_example_point.py
│   │   ├── env.py
│   │   ├── README
│   │   └── script.py.mako
│   ├── app/
│   │   ├── __init__.py
│   │   ├── crud.py
│   │   ├── db.py
│   │   ├── health.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── settings.py
│   └── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
├── spatialite.py
└── uv.lock
```

## Architecture

The application supports two database backends:

### Development (SpatiaLite)

- File-based SQLite database with SpatiaLite extension
- No Docker required for local development
- Ideal for rapid iteration and testing

### Production (PostGIS)

Docker Compose brings up two containers:

- **postgis**: PostgreSQL with PostGIS extension, initialised via `setup/init-db.sh`
- **fastapi-app**: The FastAPI application serving the geospatial API

## Prerequisites

- uv package manager
- Docker and Docker Compose (for production mode only)
- SpatiaLite DLLs (for development on Windows see below)

## Getting Started

### 1. Install uv

**PowerShell (Windows):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) for more options.

### 2. Install dependencies and activate virtual environment
```bash
uv sync
```

**PowerShell (Windows):**
```powershell
.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 3. Configure environment

Create your environment file from the example:
```bash
cp .env.example .env
```

Edit `.env` to adjust values as needed for your setup.

### 4. Set up SpatiaLite (Windows development only)

Download SpatiaLite binaries from https://www.gaia-gis.it/gaia-sins/windows-bin-amd64/ and extract to [./lib/mod_spatialite-5.1.0-win-amd64](./lib/mod_spatialite-5.1.0-win-amd64).

On Mac/Linux, install via package manager:
```bash
# macOS
brew install spatialite-tools

# Ubuntu/Debian
sudo apt-get install libsqlite3-mod-spatialite
```

## Running in Development Mode (Local SpatiaLite DB)

Development mode uses a local SpatiaLite database file, no Docker required.

### 1. Set environment to development

In your `.env` file:
```env
ENVIRONMENT=development
SPATIALITE_PATH=./geo.db
```

### 2. Run migrations
```bash
cd src/
alembic upgrade head
```

This creates `geo.db` in the `src/` directory with all spatial tables.

### 3. Start the API
```bash
cd src/
uv run fastapi dev app/main.py
```

The API is now available at http://localhost:8000/api/docs

## Running in Production Mode (Containerised PostGIS)

Production mode uses PostgreSQL with PostGIS in Docker containers.

### 1. Set environment to production

In your `.env` file:
```env
ENVIRONMENT=production
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
```

### 2. Start the database and API
```bash
docker compose up --build -d
```

### 3. Run migrations
```bash
cd src/
alembic upgrade head
```

### 4. Verify the setup
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "ok", "db": "up"}
```
51.50341458011505, -0.11953217890123567
## Usage

### Create a point
```bash
curl -X POST http://localhost:8000/api/points \
  -H "Content-Type: application/json" \
  -d '{"geom": "POINT(-0.11944 51.50339)", "value": 10.5}'
```

Response:
```json
{
  "id": 1,
  "created_at": "2026-02-03T21:21:55.391439Z",
  "geom": "POINT (-0.11944 51.50339)",
  "value": 10.5
}
```

### Get all points
```bash
curl -X 'GET' \
  'http://localhost:8000/api/points' \
  -H 'accept: application/json'
```

Response:
```json
[
  {
    "id": 1,
    "created_at": "2026-02-03T21:21:55.391439Z",
    "geom": "POINT (-0.11944 51.50339)",
    "value": 10.5
  }
]
```

### Get points within a bounding box (bbox)
```bash
curl -X 'GET' \
  'http://localhost:8000/api/points/bbox?min_lat=-90&max_lat=90&min_lon=-180&max_lon=180' \
  -H 'accept: application/json'
```

Response:
```json
[
  {
    "id": 1,
    "created_at": "2026-02-03T21:21:55.391439Z",
    "geom": "POINT (-0.11944 51.50339)",
    "value": 10.5
  }
]
```

## API Documentation

Once running, interactive API docs are available at:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Key Implementation Details

### Dual Database Support

The application automatically selects the database backend based on the `ENVIRONMENT` setting:

- `development`: Uses SpatiaLite (SQLite + spatial extension)
- `production`: Uses PostGIS (PostgreSQL + spatial extension)

This is handled in `app/db.py` which loads the appropriate extension on connection.

### Geometry Handling

- **Input:** WKT strings (e.g., `"POINT(-0.11944 51.50339)"`)
- **Storage:** PostGIS/SpatiaLite geometry type via GeoAlchemy2
- **Output:** WKT strings via Pydantic field validator

### Pydantic + GeoAlchemy2 Integration

The `ExamplePointModel` schema uses a field validator to convert `WKBElement` objects to WKT strings for JSON serialisation:
```python
@field_validator("geom", mode="before")
@classmethod
def convert_wkb_to_wkt(cls, v):
    if isinstance(v, WKBElement):
        return to_shape(v).wkt
    return v
```

### Alembic Configuration

The `alembic/env.py` loads environment variables from `.env` and automatically configures the correct database connection:

- In development: Creates/migrates the SpatiaLite database file
- In production: Connects to the PostGIS container

## Environment Variables

Configure via `.env` file (copy from `.env.example`):

| Variable            | Default       | Description                                |
| ------------------- | ------------- | ------------------------------------------ |
| `ENVIRONMENT`       | `development` | `development` or `production`              |
| `SPATIALITE_PATH`   | `./geo.db`    | Path to SpatiaLite database (dev only)     |
| `POSTGRES_USER`     | `postgres`    | PostgreSQL username (production only)      |
| `POSTGRES_PASSWORD` | `postgres`    | PostgreSQL password (production only)      |
| `POSTGRES_HOST`     | `localhost`   | PostgreSQL hostname (production only)      |
| `POSTGRES_PORT`     | `5432`        | PostgreSQL port (production only)          |
| `POSTGRES_DB`       | `postgres`    | PostgreSQL database name (production only) |

## Licence

MIT
