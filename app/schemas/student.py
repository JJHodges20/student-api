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
        min_length=3,
        max_length=255,
    )

    grade_level: int = Field(
        ge=1,
        le=12,
    )

    gpa: float | None = Field(
        default=None,
        ge=0.0,
        le=4.0,
    )

    is_enrolled: bool = True


class StudentUpdate(BaseModel):
    """Schema for a complete PUT replacement."""

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: str = Field(
        min_length=3,
        max_length=255,
    )

    grade_level: int = Field(
        ge=1,
        le=12,
    )

    gpa: float | None = Field(
        default=None,
        ge=0.0,
        le=4.0,
    )

    is_enrolled: bool


class StudentPatch(BaseModel):
    """Schema for partial PATCH updates."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    grade_level: int | None = Field(
        default=None,
        ge=1,
        le=12,
    )

    gpa: float | None = Field(
        default=None,
        ge=0.0,
        le=4.0,
    )

    is_enrolled: bool | None = None


class StudentResponse(BaseModel):
    """Schema returned by the API."""

    id: int = Field(
        gt=0,
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: str = Field(
        min_length=3,
        max_length=255,
    )

    grade_level: int = Field(
        ge=1,
        le=12,
    )

    gpa: float | None = Field(
        default=None,
        ge=0.0,
        le=4.0,
    )

    is_enrolled: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Jordan Smith",
                "email": "jordan@example.com",
                "grade_level": 11,
                "gpa": 3.7,
                "is_enrolled": True,
                "created_at": "2026-09-03T08:00:00",
            }
        },
    )