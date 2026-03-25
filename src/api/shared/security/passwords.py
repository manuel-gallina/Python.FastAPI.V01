"""Password hashing and verification utilities."""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password using Argon2id.

    Args:
        plain (str): The plaintext password to hash.

    Returns:
        str: The Argon2id hash string.
    """
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against an Argon2id hash.

    Args:
        plain (str): The plaintext password to verify.
        hashed (str): The stored Argon2id hash.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return _pwd_context.verify(plain, hashed)
