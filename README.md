# Secure Student CRUD API

A database-backed REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite** for managing student records.

This version expands the Student CRUD API by adding **JWT authentication**, user registration, login, password hashing, protected endpoints, and structured error handling.

## Features

### Student CRUD

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/students/` | Protected | Create a student |
| GET | `/students/` | Public | List and filter students |
| GET | `/students/{student_id}` | Public | Get a specific student |
| PUT | `/students/{student_id}` | Protected | Fully replace a student |
| PATCH | `/students/{student_id}` | Protected | Partially update a student |
| DELETE | `/students/{student_id}` | Protected | Delete a student |

Students can also be filtered by grade level and enrollment status.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in and receive a JWT access token |
| GET | `/users/me` | View the authenticated user's profile |

## Security

Passwords are hashed with **Passlib and bcrypt** before being stored in the database. Plain-text passwords are never saved.

After a successful login, the API generates a **JWT access token**. Protected endpoints require a valid Bearer token before the request is allowed.

Swagger UI can be used to authenticate and test protected endpoints.

## Structured Error Handling

The API uses custom exceptions and global exception handlers for consistent error responses:

- `NotFoundException` — `404 Not Found`
- `DuplicateException` — `409 Conflict`
- `BadRequestException` — `400 Bad Request`

The API also prevents enrolled students from being deleted until their enrollment status is changed.

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
│   │   ├── student.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── student.py
│   │   └── auth.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py
│   │   ├── auth.py
│   │   └── users.py
│   └── utils/
│       ├── __init__.py
│       └── security.py
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
- python-jose
- Passlib
- bcrypt

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

## Authentication Flow

The basic authentication process is:

```text
Register
   ↓
Password is hashed and user is stored
   ↓
Login
   ↓
Credentials are verified
   ↓
JWT access token is generated
   ↓
Token is sent with protected requests
   ↓
API verifies the token and identifies the user
   ↓
Protected endpoint is accessed
```

## Purpose

This project demonstrates how authentication can be added to a database-backed FastAPI application. It provides practice with user registration, secure password hashing, JWT access tokens, authentication dependencies, protected routes, persistent storage, structured error handling, and the complete CRUD pattern.