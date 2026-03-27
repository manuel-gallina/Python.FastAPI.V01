# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) — package manager
- [Dagger CLI](https://docs.dagger.io/install) — CI pipeline runner

## Architecture

### Application entry point

`src/main.py` creates the FastAPI app, wires up the lifespan (database engine init/disposal), and includes the main
router from `src/api/routes.py`. All routes are prefixed with `/api`.

### Feature module structure

Each feature module under `src/api/` follows this layout:

- `routes.py` — FastAPI `APIRouter`, injecting dependencies via `Depends`
- `repositories.py` — static async methods decorated with `Depends` for DB access; receive `AsyncEngine` via DI
- `models.py` — Pydantic models mapping DB rows (extend `BaseDbModel` from `src/api/shared/models.py`)
- `schemas.py` — Request/response schemas (extend `BaseSchema` from `src/api/shared/schemas/base.py`)

### Shared foundations

- **`BaseDbModel`** (`src/api/shared/models.py`): `ConfigDict(from_attributes=True)` — use `model_validate()` on
  SQLAlchemy row results.
- **`BaseSchema`** (`src/api/shared/schemas/base.py`): camelCase alias generator, `serialize_by_alias=True` — all API
  schemas serialize to camelCase JSON.
- **`ObjectResponseSchema[T]` / `ListResponseSchema[T]`** (`src/api/shared/schemas/responses.py`): standard envelope
  wrappers for single-object and list responses.
- **Database engine**: created in lifespan, stored on `app.state.main_async_db_engine`, retrieved in routes via
  `get_main_async_db_engine` dependency (`src/api/shared/system/databases.py`).
- **Password hashing** (`src/api/shared/security/passwords.py`): `hash_password(plain) -> str` and
  `verify_password(plain, hashed) -> bool` using `passlib.context.CryptContext` with Argon2id. Always use these
  utilities — never store plaintext passwords or roll custom hashing.

### Settings

Settings are loaded in this priority order (highest to lowest): init args → environment variables → `.env` file → file
secrets → `pyproject.toml`. Defined in `src/api/shared/system/settings.py` using `pydantic-settings`. Use `__` as the
nested delimiter for env vars (e.g. `DATABASE__MAIN_CONNECTION__HOST`). Retrieved via a cached `get_settings()`
function.

### Database

PostgreSQL with `asyncpg` async driver via SQLAlchemy `AsyncEngine`. Alembic handles schema migrations, configured in
`alembic.ini` with the named configuration `main` (migrations in `alembic/main/`). Repositories open short-lived
`AsyncSession` instances per query rather than a shared session.

### Tests

Three test levels with different fixture setups:

- **Unit** (`tests/unit_tests/`): No external services.
- **Integration** (`tests/integration_tests/`): Uses `asgi_lifespan.LifespanManager` + `httpx.ASGITransport` to run the
  full app in-process with faked DB env vars (connection is configured but expected to be mocked per test).
- **Acceptance** (`tests/acceptance_tests/`): Connects to a real running API and database. The `clean_main_db` pytest
  fixture (autouse) truncates the `auth` schema tables before tests marked with `@pytest.mark.clean_main_db`. Base URL
  is configurable via `TEST_API_BASE_URL` env var (default: `http://localhost:9101`).

Pytest is configured with `asyncio_mode = "auto"` — all async test functions run automatically without explicit markers.

#### Integration test mocking

FastAPI resolves **all** declared route dependencies before entering the handler, even if the handler would
short-circuit early (e.g. raise 404). When using `app.dependency_overrides`, mock every dependency that touches the DB —
including shared ones (e.g. `UsersRepository.get_by_id`) that appear both directly in the route and inside another
dependency.

#### Acceptance test DB verification

Use `AsyncSession` to query the DB directly in acceptance tests:

```python
async with AsyncSession(main_async_db_engine) as session:
    result = await session.execute(
        text("select * from auth.user where id = :id"), {"id": user_id}
    )
    row = result.mappings().one_or_none()
```

### CI Pipeline (Dagger)

The Dagger pipeline is defined in `.dagger/src/ci_pipeline/main.py` as the `PythonFastapiV01` object type. Utility
helpers live under `.dagger/src/ci_pipeline/utils/`. The pipeline follows the pattern: Dagger function runs tests →
returns a formatted string → GitHub Actions captures the output and optionally posts it as a sticky PR comment via
`marocchino/sticky-pull-request-comment@v2`.

Existing Dagger functions and their purpose:

- `test-unit` / `test-integration` / `test-acceptance` / `test` — run pytest at each level
- `test-coverage` — runs unit + integration tests with `--cov=src --cov-branch --cov-report=term-missing`, returns a
  formatted coverage report (terminal or markdown); markdown report is posted as a sticky PR comment by the `coverage`
  job in `tests.yml`
- `test-performance` — comparative load test against a baseline Docker image; results posted as sticky PR comment
- `export-openapi-schema` — exports the OpenAPI spec to `docs/openapi.yaml`
- `publish-docker-image` — builds and pushes the Docker image to ghcr.io
- `lint` — runs `ruff check`

When adding new Dagger functions that return formatted output for PR comments, follow the `test-performance` /
`test-coverage` pattern: accept an `output_format` parameter using a `StrEnum`, implement both terminal and markdown
formatters, and add a corresponding job to `tests.yml` with `pull-requests: write` permission.

#### Ruff rules to watch in Dagger/utils code

- **PLR2004** — avoid bare numeric constants in comparisons; extract them as module-level constants
- **PLW3301** — flatten nested `max`/`min` calls: use `max(x, *generator)` instead of `max(x, max(generator))`
- **PLR0913** — functions are limited to 5 arguments; use a dataclass parameter when more are needed

## Docs

The API OpenAPI spec is available in the `docs/openapi.yaml` file.
Diagrams are available in the `docs/diagrams/` directory, created with [plantuml](https://plantuml.com/).