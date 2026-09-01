"""
User profile routes.
"""

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.user import User
from app.schemas.auth import UserResponse
from app.utils.security import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

limiter = Limiter(
    key_func=get_remote_address
)


@router.get(
    "/me",
    response_model=UserResponse,
)
@limiter.limit("60/minute")
def get_my_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Return the currently authenticated user's profile."""

    return current_user