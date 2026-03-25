## 1. Dependencies

- [ ] 1.1 Add `passlib[argon2]` to `pyproject.toml` dependencies and run `uv lock` to update the lockfile

## 2. Password Hashing Utility

- [ ] 2.1 Create `src/api/shared/security/__init__.py` (empty)
- [ ] 2.2 Create `src/api/shared/security/passwords.py` with `hash_password(plain: str) -> str` and `verify_password(plain: str, hashed: str) -> bool` using `passlib.context.CryptContext` configured for Argon2id

## 3. Unit Tests for the Utility

- [ ] 3.1 Create `tests/unit_tests/test_api/test_shared/test_security/test_passwords.py`
- [ ] 3.2 Add test: `hash_password` returns a string starting with `$argon2id$`
- [ ] 3.3 Add test: two calls to `hash_password` with the same input produce different hashes (unique salts)
- [ ] 3.4 Add test: `verify_password` returns `True` when plaintext matches the hash
- [ ] 3.5 Add test: `verify_password` returns `False` when plaintext does not match the hash

## 4. Database Migration

- [ ] 4.1 Generate a new Alembic revision: `uv run alembic -n main revision --autogenerate -m "drop_unique_constraint_on_password_hash"`
- [ ] 4.2 Edit the generated migration to explicitly drop the unique constraint on `auth.user.password_hash` in `upgrade()` and re-add it in `downgrade()`

## 5. Repository Integration

- [ ] 5.1 Update `UsersRepository.create()` to call `hash_password(body.password)` instead of the placeholder
- [ ] 5.2 Update `UsersRepository.update()` to call `hash_password(body.password)` instead of the placeholder
- [ ] 5.3 Remove the TODO comments that referenced issue #17

## 6. Acceptance Tests

- [ ] 6.1 Update `tests/acceptance_tests/functional/test_api/test_auth/test_users/test_create.py` to assert `row["password_hash"].startswith("$argon2id$")`
- [ ] 6.2 Update `tests/acceptance_tests/functional/test_api/test_auth/test_users/test_update.py` to assert `row["password_hash"].startswith("$argon2id$")`
- [ ] 6.3 Fix the seed row in `test_update.py` — the hardcoded `password_hash = 'xyz'` will violate nothing functionally, but update it to a realistic placeholder or a pre-hashed value for clarity

## 7. Verification

- [ ] 7.1 Run unit tests: `dagger call -s test-unit --pytest-quiet`
- [ ] 7.2 Run integration tests: `dagger call -s test-integration --pytest-quiet`
- [ ] 7.3 Run acceptance tests: `dagger call -s test-acceptance --pytest-quiet`
- [ ] 7.4 Run formatting and linting: `uv run ruff format -s . && uv run ruff check -s .`
