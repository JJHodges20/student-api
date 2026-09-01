"""
Secure Student CRUD API

Security measures:
- JWT Bearer authentication protects modifying student endpoints.
- Passwords are hashed with Passlib and bcrypt.
- OAuth2 password authentication is used for login.
- CORS restricts browser access to approved frontend origins.
- HTTP methods exposed through CORS are restricted.
- SlowAPI rate limiting protects endpoints from excessive requests.
- Login requests are limited to 5 per minute.
- Create requests are limited to 20 per minute.
- General read requests are limited to 60 per minute.
- Pydantic schemas enforce input length and numeric constraints.
- Custom exceptions provide controlled API error responses.
- Business rules prevent deletion of currently enrolled students.
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
from app.models.student import Student
from app.models.user import User
from app.routers import auth, students, users


Base.metadata.create_all(bind=engine)


# Rate limiter
limiter = Limiter(
    key_func=get_remote_address
)


app = FastAPI(
    title="Secure Student CRUD API",
    description=(
        "A database-backed CRUD API with JWT authentication, "
        "background tasks, CORS protection, and rate limiting."
    ),
    version="4.0.0",
)


# Make the limiter available throughout the application.
app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# CORS configuration
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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(students.router)


@app.get("/", tags=["Root"])
@limiter.limit("60/minute")
def root(request: Request):
    return {
        "message": "Welcome to the Secure Student CRUD API"
    }