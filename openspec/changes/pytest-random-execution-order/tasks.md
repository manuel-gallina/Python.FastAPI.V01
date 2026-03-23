## 1. Dependency

- [x] 1.1 Add `pytest-randomly` as a dev dependency in `pyproject.toml`
- [x] 1.2 Update `uv.lock` by running `uv lock`

## 2. Verification

- [x] 2.1 Run `dagger call -s test` and confirm the seed line appears in pytest output
- [x] 2.2 Verify that a run with `--randomly-seed=last` reproduces the previous order
