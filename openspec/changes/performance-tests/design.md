## Context

The project has three acceptance test levels (unit, integration, acceptance) run via Dagger. The `test_acceptance` Dagger function already creates a full live environment: a PostgreSQL service container, an API service container, and a test runner container that applies migrations and runs pytest. All environment wiring (service bindings, env vars) is inlined in `test_acceptance`.

We need to extend the test infrastructure in two ways:
1. **In-process benchmarks** (`pytest-benchmark`) within the pytest acceptance suite
2. **Load comparison** (`locust`) as a separate Dagger function that spins up two live API environments (current branch vs `main`) and compares results

## Goals / Non-Goals

**Goals:**
- Separate `tests/acceptance_tests/` into `functional/` and `non-functional/` subdirectories
- Add `pytest-benchmark` non-functional tests that run against a live API
- Add a `test_performance` Dagger function that runs locust against two environments in parallel and outputs a comparative report
- Extract a reusable `_live_env` helper from `test_acceptance` to avoid duplicating service-wiring logic

**Non-Goals:**
- Automated performance regression gating (thresholds that fail CI) — out of scope for this change
- Distributed locust runs or locust UI — headless mode only
- Benchmarking unit or integration test layers

## Decisions

### 1. Test directory restructuring

Reorganize `tests/acceptance_tests/` as follows:

```
tests/acceptance_tests/
  conftest.py                  (shared fixtures, unchanged)
  functional/
    __init__.py
    test_api/                  (existing test modules moved here)
  non-functional/
    __init__.py
    test_api/
      test_benchmarks.py       (pytest-benchmark tests)
    locustfiles/
      auth.py                  (locust scenarios)
```

**Rationale**: Keeps both categories under a single acceptance umbrella, avoids new top-level test dirs, and mirrors the existing `test_api/` hierarchy.

### 2. pytest-benchmark scope

`pytest-benchmark` tests live in `tests/acceptance_tests/non_functional/test_api/` and run against a live API (same `http_client` fixture from `conftest.py`). They use `benchmark.pedantic()` to measure individual endpoint response times.

The `test_acceptance` Dagger function runs both `functional/` and `non_functional/` pytest subtrees (locustfiles are excluded automatically as they contain no `test_*` functions).

**Rationale**: pytest-benchmark integrates naturally with pytest fixtures; no separate runner is needed.

### 3. `main` branch image source for comparison

The locust comparison uses the **published `latest` Docker image** (`ghcr.io/manuel-gallina/python-fastapi-v01:latest`) as the baseline. The current branch is built from source using the existing `build_env`.

**Alternatives considered**:
- *Build from git ref inside Dagger*: more complex, requires git history to be available inside the pipeline; rejected.
- *Accept an explicit image tag parameter*: keeps the function flexible for arbitrary comparisons; adopted as an optional override parameter so callers can pin a specific tag.

### 4. Reusable live environment helper

Extract `_live_environment` as a private helper method on `PythonFastapiV01`:

```python
def _live_environment(self, source: dagger.Directory) -> tuple[dagger.Service, dagger.Service]:
    """Returns (main_db_service, api_service) for a given source directory."""
```

`test_acceptance` and `test_performance` both call this. The `test_performance` function calls it twice: once with the current source, once with a container built from the `latest` image.

### 5. Locust execution and comparison output

- Locust runs in **headless mode** (`--headless`) with `--json` stats output
- Both runs execute the same locust scenario file for the same duration and user count
- The Dagger function collects both JSON outputs and emits a human-readable comparison summary (p50, p95, p99 latencies and RPS for each environment)
- No hard failure threshold — the output is informational

**Rationale**: Keeps the first iteration simple. Thresholds can be added in a follow-up.

### 6. Locust scenario location

Locust scenario files live in `tests/acceptance_tests/non_functional/locustfiles/`. The `test_performance` Dagger function mounts this directory into the locust runner container.

## Risks / Trade-offs

- **`latest` image lag**: If `main` hasn't been published recently, the baseline may be stale. → Mitigation: the optional `baseline_image` parameter lets callers override the tag; document this in the function docstring.
- **Flaky benchmark results in Dagger**: Containerized environments have variable resource availability; benchmark numbers may differ across runs. → Mitigation: use a fixed locust duration and enough iterations to smooth noise; document that results are indicative, not authoritative.
- **Test suite path changes**: Moving existing functional tests into `functional/` requires updating any path references in Dagger functions and pytest config. → Mitigation: covered explicitly in tasks.

## Open Questions

- Should `test` (the aggregate function) include `test_performance`, or should it remain opt-in only? Leaning toward **opt-in** (not included in `test`) since it requires publishing to have a meaningful baseline.
- Default locust scenario parameters (users, spawn rate, run time): to be decided during implementation based on what produces stable results.
