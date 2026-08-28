"""
CRUD routes for students.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.schemas.student import (
    StudentCreate,
    StudentPatch,
    StudentResponse,
    StudentUpdate,
)


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


# ============================================================
# Helper functions
# ============================================================

def get_student_or_404(
    student_id: int,
    db: Session,
) -> Student:
    """
    Return a student by ID.

    Raises 404 if the student does not exist.
    """

    student = db.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return student


def email_in_use(
    email: str,
    db: Session,
    exclude_student_id: int | None = None,
) -> bool:
    """
    Check whether an email address already belongs to a student.

    exclude_student_id is useful during PUT/PATCH so a student
    can keep their existing email address.
    """

    statement = select(Student).where(
        Student.email == email
    )

    if exclude_student_id is not None:
        statement = statement.where(
            Student.id != exclude_student_id
        )

    return db.scalar(statement) is not None


# ============================================================
# CREATE
# POST /students
# ============================================================

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=201,
)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
):
    """Create and persist a new student."""

    if email_in_use(student.email, db):
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists",
        )

    new_student = Student(
        name=student.name,
        email=student.email,
        grade_level=student.grade_level,
        gpa=student.gpa,
        is_enrolled=student.is_enrolled,
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


# ============================================================
# READ COLLECTION
# GET /students
# ============================================================

@router.get(
    "/",
    response_model=list[StudentResponse],
)
def list_students(
    grade_level: int | None = Query(
        default=None,
        ge=1,
        le=12,
    ),
    is_enrolled: bool | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    """
    List students with optional grade-level
    and enrollment-status filters.
    """

    statement = select(Student)

    if grade_level is not None:
        statement = statement.where(
            Student.grade_level == grade_level
        )

    if is_enrolled is not None:
        statement = statement.where(
            Student.is_enrolled == is_enrolled
        )

    statement = statement.order_by(Student.id)

    return db.scalars(statement).all()


# ============================================================
# READ ONE
# GET /students/{student_id}
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentResponse,
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """Return one student by ID."""

    return get_student_or_404(
        student_id,
        db,
    )


# ============================================================
# FULL UPDATE
# PUT /students/{student_id}
# ============================================================

@router.put(
    "/{student_id}",
    response_model=StudentResponse,
)
def replace_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
):
    """Fully replace a student's editable fields."""

    student = get_student_or_404(
        student_id,
        db,
    )

    if email_in_use(
        student_data.email,
        db,
        exclude_student_id=student_id,
    ):
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists",
        )

    student.name = student_data.name
    student.email = student_data.email
    student.grade_level = student_data.grade_level
    student.gpa = student_data.gpa
    student.is_enrolled = student_data.is_enrolled

    db.commit()
    db.refresh(student)

    return student


# ============================================================
# PARTIAL UPDATE
# PATCH /students/{student_id}
# ============================================================

@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
)
def patch_student(
    student_id: int,
    student_data: StudentPatch,
    db: Session = Depends(get_db),
):
    """Update only the fields supplied by the client."""

    student = get_student_or_404(
        student_id,
        db,
    )

    updates = student_data.model_dump(
        exclude_unset=True
    )

    if "email" in updates:
        if email_in_use(
            updates["email"],
            db,
            exclude_student_id=student_id,
        ):
            raise HTTPException(
                status_code=409,
                detail="A student with this email already exists",
            )

    for field, value in updates.items():
        setattr(
            student,
            field,
            value,
        )

    db.commit()
    db.refresh(student)

    return student


# ============================================================
# DELETE
# DELETE /students/{student_id}
# ============================================================

@router.delete(
    "/{student_id}",
    status_code=204,
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """Delete a student."""

    student = get_student_or_404(
        student_id,
        db,
    )

    db.delete(student)
    db.commit()

    return Response(status_code=204)