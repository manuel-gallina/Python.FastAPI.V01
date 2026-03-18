# Tests

1. Tests are implemented using `pytest`.
2. All test cases are located under the `tests/` directory, organized by test level (unit, integration, acceptance).
3. Test files should be named with the `test_*.py` pattern.
4. Test functions should be named with the `test_*` pattern.
5. Test folder structure should mirror the application structure where applicable, to maintain clarity and organization.
6. Only run tests via Dagger, with `dagger call -q test` or the specific test level commands
   (`test-unit`, `test-integration`, `test-acceptance`) to ensure the correct environment and services are available.