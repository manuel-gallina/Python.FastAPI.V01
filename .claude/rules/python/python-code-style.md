---
paths:
  - "**/*.py"
---

# Python code style

1. Python code style is enforced via Ruff.
2. Run `ruff format -q .` to auto-format code.
3. Run `ruff check -q .` to check for linting errors.
4. Ruff is configured in `ruff.toml` files.
5. The `tests/` directory has its own `ruff.toml` with relaxed rules.