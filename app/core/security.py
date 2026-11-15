"""Password hashing and signed token utilities."""
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from app.core.config import get_settings

_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2id (argon2-cffi defaults)."""
    return _hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Return false for invalid credentials without leaking verifier errors."""
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False

def create_access_token(subject: str, organization_id: str, role: str) -> str:
    """Create a short-lived access token containing the active tenant context."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "org": organization_id, "role": role,
               "iat": now, "exp": now + timedelta(minutes=settings.access_token_minutes),
               "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
