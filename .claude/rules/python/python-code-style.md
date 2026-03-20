---
paths:
  - "**/*.py"
---

# Python code style

1. Python code style is enforced via Ruff.
2. Run `uv run ruff format -q .` to auto-format code.
3. Run `uv run ruff check -q .` to check for linting errors.
4. Ruff is configured in `ruff.toml` files.
5. The `tests/` directory has its own `ruff.toml` with relaxed rules.