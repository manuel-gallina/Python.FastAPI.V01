## Why

Passwords are currently stored using a trivial placeholder (`placeholder:{email}`) instead of a real cryptographic hash, leaving user credentials unprotected. Implementing proper hashing before any login/authentication feature is built prevents insecure data from ever reaching production.

## What Changes

- Replace the placeholder hashing logic in `UsersRepository.create()` and `UsersRepository.update()` with Argon2id hashing via the `passlib` library.
- Add `passlib[argon2]` as a production dependency.
- Remove the unique constraint on `password_hash` in the database (placeholder values were deterministic per email, but real hashes are not — the column should not be unique).
- Add a new Alembic migration to drop the unique constraint.
- Update acceptance tests to verify the stored hash is a valid Argon2id hash rather than the placeholder format.

## Capabilities

### New Capabilities

- `password-hashing`: Secure storage and verification of user passwords using Argon2id (OWASP-recommended), abstracted behind a reusable hashing service/utility.

### Modified Capabilities

_(none — the public API contract for user create/update endpoints is unchanged)_

## Impact

- **Code**: `src/api/auth/users/repositories.py` (hashing logic), new `src/api/shared/security/passwords.py` (or similar) for the hashing utility.
- **Dependencies**: `passlib[argon2]` added to `pyproject.toml`.
- **Database**: New migration to remove unique constraint on `auth.user.password_hash`.
- **Tests**: Acceptance tests for user create/update updated to assert Argon2id hash format; integration tests may need updated mock data.
