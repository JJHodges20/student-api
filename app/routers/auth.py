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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    responses={
        409: {
            "description": "The username is already registered."
        },
        422: {
            "description": "The registration data is invalid."
        },
    },
)
@limiter.limit("20/minute")
def register(
    request: Request,
    register_request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new application user.

    - Validates the submitted username and password.
    - Rejects usernames that are already registered.
    - Hashes the password before database storage.
    - Returns the newly created public user profile.
    """

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


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT",
    responses={
        400: {
            "description": "The username or password is incorrect."
        },
        422: {
            "description": "Required login fields are missing or invalid."
        },
        429: {
            "description": "Too many login attempts."
        },
    },
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate an existing user.

    - Accepts an OAuth2 username and password.
    - Verifies the stored password hash.
    - Returns a JWT access token after successful authentication.
    - Limits login attempts to **5 requests per minute**.
    """

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