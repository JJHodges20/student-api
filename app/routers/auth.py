"""
Authentication routes.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestException, DuplicateException
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


limiter = Limiter(
    key_func=get_remote_address
)


# ============================================================
# REGISTER
# 20 requests per minute
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
@limiter.limit("20/minute")
def register(
    request: Request,
    register_request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new application user."""

    existing_user = db.scalar(
        select(User).where(
            User.username == register_request.username
        )
    )

    if existing_user is not None:
        raise DuplicateException(
            "Username is already registered."
        )

    user = User(
        username=register_request.username,
        hashed_password=hash_password(
            register_request.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# LOGIN
# 5 requests per minute
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate a user and return a JWT access token."""

    user = db.scalar(
        select(User).where(
            User.username == form_data.username
        )
    )

    if user is None:
        raise BadRequestException(
            "Invalid username or password."
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise BadRequestException(
            "Invalid username or password."
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }