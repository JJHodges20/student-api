# Hardened Student CRUD API

A secure, database-backed REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite** for managing student records.

This project demonstrates CRUD operations, persistent storage, JWT authentication, structured error handling, background tasks, CORS protection, rate limiting, input validation, and automated testing with pytest.

## Features

### Student Management

| Method | Endpoint | Access | Rate Limit | Description |
|---|---|---|---|---|
| POST | `/students/` | Protected | 20/minute | Create a student |
| GET | `/students/` | Public | 60/minute | List and filter students |
| GET | `/students/{student_id}` | Public | 60/minute | Get a specific student |
| PUT | `/students/{student_id}` | Protected | — | Fully replace a student |
| PATCH | `/students/{student_id}` | Protected | — | Partially update a student |
| DELETE | `/students/{student_id}` | Protected | — | Delete a student |

Students can also be filtered by grade level and enrollment status.

## Authentication

The API uses JWT Bearer authentication to protect endpoints that modify student data.

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| POST | `/auth/register` | 20/minute | Register a new user |
| POST | `/auth/login` | 5/minute | Log in and receive a JWT |
| GET | `/users/me` | 60/minute | View the authenticated user's profile |

Passwords are hashed using **Passlib and bcrypt** before being stored.

FastAPI's OAuth2 password flow is integrated with Swagger UI, allowing users to authenticate through the **Authorize** button.

## Security

The API includes several layers of protection:

- JWT authentication for protected endpoints
- Password hashing with Passlib and bcrypt
- OAuth2 password authentication
- CORS restrictions
- SlowAPI rate limiting
- Pydantic input validation
- Custom exception handling
- Business-rule validation

### CORS

Browser access is restricted to:

```text
http://localhost:8501
http://localhost:3000
```

These origins support local development with **Streamlit** and **React**.

Allowed HTTP methods are restricted to:

```text
GET
POST
PUT
PATCH
DELETE
```

### Rate Limiting

SlowAPI provides request limits for important endpoints:

- Login requests: **5 per minute**
- Create requests: **20 per minute**
- General GET/list requests: **60 per minute**

Requests that exceed a limit receive:

```text
429 Too Many Requests
```

## Input Validation

Pydantic schemas enforce limits on incoming data.

Examples include:

- Student names: 1–100 characters
- Student emails: 3–255 characters
- Grade levels: 1–12
- GPA: 0.0–4.0
- Usernames: 3–100 characters
- Passwords: 6–72 characters

Invalid request data is rejected before reaching the database.

## Background Tasks

FastAPI background tasks handle work that does not need to finish before an API response is returned.

When a student is created:

- The activity is written to `activity_log.txt`.
- A simulated notification runs after a 2-second delay.
- The notification is written to `notification_log.txt`.

When a student is deleted:

- The deletion is recorded in `activity_log.txt`.

## Structured Error Handling

Custom exceptions and global exception handlers provide consistent API responses:

- `NotFoundException` — `404 Not Found`
- `DuplicateException` — `409 Conflict`
- `BadRequestException` — `400 Bad Request`
- Rate limit exceeded — `429 Too Many Requests`

The API also prevents currently enrolled students from being deleted. A student must first be updated to `is_enrolled: false`.

## Automated Testing

The project includes an automated test suite built with **pytest** and FastAPI's `TestClient`.

Tests use a separate in-memory SQLite database so the development database is never modified during testing.

Reusable pytest fixtures provide:

- A FastAPI test client
- An isolated test database
- JWT authorization headers
- A reusable sample student

The authentication fixture creates a test user directly in the test database and generates a valid JWT, preventing unrelated CRUD tests from consuming the login rate limit.

### Test Coverage

The suite contains **12 passing tests** covering:

- Successful student creation
- Invalid grade validation
- Invalid GPA validation
- Listing students with an empty database
- Listing students with existing data
- Getting an existing student by ID
- Handling a nonexistent student
- Successfully updating a student
- Updating a nonexistent student
- Successfully deleting a student
- Deleting a nonexistent student
- Rejecting protected requests without authentication

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
│       ├── security.py
│       └── notifications.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_students.py
├── activity_log.txt
├── notification_log.txt
├── requirements.txt
├── students.db
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
- python-multipart
- SlowAPI
- pytest
- HTTPX

## Running the API

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Start the development server:

```powershell
python -m uvicorn app.main:app --reload
```

Open Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

## Running the Tests

From the project root, run:

```powershell
python -m pytest -v
```

The current test suite contains 12 tests:

```text
12 passed
```

The test database is created separately from `students.db` and reset between tests.

## Purpose

This project demonstrates how a FastAPI application can grow beyond basic CRUD functionality into a more secure and testable backend application.

It provides practice with database persistence, Pydantic validation, custom errors, password hashing, JWT authentication, OAuth2, protected routes, background processing, CORS, rate limiting, pytest fixtures, isolated test databases, and automated API testing.