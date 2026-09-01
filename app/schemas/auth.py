"""
Pydantic schemas for authentication and users.
"""

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    """Data required to register a new user."""

    username: str = Field(
        min_length=3,
        max_length=100,
    )

    password: str = Field(
        min_length=6,
        max_length=72,
    )


class TokenResponse(BaseModel):
    """JWT response returned after successful login."""

    access_token: str = Field(
        min_length=1,
        max_length=2000,
    )

    token_type: str = Field(
        min_length=1,
        max_length=20,
    )


class UserResponse(BaseModel):
    """Public representation of an application user."""

    id: int = Field(
        gt=0,
    )

    username: str = Field(
        min_length=3,
        max_length=100,
    )

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )