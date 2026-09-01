# Student CRUD API

A database-backed REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite** for managing student records.

This version expands the Student CRUD API by adding structured error handling with custom exceptions and global exception handlers.

## Features

The API supports the complete CRUD cycle:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/students/` | Create a new student |
| GET | `/students/` | List all students |
| GET | `/students/{student_id}` | Get a specific student |
| PUT | `/students/{student_id}` | Fully replace a student |
| PATCH | `/students/{student_id}` | Partially update a student |
| DELETE | `/students/{student_id}` | Delete a student |

Student lists can also be filtered by grade level and enrollment status.

## Structured Error Handling

Custom exceptions are used instead of raising `HTTPException` directly inside the router:

- `NotFoundException` — returns `404 Not Found`
- `DuplicateException` — returns `409 Conflict`
- `BadRequestException` — returns `400 Bad Request`

Global exception handlers in `main.py` ensure these errors return a consistent response format.

Example:

```json
{
  "error": "not_found",
  "message": "Student with ID 10 was not found."
}
```

## Business Logic

The API includes a rule preventing currently enrolled students from being deleted.

If `is_enrolled` is `true`, the DELETE request returns a `400 Bad Request`. The student must first be updated to `is_enrolled: false` before deletion.

Duplicate student email addresses are also prevented and return a `409 Conflict`.

## Project Structure

```text
student-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── exceptions.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── student.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── student.py
│   └── routers/
│       ├── __init__.py
│       └── students.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

## Running the API

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

Start the development server:

```powershell
python -m uvicorn app.main:app --reload
```

Open the Swagger documentation at:

```text
http://127.0.0.1:8000/docs
```

## Purpose

This project demonstrates how structured error handling can improve a database-backed CRUD API. It provides practice with custom exceptions, global exception handlers, consistent API error responses, business-logic validation, persistent storage, filtering, and the complete CRUD pattern.