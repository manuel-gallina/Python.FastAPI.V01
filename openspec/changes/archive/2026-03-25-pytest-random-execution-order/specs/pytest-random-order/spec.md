## ADDED Requirements

### Requirement: Tests execute in random order by default
The test suite SHALL execute test cases in a randomised order on every run using the `pytest-randomly` plugin. The random seed SHALL be printed at the start of each test session so that any failure can be reproduced exactly.

#### Scenario: Default run uses randomised order
- **WHEN** pytest is invoked without any seed-related flags
- **THEN** tests are collected and executed in a random order
- **THEN** the seed used for that run is printed in the pytest output header

#### Scenario: Reproducing a specific run order
- **WHEN** pytest is invoked with `--randomly-seed=<seed>` using the seed from a previous run
- **THEN** tests execute in exactly the same order as the original run

#### Scenario: Seed shorthand for last run
- **WHEN** pytest is invoked with `--randomly-seed=last`
- **THEN** tests execute in the same order as the most recent run on that machine

### Requirement: pytest-randomly is available as a dev dependency
The `pytest-randomly` package SHALL be declared as a development dependency in `pyproject.toml` so it is installed in all development and CI environments.

#### Scenario: Dependency present after install
- **WHEN** the project dependencies are installed with `uv sync`
- **THEN** `pytest-randomly` is available in the environment
- **THEN** running `pytest --co -q` shows the randomly seed line in the output
