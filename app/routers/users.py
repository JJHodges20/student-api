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
    summary="View the current user profile",
    responses={
        401: {
            "description": "Authentication token is missing or invalid."
        },
    },
)
@limiter.limit("60/minute")
def get_my_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user's profile.

    - Requires JWT authentication.
    - Reads the user identity from the access token.
    - Returns only the public user fields.
    """

    return current_user