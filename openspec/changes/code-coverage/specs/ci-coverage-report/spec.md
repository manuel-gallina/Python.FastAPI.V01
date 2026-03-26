## ADDED Requirements

### Requirement: Dagger function collects coverage for unit and integration tests
The pipeline SHALL expose a `test-coverage` Dagger function that runs unit and integration tests with coverage collection enabled and returns a markdown-formatted coverage report string.

#### Scenario: Function runs and returns markdown report
- **WHEN** `dagger call test-coverage` is executed against a valid source directory
- **THEN** the function returns a non-empty markdown string containing the overall coverage percentage and a per-module breakdown

#### Scenario: Function accepts the same optional arguments as existing test functions
- **WHEN** `test-coverage` is called with `--pytest-quiet` or `--pytest-randomly-seed`
- **THEN** those flags are forwarded to pytest as in the existing `test-unit` and `test-integration` functions

### Requirement: Coverage report includes overall percentage and low-coverage modules
The coverage report SHALL contain:
- The overall (total) coverage percentage.
- A table of all modules whose individual coverage is below 100%, with columns: Module, Stmts, Miss, Branch, BrPart, Cover.
- Modules SHALL be sorted by ascending coverage percentage (least covered first).
- The report SHALL be produced by both the terminal and markdown formatters with the same column set.

#### Scenario: All modules at 100% coverage
- **WHEN** every module has 100% coverage
- **THEN** the report states overall coverage is 100% and the low-coverage module table is empty (or omitted)

#### Scenario: Some modules below 100% coverage
- **WHEN** one or more modules have coverage below 100%
- **THEN** the report lists those modules sorted by ascending coverage %, with Stmts, Miss, Branch, BrPart, and Cover columns visible

#### Scenario: Multiple modules with the same coverage percentage
- **WHEN** two or more modules share the same coverage percentage
- **THEN** their relative order is stable (consistent across runs)

### Requirement: GitHub Actions posts coverage as a non-blocking sticky PR comment
The `tests.yml` workflow SHALL include a `coverage` job that runs on pull requests targeting `main`, calls `dagger call test-coverage --output-format=markdown`, and posts the output as a sticky PR comment. The job SHALL NOT gate PR merges (it is informational only).

#### Scenario: Coverage job runs on a new pull request
- **WHEN** a pull request is opened or updated against `main`
- **THEN** the `coverage` job executes and a PR comment is created or updated with the coverage report

#### Scenario: Coverage job failure does not block merge
- **WHEN** the `coverage` job fails (e.g. due to a transient error)
- **THEN** the pull request can still be merged (the job is not a required status check)

#### Scenario: Comment is updated on subsequent pushes
- **WHEN** a new commit is pushed to an open pull request
- **THEN** the existing coverage comment is updated in place (not duplicated)

### Requirement: pytest-cov is available in the development environment
The `dev` dependency group in `pyproject.toml` SHALL include `pytest-cov` so coverage collection works inside the Dagger container built with `development=True`.

#### Scenario: Coverage flags accepted by pytest inside the container
- **WHEN** the Dagger test container is built with `development=True` and pytest is invoked with `--cov`
- **THEN** pytest runs successfully with coverage collection enabled and no missing-plugin error is raised
