# Hardened Student CRUD API

A secure, database-backed REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite** for managing student records.

This project demonstrates a complete CRUD application with persistent storage, structured error handling, JWT authentication, background tasks, CORS protection, rate limiting, and input validation.

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

The API uses JWT Bearer authentication to protect endpoints that modify student data.

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| POST | `/auth/register` | 20/minute | Register a new user |
| POST | `/auth/login` | 5/minute | Log in and receive a JWT |
| GET | `/users/me` | 60/minute | View the authenticated user's profile |

Passwords are hashed using **Passlib and bcrypt** before being stored.

FastAPI's OAuth2 password flow is integrated with Swagger UI so users can authenticate using the **Authorize** button.

## Rate Limiting

**SlowAPI** is used to prevent excessive requests to important endpoints.

Current limits include:

- Login requests: **5 per minute**
- Create requests: **20 per minute**
- General GET/list requests: **60 per minute**

Requests exceeding their limit receive:

```text
429 Too Many Requests
```

## CORS Protection

CORS middleware restricts browser-based access to the frontend applications expected to communicate with the API.

Allowed origins:

```text
http://localhost:8501
http://localhost:3000
```

These represent local development environments for **Streamlit** and **React**.

Allowed HTTP methods are restricted to:

```text
GET
POST
PUT
PATCH
DELETE
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

Invalid input is rejected before it reaches the database.

## Background Tasks

FastAPI background tasks handle work that does not need to finish before the API response is returned.

When a student is created:

- The activity is written to `activity_log.txt`.
- A simulated notification runs after a 2-second delay.
- The notification is written to `notification_log.txt`.
- The API response can return without waiting for the notification process.

When a student is deleted:

- The deletion is recorded in `activity_log.txt` in the background.

## Structured Error Handling

Custom exceptions and global exception handlers provide consistent API errors:

- `NotFoundException` — `404 Not Found`
- `DuplicateException` — `409 Conflict`
- `BadRequestException` — `400 Bad Request`
- Rate limit exceeded — `429 Too Many Requests`

The API also includes a business rule preventing enrolled students from being deleted. A student must first be updated to `is_enrolled: false`.

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

## Running the API

Install the required dependencies:

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

## Testing Authentication

1. Register a user using `/auth/register`.
2. Click **Authorize** in Swagger UI.
3. Enter the registered username and password.
4. Swagger authenticates through `/auth/login` and receives a JWT.
5. Test a protected endpoint such as `POST /students/`.
6. Log out and retry the endpoint to verify unauthorized requests are rejected.

## Testing Rate Limiting

The login endpoint allows a maximum of five requests per minute.

Calling `/auth/login` six times within one minute should produce:

```text
Request 1 → 200 OK
Request 2 → 200 OK
Request 3 → 200 OK
Request 4 → 200 OK
Request 5 → 200 OK
Request 6 → 429 Too Many Requests
```

This confirms that the API's rate limiting protection is working.

## Security Measures

The API currently includes several layers of protection:

```text
Request
   ↓
CORS Restrictions
   ↓
Rate Limiting
   ↓
Pydantic Input Validation
   ↓
JWT Authentication
   ↓
Business Rules
   ↓
Database Operations
   ↓
Response
   ↓
Background Tasks
```

Together these protections help control where browser requests originate, how frequently endpoints can be accessed, what data can enter the application, and who is allowed to modify protected resources.

## Purpose

This project demonstrates how a FastAPI application can be hardened beyond basic CRUD functionality. It provides practice with database persistence, validation, structured errors, password hashing, JWT authentication, OAuth2, protected routes, background processing, CORS configuration, and API rate limiting.