"""
Security measures implemented in this API:

- JWT Bearer authentication for protected endpoints
- Password hashing with Passlib and bcrypt
- OAuth2 password authentication
- CORS restricted to approved frontend origins
- HTTP methods restricted through CORS configuration
- SlowAPI rate limiting
- Pydantic input validation and length constraints
- Custom structured exception handling
- Business rule preventing deletion of enrolled students
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.database import Base, engine
from app.exceptions import (
    BadRequestException,
    DuplicateException,
    NotFoundException,
)
from app.routers import auth, students, users


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# API DOCUMENTATION
# ============================================================

tags_metadata = [
    {
        "name": "Authentication",
        "description": (
            "Register users and authenticate with **JWT Bearer tokens**."
        ),
    },
    {
        "name": "Students",
        "description": (
            "Create, view, update, and delete student records. "
            "Write operations require authentication."
        ),
    },
    {
        "name": "Users",
        "description": (
            "Access information about the currently authenticated user."
        ),
    },
    {
        "name": "Root",
        "description": "Basic API status and welcome endpoint.",
    },
]


# ============================================================
# RATE LIMITING
# ============================================================

limiter = Limiter(
    key_func=get_remote_address
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Secure Student CRUD API",
    description="""
## Student Management API

A secure REST API for managing student records.

### Features

- **Create, read, update, and delete** student records
- Filter students by **grade level** and **enrollment status**
- Authenticate users with **JWT Bearer tokens**
- Validate incoming data with **Pydantic**
- Protect endpoints with **rate limiting**
- Restrict browser access with **CORS**
- Run non-critical work using **background tasks**
- Return consistent **structured error responses**

### Authentication

Public endpoints can be accessed without authentication.

Protected endpoints require a JWT access token obtained through the
`/auth/login` endpoint.

Use the **Authorize** button in Swagger UI to authenticate.
""",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


# ============================================================
# CUSTOM EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(NotFoundException)
async def not_found_handler(
    request: Request,
    exc: NotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": exc.message,
        },
    )


@app.exception_handler(DuplicateException)
async def duplicate_handler(
    request: Request,
    exc: DuplicateException,
):
    return JSONResponse(
        status_code=409,
        content={
            "error": "duplicate",
            "message": exc.message,
        },
    )


@app.exception_handler(BadRequestException)
async def bad_request_handler(
    request: Request,
    exc: BadRequestException,
):
    return JSONResponse(
        status_code=400,
        content={
            "error": "bad_request",
            "message": exc.message,
        },
    )


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(users.router)


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["Root"],
    summary="View API welcome message",
)
@limiter.limit("60/minute")
def root(request: Request):
    """
    Return basic information about the API.

    - Confirms that the API is running.
    - Provides a simple welcome message.
    - Does not require authentication.
    """

    return {
        "message": "Welcome to the Secure Student CRUD API"
    }