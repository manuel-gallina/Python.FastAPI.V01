## Context

Passwords are currently stored as `placeholder:{email}` strings in the `auth.user.password_hash` column. The placeholder was always a stopgap; no real cryptographic hashing is in place. The `password_hash` column has a `UNIQUE` constraint that will be removed as part of this change (see proposal for rationale).

The public API contract is unchanged: passwords arrive as plaintext in request bodies and are never returned in responses.

## Goals / Non-Goals

**Goals:**
- Hash passwords with Argon2id (OWASP recommended) before persisting them.
- Encapsulate hashing behind a small, reusable utility so future features (e.g., login/verify) can call it without touching the repository directly.
- Remove the `UNIQUE` constraint on `password_hash`.

**Non-Goals:**
- Password verification / login endpoint — out of scope for this change.
- Password strength validation — out of scope.
- Re-hashing existing rows — the database currently holds only placeholder data; no migration of existing hashes is needed.

## Decisions

### 1. Library: `passlib[argon2]`

**Chosen:** `passlib` with the `argon2` extra (which pulls in `argon2-cffi`).

**Alternatives considered:**
- `argon2-cffi` directly — lower-level, requires manual salt generation and encoding. `passlib` wraps it with a safe, high-level API and standardised hash string format (`$argon2id$...`), reducing the risk of misuse.
- `bcrypt` / `scrypt` — both are acceptable but OWASP now recommends Argon2id as the first choice; the issue also specifies it explicitly.

**Passlib defaults for Argon2id** (as of passlib 1.7): time_cost=2, memory_cost=102400 (100 MB), parallelism=8 — these meet or exceed the OWASP minimum parameters.

### 2. Module location: `src/api/shared/security/passwords.py`

**Chosen:** A dedicated module under `shared/security/` exposing two functions:
- `hash_password(plain: str) -> str`
- `verify_password(plain: str, hashed: str) -> bool`

`verify_password` is added now even though it has no caller yet, because hashing and verification always belong together and the next feature (login) will need it immediately.

**Alternatives considered:**
- Inline hashing inside `UsersRepository` — couples the repository to the security library and duplicates the import site when verification is added later.
- A class/service — unnecessary indirection for two pure functions.

### 3. Database migration: drop UNIQUE constraint on `password_hash`

A new Alembic revision drops the constraint before any real hashes are written. Because existing rows hold only placeholder values (not real user data), no data migration is required.

## Risks / Trade-offs

- **passlib is in maintenance mode** — The project is stable and widely used, but receives only security fixes. Acceptable for now; revisit if a successor emerges.
  → Mitigation: encapsulating the library behind `shared/security/passwords.py` makes a future swap a single-file change.

- **Default Argon2id parameters may be too slow on constrained hardware** — 100 MB memory cost could be an issue on low-memory deployments.
  → Mitigation: document the parameters in the module and make them overridable via settings if needed in the future (out of scope now).

- **Existing `password_hash` values are invalid after this change** — Any rows already in the DB hold placeholder strings; they cannot be verified with Argon2id.
  → Acceptable: existing data is non-production placeholder data with no real users.

## Migration Plan

1. Add `passlib[argon2]` to `pyproject.toml` dependencies.
2. Create `src/api/shared/security/passwords.py` with `hash_password` and `verify_password`.
3. Generate and apply a new Alembic migration that drops `UNIQUE` on `auth.user.password_hash`.
4. Update `UsersRepository.create()` and `UsersRepository.update()` to call `hash_password()`.
5. Update acceptance tests to assert the stored hash starts with `$argon2id$` instead of `placeholder:`.

Rollback: revert the migration (re-add the constraint) and revert the repository and utility changes. No data loss risk since placeholder rows are non-production.

## Open Questions

_(none)_
