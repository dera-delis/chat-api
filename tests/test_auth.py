import pytest
from fastapi import status


def test_signup_success(client):
    """Test successful user signup"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data


def test_signup_duplicate_username(client, test_user):
    """Test signup with duplicate username"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]


def test_signup_duplicate_email(client, test_user):
    """Test signup with duplicate email"""
    response = client.post(
        "/auth/signup",
        json={
            "username": "differentuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_username(client):
    """Test login with invalid username"""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_invalid_password(client, test_user):
    """Test login with invalid password"""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

