"""
Tests for Student API CRUD endpoints.
"""


# ============================================================
# CREATE
# ============================================================

def test_create_student_success(
    client,
    auth_headers,
):
    response = client.post(
        "/students/",
        headers=auth_headers,
        json={
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "grade_level": 11,
            "gpa": 3.8,
            "is_enrolled": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Alice Johnson"
    assert data["email"] == "alice@example.com"
    assert data["grade_level"] == 11
    assert data["gpa"] == 3.8
    assert data["is_enrolled"] is True
    assert "id" in data
    assert "created_at" in data


# ============================================================
# VALIDATION
# ============================================================

def test_create_student_invalid_grade(
    client,
    auth_headers,
):
    response = client.post(
        "/students/",
        headers=auth_headers,
        json={
            "name": "Invalid Grade",
            "email": "grade@example.com",
            "grade_level": 15,
            "gpa": 3.0,
            "is_enrolled": True,
        },
    )

    assert response.status_code == 422


def test_create_student_invalid_gpa(
    client,
    auth_headers,
):
    response = client.post(
        "/students/",
        headers=auth_headers,
        json={
            "name": "Invalid GPA",
            "email": "gpa@example.com",
            "grade_level": 10,
            "gpa": 5.0,
            "is_enrolled": True,
        },
    )

    assert response.status_code == 422


# ============================================================
# LIST
# ============================================================

def test_list_students_empty(client):
    response = client.get(
        "/students/"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_students_with_data(
    client,
    sample_student,
):
    response = client.get(
        "/students/"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == sample_student["id"]
    assert data[0]["name"] == "Test Student"


# ============================================================
# GET BY ID
# ============================================================

def test_get_student_found(
    client,
    sample_student,
):
    student_id = sample_student["id"]

    response = client.get(
        f"/students/{student_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == student_id
    assert data["name"] == "Test Student"


def test_get_student_not_found(client):
    response = client.get(
        "/students/99999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == "not_found"


# ============================================================
# UPDATE
# ============================================================

def test_patch_student_success(
    client,
    auth_headers,
    sample_student,
):
    student_id = sample_student["id"]

    response = client.patch(
        f"/students/{student_id}",
        headers=auth_headers,
        json={
            "gpa": 3.9,
            "grade_level": 11,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["gpa"] == 3.9
    assert data["grade_level"] == 11
    assert data["name"] == "Test Student"


def test_patch_student_not_found(
    client,
    auth_headers,
):
    response = client.patch(
        "/students/99999",
        headers=auth_headers,
        json={
            "gpa": 3.7,
        },
    )

    assert response.status_code == 404


# ============================================================
# DELETE
# ============================================================

def test_delete_student_success(
    client,
    auth_headers,
    sample_student,
):
    student_id = sample_student["id"]

    response = client.delete(
        f"/students/{student_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/students/{student_id}"
    )

    assert get_response.status_code == 404


def test_delete_student_not_found(
    client,
    auth_headers,
):
    response = client.delete(
        "/students/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404


# ============================================================
# AUTHENTICATION
# ============================================================

def test_create_student_without_token(
    client,
):
    response = client.post(
        "/students/",
        json={
            "name": "Unauthorized Student",
            "email": "unauthorized@example.com",
            "grade_level": 10,
            "gpa": 3.0,
            "is_enrolled": True,
        },
    )

    assert response.status_code == 401