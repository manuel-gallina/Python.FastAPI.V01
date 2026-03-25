## ADDED Requirements

### Requirement: Acceptance tests are separated into functional and non-functional categories
The project's acceptance test suite SHALL be organised into two mutually exclusive subdirectories under `tests/acceptance_tests/`: `functional/` for behaviour-driven tests and `non_functional/` for performance-driven tests. All existing acceptance test modules SHALL be moved into `functional/` without modification to their content.

#### Scenario: Existing tests run under functional subdirectory
- **WHEN** the `test_acceptance` Dagger function is executed
- **THEN** all previously existing acceptance test cases are discovered and executed from `tests/acceptance_tests/functional/`

#### Scenario: Non-functional directory exists alongside functional
- **WHEN** the repository is checked out
- **THEN** both `tests/acceptance_tests/functional/` and `tests/acceptance_tests/non_functional/` directories exist

---

### Requirement: In-process benchmark tests use pytest-benchmark
The system SHALL provide pytest-based benchmark tests in `tests/acceptance_tests/non_functional/` that use `pytest-benchmark` to measure endpoint response times against a live API. These tests SHALL run as part of the `test_acceptance` Dagger function.

#### Scenario: Benchmark test measures endpoint latency
- **WHEN** a benchmark test calls an API endpoint via `benchmark.pedantic()`
- **THEN** pytest-benchmark records timing statistics (min, max, mean, stddev) and includes them in the test output

#### Scenario: Benchmark tests are included in test_acceptance
- **WHEN** the `test_acceptance` Dagger function is executed
- **THEN** both `functional/` and `non_functional/` pytest subtrees are discovered and run

---

### Requirement: Locust scenarios are defined for API load testing
The system SHALL provide locust scenario files in `tests/acceptance_tests/non_functional/locustfiles/` that describe user behaviour tasks exercising the API. Scenario files SHALL be valid locust `HttpUser` subclasses usable in headless mode.

#### Scenario: Locust scenario file targets auth endpoints
- **WHEN** locust loads a scenario file from `locustfiles/`
- **THEN** it finds at least one `HttpUser` subclass with at least one `@task`-decorated method targeting an API endpoint

---

### Requirement: A dedicated Dagger function runs comparative locust load tests
The system SHALL provide a `test_performance` Dagger function that:
- Builds a live environment from the current branch source (API + database services)
- Pulls the baseline environment from the published `latest` Docker image (or a caller-supplied image tag)
- Runs the same locust scenario against both environments sequentially in headless mode
- Outputs a human-readable comparison of p50, p95, p99 latency and requests-per-second for both environments

#### Scenario: Performance test runs against two environments
- **WHEN** `test_performance` is called without an explicit baseline image tag
- **THEN** it spins up two API environments: one built from source and one from `ghcr.io/manuel-gallina/python-fastapi-v01:latest`
- **AND** locust runs the same scenario against both

#### Scenario: Caller supplies a custom baseline image
- **WHEN** `test_performance` is called with an explicit `baseline_image` parameter
- **THEN** the baseline environment uses that image instead of `latest`

#### Scenario: Output contains comparative latency metrics
- **WHEN** `test_performance` completes successfully
- **THEN** the returned string contains p50, p95, and p99 response time values for both the current branch and the baseline
- **AND** the requests-per-second values for both environments are included

---

### Requirement: Live environment setup is extracted into a reusable helper
The Dagger pipeline SHALL expose a private `_live_environment` helper method that creates a `(db_service, api_service)` tuple for a given source directory or container image. Both `test_acceptance` and `test_performance` SHALL use this helper instead of duplicating service-wiring logic.

#### Scenario: test_acceptance uses the shared helper
- **WHEN** `test_acceptance` is executed
- **THEN** it obtains the database and API services via `_live_environment` rather than inlining container setup

#### Scenario: test_performance uses the shared helper twice
- **WHEN** `test_performance` is executed
- **THEN** it calls `_live_environment` once for the current-branch source and once for the baseline image

---

### Requirement: pytest-benchmark and locust are registered as dev dependencies
The project's `pyproject.toml` SHALL list `pytest-benchmark` and `locust` as development dependencies so they are available in the dev virtual environment and inside Dagger build containers when `development=True`.

#### Scenario: Dev install includes performance dependencies
- **WHEN** `uv sync --locked` is run with dev dependencies enabled
- **THEN** both `pytest-benchmark` and `locust` are available in the virtual environment

---

### Requirement: test_performance is not included in the aggregate test function
The aggregate `test` Dagger function SHALL NOT invoke `test_performance`. Performance comparison tests SHALL be opt-in, callable explicitly via `dagger call test-performance`.

#### Scenario: Running aggregate tests skips performance tests
- **WHEN** `dagger call test` is executed
- **THEN** no locust process is started and `test_performance` logic is not executed
