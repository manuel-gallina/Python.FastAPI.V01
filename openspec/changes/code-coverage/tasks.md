## 1. Dependencies

- [x] 1.1 Add `pytest-cov` to the `dev` dependency group in `pyproject.toml` and run `uv lock` to update the lockfile

## 2. Dagger pipeline

- [x] 2.1 Add a `test_coverage` function to `PythonFastapiV01` in `.dagger/src/ci_pipeline/main.py` that runs unit and integration tests with `--cov=src --cov-report=term-missing` and returns the raw pytest output
- [x] 2.2 Add a `CoverageFormats` enum (or reuse a pattern from the existing `OutputFormats`) and a helper that transforms the raw `pytest --cov` terminal output into a markdown string with overall coverage percentage and a table of modules below 100%
- [x] 2.3 Wire the markdown formatter into `test_coverage` so the function returns the formatted markdown report

## 3. GitHub Actions workflow

- [x] 3.1 Add a `coverage` job to `.github/workflows/tests.yml` that checks out code, installs the Dagger CLI, and runs `dagger call test-coverage --output-format=markdown >> pr_comment.md`
- [x] 3.2 Add the `pull-requests: write` permission to the `coverage` job
- [x] 3.3 Add the `marocchino/sticky-pull-request-comment@v2` step to the `coverage` job with `header: pytest-coverage-result` and `path: pr_comment.md`

## 4. Verification (initial)

- [x] 4.1 Run `dagger call test-coverage` locally and confirm the output is valid markdown containing overall coverage and a per-module breakdown
- [x] 4.2 Push to the feature branch and confirm the `coverage` job appears on the PR, posts a comment, and does not block merge

## 5. Enhanced report: branch coverage + full columns + sorted output

- [x] 5.1 Add `--cov-branch` to the pytest invocation in `test_coverage` in `.dagger/src/ci_pipeline/main.py`
- [x] 5.2 Update `_parse_coverage_output` in `coverage.py` to capture all columns: name, stmts, miss, branch, brpart, cover_pct — returning a structured list instead of `list[tuple[str, str]]`
- [x] 5.3 Update `_format_terminal` to display all columns (Module, Stmts, Miss, Branch, BrPart, Cover) sorted by ascending cover_pct
- [x] 5.4 Update `_format_markdown` to display all columns (Module, Stmts, Miss, Branch, BrPart, Cover) sorted by ascending cover_pct
- [x] 5.5 Run `dagger call test-coverage --output-format=markdown` locally and confirm the output contains all columns, branch data, and is sorted ascending by coverage
