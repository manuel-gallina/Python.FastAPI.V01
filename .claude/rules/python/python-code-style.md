---
paths:
  - "**/*.py"
---

# Python code style

1. Python code style is enforced via Ruff.
2. Run `uv run ruff format -s .` to auto-format code.
3. Run `uv run ruff check -s .` to check for linting errors.
4. Ruff is configured in `ruff.toml` files.
5. The `tests/` directory has its own `ruff.toml` with relaxed rules.