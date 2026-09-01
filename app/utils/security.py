"""
Security utilities for password hashing and JWT authentication.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestException
from app.models.user import User


SECRET_KEY = "replace-this-with-a-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def hash_password(password: str) -> str:
    """Hash a password before storing it."""

    return password_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Compare a plain password with its stored hash."""

    return password_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: int,
) -> str:
    """Create a signed JWT access token."""

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Return the authenticated user from a JWT."""

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise BadRequestException(
                "Invalid authentication token."
            )

        user = db.get(
            User,
            int(user_id),
        )

    except (JWTError, ValueError):
        raise BadRequestException(
            "Invalid authentication token."
        )

    if user is None:
        raise BadRequestException(
            "User associated with this token was not found."
        )

    if not user.is_active:
        raise BadRequestException(
            "User account is inactive."
        )

    return user