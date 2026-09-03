"""
CRUD routes for students.

Security:
- GET endpoints are public and rate-limited to 60/minute.
- POST is protected and rate-limited to 20/minute.
- PUT, PATCH, and DELETE require authentication.
- Background tasks log create/delete activity.
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    Request,
    Response,
)
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import (
    BadRequestException,
    DuplicateException,
    NotFoundException,
)
from app.models.student import Student
from app.models.user import User
from app.schemas.student import (
    StudentCreate,
    StudentPatch,
    StudentResponse,
    StudentUpdate,
)
from app.utils.notifications import (
    log_activity,
    send_notification,
)
from app.utils.security import get_current_user


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

limiter = Limiter(
    key_func=get_remote_address
)


# ============================================================
# HELPERS
# ============================================================

def get_student_or_404(
    student_id: int,
    db: Session,
) -> Student:
    """Return a student or raise a custom 404 exception."""

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
    """Return True if another student already uses this email."""

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
    summary="Create a new student",
    responses={
        401: {
            "description": "Authentication token is missing or invalid."
        },
        409: {
            "description": "A student with this email already exists."
        },
        422: {
            "description": "The submitted student data is invalid."
        },
    },
)
@limiter.limit("20/minute")
def create_student(
    request: Request,
    student: StudentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new student record.

    - Requires JWT authentication.
    - Validates grade level and GPA ranges.
    - Rejects duplicate email addresses.
    - Logs the creation as a background task.
    - Sends a simulated background notification.
    """

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

    background_tasks.add_task(
        log_activity,
        current_user.id,
        f"Created student {new_student.id} ({new_student.name})",
    )

    background_tasks.add_task(
        send_notification,
        new_student.email,
        f"Student record created successfully for {new_student.name}.",
    )

    return new_student


# ============================================================
# READ ALL
# ============================================================

@router.get(
    "/",
    response_model=list[StudentResponse],
    summary="List student records",
    responses={
        422: {
            "description": "One or more query parameters are invalid."
        },
    },
)
@limiter.limit("60/minute")
def list_students(
    request: Request,
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
    Return a list of students.

    - Does not require authentication.
    - Can filter results by **grade level**.
    - Can filter results by **enrollment status**.
    - Returns all students when no filters are supplied.
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
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get a student by ID",
    responses={
        404: {
            "description": "The requested student was not found."
        },
        422: {
            "description": "The student ID is invalid."
        },
    },
)
@limiter.limit("60/minute")
def get_student(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
):
    """
    Return one student by ID.

    - Does not require authentication.
    - Searches for the student using the provided ID.
    - Returns `404 Not Found` when the student does not exist.
    """

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
    summary="Replace a student record",
    responses={
        401: {
            "description": "Authentication token is missing or invalid."
        },
        404: {
            "description": "The requested student was not found."
        },
        409: {
            "description": "The email is already used by another student."
        },
        422: {
            "description": "The submitted student data is invalid."
        },
    },
)
def replace_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fully replace an existing student record.

    - Requires JWT authentication.
    - Requires all editable student fields.
    - Validates the replacement data.
    - Rejects an email already used by another student.
    - Returns `404 Not Found` when the student does not exist.
    """

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
    summary="Partially update a student",
    responses={
        401: {
            "description": "Authentication token is missing or invalid."
        },
        404: {
            "description": "The requested student was not found."
        },
        409: {
            "description": "The email is already used by another student."
        },
        422: {
            "description": "The submitted update data is invalid."
        },
    },
)
def patch_student(
    student_id: int,
    student_data: StudentPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update selected fields on an existing student.

    - Requires JWT authentication.
    - Only changes fields included in the request.
    - Validates any fields that are supplied.
    - Rejects duplicate student email addresses.
    - Returns `404 Not Found` when the student does not exist.
    """

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
    summary="Delete a student record",
    responses={
        400: {
            "description": "An enrolled student cannot be deleted."
        },
        401: {
            "description": "Authentication token is missing or invalid."
        },
        404: {
            "description": "The requested student was not found."
        },
    },
)
def delete_student(
    student_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an existing student.

    - Requires JWT authentication.
    - Returns `404 Not Found` when the student does not exist.
    - Prevents deletion while the student is enrolled.
    - Logs successful deletion as a background task.
    """

    student = get_student_or_404(
        student_id,
        db,
    )

    if student.is_enrolled:
        raise BadRequestException(
            "An enrolled student cannot be deleted. "
            "Mark the student as not enrolled first."
        )

    student_name = student.name

    db.delete(student)
    db.commit()

    background_tasks.add_task(
        log_activity,
        current_user.id,
        f"Deleted student {student_id} ({student_name})",
    )

    return Response(status_code=204)