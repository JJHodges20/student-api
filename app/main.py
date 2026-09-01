"""
Main application for the secured Student CRUD API.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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


app = FastAPI(
    title="Secure Student CRUD API",
    description=(
        "A database-backed CRUD API "
        "with JWT authentication."
    ),
    version="3.0.0",
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
def root():
    return {
        "message": "Welcome to the Secure Student CRUD API"
    }