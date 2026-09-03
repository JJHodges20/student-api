# Hardened Student CRUD API

A secure, database-backed REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite** for managing student records.

This project demonstrates a complete CRUD application with persistent storage, structured error handling, JWT authentication, background tasks, CORS protection, rate limiting, input validation, automated testing, and polished OpenAPI documentation.

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

Students can be filtered by grade level and enrollment status.

## Authentication

The API uses JWT Bearer authentication for protected endpoints.

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| POST | `/auth/register` | 20/minute | Register a new user |
| POST | `/auth/login` | 5/minute | Log in and receive a JWT |
| GET | `/users/me` | 60/minute | View the authenticated user's profile |

Passwords are hashed using **Passlib and bcrypt** before being stored.

FastAPI's OAuth2 password flow is integrated with Swagger UI through the **Authorize** button.

## Professional API Documentation

The API includes enhanced OpenAPI documentation with:

- Application title and version
- Markdown-formatted API description
- Descriptions for each router tag
- Endpoint summaries
- Markdown endpoint docstrings
- Documented error responses
- Example response data using `json_schema_extra`

Documentation is available through both FastAPI interfaces:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger provides an interactive interface for viewing and testing endpoints.

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

ReDoc provides a structured API-reference view generated from the same OpenAPI specification.

## Documented Responses

Endpoints include documentation for common HTTP responses such as:

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `429 Too Many Requests`

## Security

The API includes several layers of protection:

- JWT Bearer authentication
- Password hashing
- OAuth2 authentication flow
- CORS restrictions
- SlowAPI rate limiting
- Pydantic input validation
- Custom exception handling
- Business-rule validation

### CORS

Allowed browser origins:

```text
http://localhost:8501
http://localhost:3000
```

Allowed methods:

```text
GET
POST
PUT
PATCH
DELETE
```

### Rate Limiting

SlowAPI applies limits including:

- Login: **5 requests per minute**
- Create endpoints: **20 requests per minute**
- General GET endpoints: **60 requests per minute**

Requests that exceed the configured limit receive:

```text
429 Too Many Requests
```

## Input Validation

Pydantic schemas enforce constraints such as:

- Student names: 1–100 characters
- Emails: 3–255 characters
- Grade levels: 1–12
- GPA: 0.0–4.0
- Usernames: 3–100 characters
- Passwords: 6–72 characters

Invalid requests are rejected before reaching the database.

## Background Tasks

FastAPI background tasks are used for non-critical post-response processing.

When a student is created:

- The activity is logged
- A simulated notification runs after a delay
- The API response does not wait for the notification to finish

When a student is deleted:

- The deletion is logged in the background

Generated files include:

```text
activity_log.txt
notification_log.txt
```

## Structured Error Handling

Custom exceptions provide consistent error responses:

- `NotFoundException` — `404`
- `DuplicateException` — `409`
- `BadRequestException` — `400`

The API also prevents enrolled students from being deleted until their enrollment status is changed.

## Automated Testing

The project includes a pytest suite using a separate in-memory SQLite database.

Tests cover:

- Successful student creation
- Invalid grade validation
- Invalid GPA validation
- Empty and populated student lists
- Student lookup success and failure
- Student update success and failure
- Student deletion success and failure
- Authentication protection

Current test result:

```text
12 passed
```

Run the tests with:

```powershell
python -m pytest -v
```

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
├── students.db
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

Then open:

```text
http://127.0.0.1:8000/docs
```

or:

```text
http://127.0.0.1:8000/redoc
```

## Purpose

This project demonstrates how a FastAPI application can evolve from a basic CRUD API into a more complete backend service with persistence, authentication, validation, security protections, background processing, automated testing, and professional API documentation.