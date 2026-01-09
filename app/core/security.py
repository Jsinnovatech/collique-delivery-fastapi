from datetime import datetime, timedelta
from typing import Any, Union, Optional
import hashlib
import secrets

from jose import jwt

from app.core.config import settings


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        salt, stored_hash = hashed_password.split('$')
        password_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
        return password_hash.hex() == stored_hash
    except:
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash using PBKDF2."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${password_hash.hex()}"


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except Exception:
        return None