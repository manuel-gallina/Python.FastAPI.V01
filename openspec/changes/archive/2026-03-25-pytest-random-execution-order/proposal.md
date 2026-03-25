## Why

Test suites that always run in the same order can mask hidden dependencies between tests — a test may silently rely on state set up by a previous one. Randomising execution order exposes these inter-test dependencies early, before they cause flaky failures in CI or on other machines.

## What Changes

- Add `pytest-randomly` as a development dependency.
- Configure pytest to use `pytest-randomly` for randomised test execution order across all test levels (unit, integration, acceptance).

## Capabilities

### New Capabilities

- `pytest-random-order`: Integration of `pytest-randomly` plugin to randomise test execution order and surface hidden inter-test dependencies.

### Modified Capabilities

<!-- No existing spec-level requirements are changing. -->

## Impact

- `pyproject.toml`: new dev dependency (`pytest-randomly`).
- `uv.lock`: updated lock file.
- All test runs will execute in a randomised order by default; a fixed seed can be passed to reproduce failures.
