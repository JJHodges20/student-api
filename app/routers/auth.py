"""
Authentication routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestException, DuplicateException
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new application user."""

    existing_user = db.scalar(
        select(User).where(
            User.username == request.username
        )
    )

    if existing_user is not None:
        raise DuplicateException(
            "Username is already registered."
        )

    user = User(
        username=request.username,
        hashed_password=hash_password(
            request.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate a user and return a JWT."""

    user = db.scalar(
        select(User).where(
            User.username == request.username
        )
    )

    if user is None:
        raise BadRequestException(
            "Invalid username or password."
        )

    if not verify_password(
        request.password,
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