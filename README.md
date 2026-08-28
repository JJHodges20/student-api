# Student CRUD API

A database-backed REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite** for managing student records.

This project focuses on implementing the complete CRUD pattern, including creating, reading, replacing, partially updating, and deleting resources.

## Features

The API supports six main endpoints:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/students/` | Create a new student |
| GET | `/students/` | List all students |
| GET | `/students/{student_id}` | Get a specific student |
| PUT | `/students/{student_id}` | Fully replace a student |
| PATCH | `/students/{student_id}` | Partially update a student |
| DELETE | `/students/{student_id}` | Delete a student |

The student list can also be filtered by:

- Grade level
- Enrollment status

## Student Data

Each student contains:

- Name
- Unique email address
- Grade level from 1–12
- Optional GPA
- Enrollment status
- Automatically generated ID
- Creation date and time

Duplicate email addresses return a `409 Conflict`, while requests for students that do not exist return a `404 Not Found`.

## PUT vs. PATCH

This project demonstrates the difference between two types of updates:

- **PUT** requires a complete replacement of the student's editable information.
- **PATCH** allows individual fields to be updated without changing the remaining data.

## Project Structure

```text
student-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
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

This project demonstrates a complete database-backed CRUD API using FastAPI and SQLAlchemy. It provides practice with persistent storage, Pydantic schemas, filtering, duplicate handling, reusable helper functions, PUT vs. PATCH updates, HTTP status codes, and database operations.