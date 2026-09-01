"""
CRUD routes for students using custom application exceptions.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import (
    BadRequestException,
    DuplicateException,
    NotFoundException,
)
from app.models.student import Student
from app.schemas.student import (
    StudentCreate,
    StudentPatch,
    StudentResponse,
    StudentUpdate,
)

from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

from app.utils.notifications import (
    log_activity,
    send_notification,
)

# ============================================================
# Helper functions
# ============================================================

def get_student_or_404(
    student_id: int,
    db: Session,
) -> Student:
    """Return a student or raise NotFoundException."""

    student = db.get(Student, student_id)

    if student is None:
        raise NotFoundException(
            f"Student with ID {student_id} was not found."
        )

    return student


def email_in_use(
    email: str,
    db: Session,
    exclude_student_id: int | None = None,
) -> bool:
    """Return True if the email already belongs to another student."""

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
# ============================================================

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=201,
)
def create_student(
    student: StudentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new student and schedule background tasks."""

    if email_in_use(student.email, db):
        raise DuplicateException(
            "A student with this email already exists."
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

    # Runs after the API response is returned.
    background_tasks.add_task(
        log_activity,
        current_user.id,
        f"Created student {new_student.id} "
        f"({new_student.name})",
    )

    # Simulates a slower email/notification operation.
    background_tasks.add_task(
        send_notification,
        new_student.email,
        (
            f"Student record created successfully "
            f"for {new_student.name}."
        ),
    )

    return new_student
    if email_in_use(student.email, db):
        raise DuplicateException(
            "A student with this email already exists."
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
# READ ALL
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
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentResponse,
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    return get_student_or_404(
        student_id,
        db,
    )


# ============================================================
# PUT
# ============================================================

@router.put(
    "/{student_id}",
    response_model=StudentResponse,
)
def replace_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = get_student_or_404(
        student_id,
        db,
    )

    if email_in_use(
        student_data.email,
        db,
        exclude_student_id=student_id,
    ):
        raise DuplicateException(
            "A student with this email already exists."
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
# PATCH
# ============================================================

@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
)
def patch_student(
    student_id: int,
    student_data: StudentPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
            raise DuplicateException(
                "A student with this email already exists."
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
# ============================================================

@router.delete(
    "/{student_id}",
    status_code=204,
)
def delete_student(
    student_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a student and log the action in the background."""

    student = get_student_or_404(
        student_id,
        db,
    )

    if student.is_enrolled:
        raise BadRequestException(
            "An enrolled student cannot be deleted. "
            "Mark the student as not enrolled first."
        )

    # Save information before deleting the ORM object.
    student_name = student.name

    db.delete(student)
    db.commit()

    background_tasks.add_task(
        log_activity,
        current_user.id,
        f"Deleted student {student_id} ({student_name})",
    )

    return Response(status_code=204)

    # Business rule:
    # Active/enrolled students cannot be deleted.
    if student.is_enrolled:
        raise BadRequestException(
            "An enrolled student cannot be deleted. "
            "Mark the student as not enrolled first."
        )

    db.delete(student)
    db.commit()

    return Response(status_code=204)