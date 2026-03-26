## Context

The project uses Dagger as its CI runner, invoked from GitHub Actions workflows. Tests run at three levels (unit, integration, acceptance) via `dagger call test` (or the individual `test-unit`, `test-integration`, `test-acceptance` functions). The `tests.yml` workflow already follows the pattern of: run a Dagger function → capture output → optionally post a PR comment (as seen in the `performance` job using `marocchino/sticky-pull-request-comment@v2`).

Coverage collection is currently absent from the pipeline. The goal is to collect coverage across all test levels and post a non-blocking PR comment.

## Goals / Non-Goals

**Goals:**
- Add a new `test-coverage` Dagger function that runs all tests with `pytest-cov` and returns a markdown coverage report.
- Add a `coverage` job to `.github/workflows/tests.yml` that calls the Dagger function and posts a sticky PR comment.
- The job is non-blocking (no coverage threshold enforced; PR merge is not gated).

**Non-Goals:**
- Merging coverage into the existing `test` Dagger function (keep them separate to avoid coupling).
- Enforcing a minimum coverage threshold.
- Generating HTML or XML coverage artifacts beyond the PR comment.
- Acceptance test coverage (acceptance tests require a live environment; coverage there is not the goal here).

## Decisions

### Only unit + integration tests for coverage

**Decision**: Collect coverage only for unit and integration tests; exclude acceptance tests.

**Rationale**: Acceptance tests spin up a live API + database service via Dagger, making coverage collection more involved (the code runs inside a separate service container, not the test runner container). Unit and integration tests run in a single container and cover the application source directly. This keeps the implementation simple and consistent.

**Alternative considered**: Run coverage across all three levels. Rejected due to the added complexity of instrumenting a service container.

---

### New `test-coverage` Dagger function returning markdown

**Decision**: Add a dedicated `test_coverage` function to `PythonFastapiV01` that runs both unit and integration tests with `--cov` and `--cov-report=term-missing` and formats output as a markdown comment.

**Rationale**: The performance job already follows this pattern (Dagger function returns markdown → GitHub Action posts it). Reusing the same integration pattern keeps the CI workflow consistent and avoids any GitHub-specific logic inside Dagger.

**Alternative considered**: Run `pytest --cov` directly in the GitHub Actions step. Rejected because it would bypass the Dagger environment and deviate from the project's convention that all test execution goes through Dagger.

---

### `marocchino/sticky-pull-request-comment` for the PR comment

**Decision**: Reuse the same sticky comment action already used by the `performance` job, with a distinct `header` value (`pytest-coverage-result`).

**Rationale**: Already a proven dependency in the repo. The sticky behaviour (create on first run, update on subsequent runs) is exactly what is needed for a per-PR coverage audit.

---

### `pytest-cov` as the coverage backend

**Decision**: Add `pytest-cov` to the `dev` dependency group in `pyproject.toml`.

**Rationale**: `pytest-cov` is the standard pytest plugin; it integrates transparently with the existing pytest invocations. No configuration file changes needed beyond passing `--cov` flags.

---

### Branch coverage enabled via `--cov-branch`

**Decision**: Pass `--cov-branch` to pytest alongside `--cov=src --cov-report=term-missing`.

**Rationale**: `coverage.py` (the backend for `pytest-cov`) supports branch coverage natively — no additional dependency is needed. Enabling it produces two extra columns (`Branch`, `BrPart`) that give a more accurate picture of how well conditional paths are exercised. Without branch coverage, a file with an untested `else` branch would still show 100% line coverage.

**Alternative considered**: Leave branch coverage disabled to keep the output simpler. Rejected because the additional signal is valuable for an audit report and costs nothing.

---

### All numeric columns displayed in both formatters

**Decision**: Both the terminal and markdown formatters render all six columns: Module, Stmts, Miss, Branch, BrPart, Cover.

**Rationale**: The `Missing` column (line numbers and branch arrows) can be arbitrarily long and does not format well in a markdown table or aligned terminal output. The numeric columns provide the full quantitative picture without noise.

---

### Modules sorted by ascending coverage percentage

**Decision**: Rows in the low-coverage table are sorted by `cover_pct` ascending (least covered first).

**Rationale**: The most actionable modules — those needing the most attention — appear at the top. Stable sort preserves the original ordering among modules with identical percentages.

## Risks / Trade-offs

- **Coverage noise from integration tests**: Integration tests mock the database, so coverage numbers reflect mocked paths. This is acceptable for an audit-only report.
- **Sticky comment on force-push**: `marocchino/sticky-pull-request-comment` updates the comment in place, so coverage always reflects the latest push. No stale data risk.
- **CI time**: Running tests twice (once in the `test` job, once in `coverage`) adds wall-clock time. Mitigated by the fact that the `coverage` job runs in parallel with `test` (independent GitHub Actions jobs).
