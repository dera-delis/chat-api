import pytest
from fastapi import status


def test_get_messages(client, auth_token):
    """Test getting messages from a room"""
    # Create a room
    room_response = client.post(
        "/rooms",
        json={
            "name": "Message Room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    room_id = room_response.json()["id"]
    
    # Get messages (should be empty initially)
    response = client.get(
        f"/rooms/{room_id}/messages",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_messages_pagination(client, auth_token):
    """Test paginated message retrieval"""
    # Create a room
    room_response = client.post(
        "/rooms",
        json={
            "name": "Pagination Room",
            "is_private": False
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    room_id = room_response.json()["id"]
    
    # Get messages with pagination
    response = client.get(
        f"/rooms/{room_id}/messages?skip=0&limit=10",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


def test_get_messages_not_member(client, auth_token):
    """Test getting messages from a room user is not a member of"""
    # Create a room
    room_response = client.post(
        "/rooms",
        json={
            "name": "Restricted Room",
            "is_private": True
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    room_id = room_response.json()["id"]
    
    # Create another user
    client.post(
        "/auth/signup",
        json={
            "username": "user4",
            "email": "user4@example.com",
            "password": "password123"
        }
    )
    login_response = client.post(
        "/auth/login",
        json={
            "username": "user4",
            "password": "password123",
        },
    )
    token4 = login_response.json()["access_token"]
    
    # Try to get messages (should fail)
    response = client.get(
        f"/rooms/{room_id}/messages",
        headers={"Authorization": f"Bearer {token4}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

