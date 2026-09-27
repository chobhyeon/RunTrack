"""Password and access token helpers."""
from datetime import datetime, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings


password_context = CryptContext(
    schemes=["pbkdf2_sha256"], pbkdf2_sha256__default_rounds=600_000,
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_context.verify(password, hashed_password)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> tuple[str, int]:
    """Return a signed token and its lifetime in seconds from one configuration."""
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    if expires_in <= 0:
        raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
    issued_at = int(datetime.now(timezone.utc).timestamp())
    payload = {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": issued_at + expires_in,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expires_in


def decode_access_token(token: str) -> int:
    """Validate a token and return a PostgreSQL INTEGER user ID."""
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],
        options={"require_exp": True, "require_sub": True},
    )
    expiry = payload["exp"]
    if type(expiry) is not int or expiry <= int(datetime.now(timezone.utc).timestamp()):
        raise JWTError("Invalid expiry")
    subject = payload["sub"]
    if (not isinstance(subject, str) or not subject.isascii()
            or not subject.isdecimal() or len(subject) > 10):
        raise JWTError("Invalid subject")
    user_id = int(subject)
    if not 0 < user_id <= 2_147_483_647:
        raise JWTError("Invalid subject")
    return user_id
