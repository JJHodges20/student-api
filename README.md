# Secure Student CRUD API

A database-backed REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite** for managing student records.

This project demonstrates a complete CRUD application with JWT authentication, structured error handling, and background task processing.

## Features

### Student Management

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/students/` | Protected | Create a new student |
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

Protected endpoints require a valid JWT Bearer token.

## Background Tasks

FastAPI background tasks are used for work that does not need to finish before the API sends its response.

When a student is created:

- The activity is written to `activity_log.txt`.
- A simulated notification is sent after a 2-second delay.
- The notification is written to `notification_log.txt`.
- The API response is returned without waiting for the notification to finish.

When a student is deleted:

- The deletion is recorded in `activity_log.txt` in the background.

Example activity log:

```text
[2026-09-01T10:42:15] User 1: Created student 4 (Diana Prince)
[2026-09-01T10:45:32] User 1: Deleted student 4 (Diana Prince)
```

Example notification log:

```text
[2026-09-01T10:42:17] To: diana@example.com | Message: Student record created successfully for Diana Prince.
```

## Security

Passwords are hashed using **Passlib and bcrypt** before being stored in the database.

After a successful login, the API generates a **JWT access token** using `python-jose`. Protected routes use the token to identify the authenticated user.

FastAPI's OAuth2 password flow is also integrated with Swagger UI, allowing protected endpoints to be tested using the **Authorize** button.

## Structured Error Handling

Custom exceptions and global exception handlers provide consistent API error responses:

- `NotFoundException` — `404 Not Found`
- `DuplicateException` — `409 Conflict`
- `BadRequestException` — `400 Bad Request`

The API also includes business logic preventing an enrolled student from being deleted. The student must first be updated to `is_enrolled: false`.

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

## Running the API

Install the dependencies:

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

## Testing Authentication

1. Register a user with `/auth/register`.
2. Click **Authorize** in Swagger.
3. Enter the registered username and password.
4. Swagger logs in through `/auth/login` and receives a JWT.
5. Test a protected student endpoint.
6. Log out and retry the endpoint to confirm unauthorized requests are rejected.

## Background Task Flow

```text
POST /students
      ↓
Student saved to database
      ↓
API returns 201 Created
      ↓
Background Tasks
├── Log activity
└── Wait 2 seconds → Write notification


DELETE /students/{id}
      ↓
Student deleted
      ↓
API returns 204 No Content
      ↓
Background Task
└── Log deletion activity
```

## Purpose

This project demonstrates how several common backend API concepts work together in FastAPI, including persistent database storage, CRUD operations, validation, structured errors, password hashing, JWT authentication, protected routes, and post-response background processing.