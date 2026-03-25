## Why

The acceptance test suite currently covers only functional behavior. Adding performance tests will validate that the API meets non-functional requirements (latency, throughput) and catch regressions before they reach production. Comparing the current `main` branch against the branch under development allows detecting performance regressions as part of the development workflow.

## What Changes

- Restructure `tests/acceptance_tests/` into `functional/` and `non-functional/` subdirectories
- Integrate `pytest-benchmark` for micro-level performance assertions within the existing pytest pipeline
- Add `locust` load test scenarios as a dedicated Dagger function that:
  - Reuses the acceptance test live environment setup (API + database containers)
  - Spins up two environments: one from the `main` branch image and one from the current branch image
  - Runs the same locust scenario against both and produces a comparative report
- Add `pytest-benchmark` and `locust` as dev dependencies

## Capabilities

### New Capabilities

- `performance-tests`: Performance test infrastructure covering both in-process benchmarks via pytest-benchmark and comparative load/stress testing via a dedicated Dagger function that benchmarks the current branch against `main`

### Modified Capabilities

_(none — no existing spec-level behavior changes)_

## Impact

- **Test directory**: `tests/acceptance_tests/` reorganized into `functional/` and `non-functional/` subdirectories
- **Dependencies**: `pytest-benchmark`, `locust` added to dev dependencies
- **Dagger pipeline**: new `test-performance` Dagger function added, reusing environment setup from `test-acceptance`, running two parallel live environments for comparison
- **CI configuration**: pipeline extended to include the locust comparison step
