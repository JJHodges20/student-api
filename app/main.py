"""
Main application for the Student CRUD API.
"""

from fastapi import FastAPI

from app.database import Base, engine
from app.models.student import Student
from app.routers import students


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Student CRUD API",
    description=(
        "A database-backed FastAPI application "
        "demonstrating complete CRUD operations."
    ),
    version="1.0.0",
)


app.include_router(students.router)


@app.get("/", tags=["Root"])
def root():
    """Return a welcome message."""

    return {
        "message": "Welcome to the Student CRUD API"
    }