## 1. Dependencies and configuration

- [x] 1.1 Add `pytest-benchmark` and `locust` to dev dependencies in `pyproject.toml` and update `uv.lock`

## 2. Test directory restructuring

- [x] 2.1 Create `tests/acceptance_tests/functional/` and `tests/acceptance_tests/non_functional/` directories with
  `__init__.py` files
- [x] 2.2 Move all existing test modules from `tests/acceptance_tests/test_api/` into
  `tests/acceptance_tests/functional/test_api/`
- [x] 2.3 Remove the now-empty `tests/acceptance_tests/test_api/` directory

## 3. pytest-benchmark tests

- [x] 3.1 Create `tests/acceptance_tests/non_functional/test_api/` with `__init__.py`
- [x] 3.2 Write benchmark test cases in `tests/acceptance_tests/non_functional/test_api/` using `benchmark.pedantic()`
  against at least one endpoint

## 4. Locust scenarios

- [x] 4.1 Create `tests/acceptance_tests/non_functional/locustfiles/` directory
- [x] 4.2 Implement at least one locust scenario file with an `HttpUser` subclass and `@task`-decorated methods
  targeting auth API endpoints

## 5. Dagger pipeline refactoring

- [x] 5.1 Extract `_live_environment(source)` private helper method from `test_acceptance` that returns
  `(db_service, api_service)` for a given source directory
- [x] 5.2 Refactor `test_acceptance` to use `_live_environment` instead of inlining service setup
- [x] 5.3 Update the pytest path in `test_acceptance` to run both `tests/acceptance_tests/functional/` and
  `tests/acceptance_tests/non_functional/` (excluding `locustfiles/`)

## 6. test_performance Dagger function

- [x] 6.1 Implement `test_performance` Dagger function that accepts an optional `baseline_image` parameter (default:
  `ghcr.io/manuel-gallina/python-fastapi-v01:latest`)
- [x] 6.2 Build the current-branch live environment using `_live_environment(source)`
- [x] 6.3 Build the baseline live environment from the baseline image using `_live_environment` (adapted for a pre-built
  container)
- [x] 6.4 Run locust headlessly against the current-branch environment and capture JSON stats output
- [x] 6.5 Run locust headlessly against the baseline environment and capture JSON stats output
- [x] 6.6 Parse both JSON outputs and return a human-readable comparison of p50, p95, p99 latency and RPS for both
  environments

## 7. Validation

- [x] 7.1 Run `dagger call -s test` and confirm all functional and non-functional pytest tests pass
- [x] 7.2 Run `dagger call test-performance` and confirm the comparative output contains latency metrics for both
  environments
- [x] 7.3 Run `uv run ruff format -s .` and `uv run ruff check -s .` and fix any linting issues
