"""
Main application for the Student CRUD API.
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
from app.routers import students


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Student CRUD API",
    description="A CRUD API demonstrating structured error handling.",
    version="2.0.0",
)


# ============================================================
# Global exception handlers
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


app.include_router(students.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Student CRUD API"
    }