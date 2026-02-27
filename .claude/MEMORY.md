# Project Memory

## Package management

- Always use `uv sync --locked` — never plain `uv sync`. The project uses Dependabot to update `uv.lock` directly; running without `--locked` could overwrite locked dependency versions with ranges from `pyproject.toml`.
- When adding a new dependency: run `uv add [--group dev] <package>` (updates both `pyproject.toml` and `uv.lock` atomically), then verify the environment with `uv sync --locked`.
- Alternatively: edit `pyproject.toml` manually → `uv lock` to update the lock file → `uv sync --locked` to install.
