import pytest
from fastapi import status


def test_create_room(client, auth_token):
    """Test creating a room"""
    response = client.post(
        "/rooms",
        json={
            "name": "Test Room",
            "description": "A test room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Room"
    assert data["description"] == "A test room"
    assert data["is_private"] == False
    assert "id" in data


def test_create_room_unauthorized(client):
    """Test creating a room without authentication"""
    response = client.post(
        "/rooms",
        json={
            "name": "Test Room",
            "description": "A test room",
            "is_private": False
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_duplicate_room(client, auth_token):
    """Test creating a room with duplicate name"""
    # Create first room
    client.post(
        "/rooms",
        json={
            "name": "Duplicate Room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Try to create duplicate
    response = client.post(
        "/rooms",
        json={
            "name": "Duplicate Room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_rooms(client, auth_token):
    """Test getting user's rooms"""
    # Create a room
    client.post(
        "/rooms",
        json={
            "name": "My Room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get rooms
    response = client.get(
        "/rooms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(room["name"] == "My Room" for room in data)


def test_join_room(client, auth_token, test_user):
    """Test joining a public room"""
    # Create a room
    room_response = client.post(
        "/rooms",
        json={
            "name": "Public Room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    room_id = room_response.json()["id"]
    
    # Create another user and join
    client.post(
        "/auth/signup",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123"
        }
    )
    login_response = client.post(
        "/auth/login",
        data={
            "username": "user2",
            "password": "password123"
        }
    )
    token2 = login_response.json()["access_token"]
    
    # Join room
    response = client.post(
        f"/rooms/{room_id}/join",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_join_private_room(client, auth_token):
    """Test joining a private room (should fail)"""
    # Create a private room
    room_response = client.post(
        "/rooms",
        json={
            "name": "Private Room",
            "is_private": True
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    room_id = room_response.json()["id"]
    
    # Create another user and try to join
    client.post(
        "/auth/signup",
        json={
            "username": "user3",
            "email": "user3@example.com",
            "password": "password123"
        }
    )
    login_response = client.post(
        "/auth/login",
        data={
            "username": "user3",
            "password": "password123"
        }
    )
    token3 = login_response.json()["access_token"]
    
    # Try to join private room
    response = client.post(
        f"/rooms/{room_id}/join",
        headers={"Authorization": f"Bearer {token3}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_leave_room(client, auth_token):
    """Test leaving a room"""
    # Create a room
    room_response = client.post(
        "/rooms",
        json={
            "name": "Leave Room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    room_id = room_response.json()["id"]
    
    # Leave room
    response = client.post(
        f"/rooms/{room_id}/leave",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

