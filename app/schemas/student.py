"""
Pydantic schemas for student data.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    """Schema for creating a student."""

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: str = Field(
        min_length=1,
        max_length=255,
    )

    grade_level: int = Field(
        ge=1,
        le=12,
    )

    gpa: float | None = None

    is_enrolled: bool = True


class StudentUpdate(BaseModel):
    """
    Schema for a complete PUT replacement.

    All main fields must be supplied.
    """

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: str = Field(
        min_length=1,
        max_length=255,
    )

    grade_level: int = Field(
        ge=1,
        le=12,
    )

    gpa: float | None

    is_enrolled: bool


class StudentPatch(BaseModel):
    """
    Schema for a partial PATCH update.

    Every field is optional.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    grade_level: int | None = Field(
        default=None,
        ge=1,
        le=12,
    )

    gpa: float | None = None

    is_enrolled: bool | None = None


class StudentResponse(BaseModel):
    """Schema returned by the API."""

    id: int
    name: str
    email: str
    grade_level: int
    gpa: float | None
    is_enrolled: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )