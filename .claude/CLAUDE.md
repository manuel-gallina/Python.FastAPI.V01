# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) — package manager
- [Dagger CLI](https://docs.dagger.io/install) — CI pipeline runner

## Setup

```sh
uv sync --group dev
cp .env .env.local  # adjust values for local environment
```

## Common Commands

```sh
# Run the app
fastapi dev src/main.py

# Apply DB migrations
alembic --name main upgrade head

# Lint (check)
ruff check .

# Format
ruff format .
```

> **Always run tests via Dagger** (not `pytest` directly) — it ensures the correct
> environment and services are available.

```sh
# Run unit and integration tests locally (no external services needed)
dagger call test-unit
dagger call test-integration

# Run acceptance tests (spins up PostgreSQL service automatically)
dagger call test-acceptance

# Run all test levels
dagger call test
```

## Dagger CI Pipeline

The pipeline module lives in `.dagger/src/ci_pipeline/main.py`.

| Command | Description |
|---|---|
| `dagger call test` | Run all test levels (unit, integration, acceptance) |
| `dagger call test-unit` | Unit tests only |
| `dagger call test-integration` | Integration tests only |
| `dagger call test-acceptance` | Acceptance tests (spins up PostgreSQL service) |
| `dagger call lint` | Run `ruff check` |
| `dagger call build-env` | Build the application container |
| `dagger call export-openapi-schema -o .` | Export OpenAPI schema to `docs/openapi.yaml` |
| `dagger call publish-docker-image --token <secret>` | Publish image to `ghcr.io` |

## Architecture

### Application entry point

`src/main.py` creates the FastAPI app, wires up the lifespan (database engine init/disposal), and includes the main router from `src/api/routes.py`. All routes are prefixed with `/api` and use `ORJSONResponse` by default.

### Feature module structure

Each feature module under `src/api/` follows this layout:
- `routes.py` — FastAPI `APIRouter`, injecting dependencies via `Depends`
- `repositories.py` — static async methods decorated with `Depends` for DB access; receive `AsyncEngine` via DI
- `models.py` — Pydantic models mapping DB rows (extend `BaseDbModel` from `src/api/shared/models.py`)
- `schemas.py` — Request/response schemas (extend `BaseSchema` from `src/api/shared/schemas/base.py`)

### Shared foundations

- **`BaseDbModel`** (`src/api/shared/models.py`): `ConfigDict(from_attributes=True)` — use `model_validate()` on SQLAlchemy row results.
- **`BaseSchema`** (`src/api/shared/schemas/base.py`): camelCase alias generator, `serialize_by_alias=True` — all API schemas serialize to camelCase JSON.
- **`ObjectResponseSchema[T]` / `ListResponseSchema[T]`** (`src/api/shared/schemas/responses.py`): standard envelope wrappers for single-object and list responses.
- **Database engine**: created in lifespan, stored on `app.state.main_async_db_engine`, retrieved in routes via `get_main_async_db_engine` dependency (`src/api/shared/system/databases.py`).

### Settings

Settings are loaded in this priority order (highest to lowest): init args → environment variables → `.env` file → file secrets → `pyproject.toml`. Defined in `src/api/shared/system/settings.py` using `pydantic-settings`. Use `__` as the nested delimiter for env vars (e.g. `DATABASE__MAIN_CONNECTION__HOST`). Retrieved via a cached `get_settings()` function.

### Database

PostgreSQL with `asyncpg` async driver via SQLAlchemy `AsyncEngine`. Alembic handles schema migrations, configured in `alembic.ini` with the named configuration `main` (migrations in `alembic/main/`). Repositories open short-lived `AsyncSession` instances per query rather than a shared session.

### Tests

Three test levels with different fixture setups:

- **Unit** (`tests/unit_tests/`): No external services.
- **Integration** (`tests/integration_tests/`): Uses `asgi_lifespan.LifespanManager` + `httpx.ASGITransport` to run the full app in-process with faked DB env vars (connection is configured but expected to be mocked per test).
- **Acceptance** (`tests/acceptance_tests/`): Connects to a real running API and database. The `clean_main_db` pytest fixture (autouse) truncates the `auth` schema tables before tests marked with `@pytest.mark.clean_main_db`. Base URL is configurable via `TEST_API_BASE_URL` env var (default: `http://localhost:9101`).

Pytest is configured with `asyncio_mode = "auto"` — all async test functions run automatically without explicit markers.

#### Integration test mocking

FastAPI resolves **all** declared route dependencies before entering the handler, even if the handler would short-circuit early (e.g. raise 404). When using `app.dependency_overrides`, mock every dependency that touches the DB — including shared ones (e.g. `UsersRepository.get_by_id`) that appear both directly in the route and inside another dependency.

#### Acceptance test DB verification

Use `AsyncSession` to query the DB directly in acceptance tests:

```python
async with AsyncSession(main_async_db_engine) as session:
    result = await session.execute(
        text("select * from auth.user where id = :id"), {"id": user_id}
    )
    row = result.mappings().one_or_none()
```

### Git commit messages

Use the format `<tag>: <message>`. Valid tags:

| Tag | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `tests` | Adding or updating tests |
| `docs` | Documentation changes |
| `refactor` | Code restructuring without behaviour change |
| `chore` | Maintenance tasks (deps, config, tooling) |

### Code style

Ruff is used for linting and formatting, configured in `ruff.toml` (Google docstring convention). The `tests/` directory has its own `ruff.toml` with relaxed rules (notably `S101` for `assert` and `D104` for missing package docstrings are ignored).
