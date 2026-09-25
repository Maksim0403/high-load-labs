# LogiFlow — Backend

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-enabled-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> LogiFlow is a logistics management platform that helps teams track shipments,
> manage warehouses, and automate delivery workflows.

---

## Project Structure

| Directory/File | Description |
| --- | --- |
| `alembic/` | Database migration scripts and configuration |
| `app/` | Core backend application logic |
| `app/api/` | API endpoints and routes (v1) |
| `app/core/` | Configuration, security, and cloud storage logic |
| `app/crud/` | CRUD operations (Direct DB interaction) |
| `app/db/` | Database session and connection management |
| `app/models/` | SQLAlchemy database models |
| `app/schemas/` | Pydantic schemas for data validation |
| `app/services/` | Business logic layer (Service pattern) |
| `app/main.py` | FastAPI application entry point |
| `deployment/` | Docker Compose, Dockerfiles, and deployment configs |
| `tests/` | Comprehensive test suite (Unit and Integration) |

---

## Deployment Guide

### System Requirements

- **Docker:** Engine 20.10+ or Docker Desktop
- **Docker Compose:** v2.0+
- **Resources:**
  - RAM: 2GB (minimum) / 4GB (recommended)
  - CPU: 2 Cores
  - Disk: 5GB free space

### Quick Start with Docker

1. **Clone the repository:**

```bash
git clone https://github.com/practice-team-lymhqo34/backend.git
cd backend
```

1. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env and fill in required secrets
```

1. **Launch the services:**

```bash
docker-compose -f deployment/docker-compose.yml up --build -d
```

1. **Apply database migrations:**

```bash
docker exec -it logiflow_backend alembic upgrade head
```

The API will be available at `http://localhost:8000`.
Documentation: `http://localhost:8000/docs`

---

## Test Credentials

For testing purposes, you can use the following accounts (register them first
via `/api/v1/auth/register` if the database is fresh):

|Role|Email|Password|
|---|---|---|
|**Manager**|`manager@example.com`|`password123`|
|**Driver**|`driver@example.com`|`password123`|
|**Client**|`client@example.com`|`password123`|

---

## Local Development

### Prerequisites

- Python >= 3.13
- PostgreSQL 17
- [uv](https://github.com/astral-sh/uv) (recommended package manager)

### Installation

1. **Create virtual environment and install dependencies:**

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows
uv sync
```

### Running

```bash
# Start development server
uvicorn app.main:app --reload
```

---

## Testing

```bash
# Run all tests
uv run pytest
```
