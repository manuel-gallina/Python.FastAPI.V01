## Why

There is currently no visibility into test coverage within the CI pipeline. Adding automated coverage reporting on pull requests enables early detection of untested code paths without blocking merges, serving as an audit trail for coverage health over time.

## What Changes

- Run `pytest` with coverage collection enabled in the CI pipeline.
- Generate a coverage report after tests complete.
- Post a PR comment (created or updated on each run) containing:
  - Overall coverage percentage.
  - A list of modules with coverage below 100%, including their individual percentages.
- The coverage step is non-blocking: PR merges are not gated on coverage thresholds.

## Capabilities

### New Capabilities

- `ci-coverage-report`: Collect test coverage during CI runs and post a summary comment on open pull requests.

### Modified Capabilities

_(none)_

## Impact

- **CI pipeline** (`ci/` or Dagger pipeline): new step to run tests with coverage and publish results.
- **Dependencies**: `pytest-cov` added to dev/test dependencies.
- **GitHub**: requires a GitHub token with `pull-requests: write` permission to post PR comments.
- **No application code changes** — purely CI/tooling concern.
