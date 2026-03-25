## ADDED Requirements

### Requirement: Password hashed on user creation
When a new user is created, the system SHALL hash the plaintext password using Argon2id before persisting it to the database. The plaintext password SHALL NOT be stored.

#### Scenario: User created with valid password
- **WHEN** a POST request is made to create a user with a plaintext password
- **THEN** the stored `password_hash` value starts with `$argon2id$`

#### Scenario: Two users created with the same password
- **WHEN** two users are created with identical plaintext passwords
- **THEN** their stored `password_hash` values are different (unique salts)

### Requirement: Password hashed on user update
When an existing user is updated, the system SHALL hash the new plaintext password using Argon2id before persisting it. The plaintext password SHALL NOT be stored.

#### Scenario: User updated with a new password
- **WHEN** a PUT request is made to update a user with a plaintext password
- **THEN** the stored `password_hash` value starts with `$argon2id$`

### Requirement: Password verification
The system SHALL provide a utility function that verifies a plaintext password against a stored Argon2id hash.

#### Scenario: Correct password verified successfully
- **WHEN** `verify_password` is called with the original plaintext and its Argon2id hash
- **THEN** it returns `True`

#### Scenario: Incorrect password rejected
- **WHEN** `verify_password` is called with a wrong plaintext and an Argon2id hash
- **THEN** it returns `False`

### Requirement: OWASP-compliant hashing parameters
The Argon2id configuration SHALL use parameters that meet or exceed OWASP minimum recommendations: memory ≥ 19 MB, iterations ≥ 2, parallelism ≥ 1.

#### Scenario: Hash produced with compliant parameters
- **WHEN** `hash_password` is called with any plaintext
- **THEN** the resulting hash encodes memory_cost ≥ 19456 kB, time_cost ≥ 2, and parallelism ≥ 1
