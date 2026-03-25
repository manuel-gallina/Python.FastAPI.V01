"""Unit tests for src/api/shared/security/passwords.py."""

from api.shared.security.passwords import hash_password, verify_password


def test_hash_password_returns_argon2id_hash() -> None:
    result = hash_password("secret")
    assert result.startswith("$argon2id$")


def test_hash_password_produces_unique_salts() -> None:
    hash1 = hash_password("secret")
    hash2 = hash_password("secret")
    assert hash1 != hash2


def test_verify_password_returns_true_for_correct_password() -> None:
    hashed = hash_password("correct")
    assert verify_password("correct", hashed) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    hashed = hash_password("correct")
    assert verify_password("wrong", hashed) is False
