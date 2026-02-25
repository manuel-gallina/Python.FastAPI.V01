![Banner](./docs/logo/logo.svg)

# FastAPI Template V1

Template project for FastAPI applications.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Dagger CLI](https://docs.dagger.io/install)

## Setup

Install dependencies:

```sh
uv sync --group dev
```

Copy `.env` and adjust values for your local environment:

```sh
cp .env .env.local
```

The app loads settings from both `.env` and `pyproject.toml` via `pydantic-settings`,
with environment variables taking priority.

## Configuration

Settings are defined in `src/api/shared/system/settings.py` and loaded from:
1. Environment variables
2. `.env` file
3. `pyproject.toml` (for `[project]` metadata)

Nested settings use `__` as the delimiter.

| Variable | Default | Description |
|---|---|---|
| `DATABASE__MAIN_CONNECTION__DBMS` | — | Database system (e.g. `postgresql`) |
| `DATABASE__MAIN_CONNECTION__DRIVER` | — | Async driver (e.g. `asyncpg`) |
| `DATABASE__MAIN_CONNECTION__HOST` | `localhost` | Database host |
| `DATABASE__MAIN_CONNECTION__PORT` | `5432` | Database port |
| `DATABASE__MAIN_CONNECTION__USER` | — | Database user |
| `DATABASE__MAIN_CONNECTION__PASSWORD` | — | Database password |
| `DATABASE__MAIN_CONNECTION__NAME` | — | Database name |
| `TIMEZONE` | `Europe/Rome` | Application timezone |

## Running the app

```sh
fastapi dev src/main.py
```

## Database

Alembic is used for schema migrations, scoped to local development and test setup. Production schema management is intentionally out of scope.

Apply migrations:

```sh
alembic --name main upgrade head
```

The database schema is documented in [`docs/pages/database.md`](./docs/pages/database.md).

## Tests

Tests are organized in three levels under `tests/`:

| Level | Directory | External services |
|---|---|---|
| Unit | `tests/unit_tests/` | All mocked |
| Integration | `tests/integration_tests/` | Databases and external services mocked |
| Acceptance | `tests/acceptance_tests/` | Real PostgreSQL instance required |

Run all tests via Dagger (recommended):

```sh
dagger call test
```

Or run individual levels locally with pytest (unit and integration only):

```sh
pytest tests/unit_tests
pytest tests/integration_tests
```

For acceptance tests locally, a running PostgreSQL instance must be configured via `.env`. Run migrations before the test suite:

```sh
alembic --name main upgrade head
pytest tests/acceptance_tests
```

## Pipeline

The CI pipeline is implemented as a [Dagger](https://docs.dagger.io/) module located in `.dagger/`.

### Available Dagger functions

| Function | Description |
|---|---|
| `dagger call test` | Run all test levels |
| `dagger call test-unit` | Run unit tests only |
| `dagger call test-integration` | Run integration tests only |
| `dagger call test-acceptance` | Run acceptance tests (spins up PostgreSQL service) |
| `dagger call lint` | Run `ruff check` |
| `dagger call build-env` | Build the application container |
| `dagger call export-openapi-schema -o .` | Export OpenAPI schema to `docs/openapi.yaml` |
| `dagger call publish-docker-image --token <secret>` | Publish image to `ghcr.io` |

Publishing example using 1Password:

```sh
dagger call publish-docker-image --token cmd://"op read op://employee/github/dagger/password"
```

### GitHub Actions workflows

| Workflow | Trigger | Description |
|---|---|---|
| `tests.yml` | PR to `main` | Runs `dagger call test` |
| `style.yml` | PR to `main` | Runs `dagger call lint`, posts results as a PR comment |

## Code style

Linting and formatting via [ruff](https://docs.astral.sh/ruff/), configured in `ruff.toml` (Google docstring convention).
The `tests/` directory has its own `ruff.toml` with relaxed rules.

```sh
# Check
ruff check .

# Format
ruff format .
```

## Docs

- [Docs index](./docs/index.md)
- [OpenAPI schema](./docs/openapi.yaml)

Diagrams are authored in PlantUML under `docs/diagrams/src/` and rendered to `docs/diagrams/out/`.
Use the [PlantUML VSCode extension](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) to edit and preview them.
