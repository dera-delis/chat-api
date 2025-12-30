#!/usr/bin/env python3
"""Quick test script for the chat API"""
import httpx
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        return response.status_code == 200

def test_signup():
    """Test user signup"""
    print("Testing /auth/signup...")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/auth/signup", json=data)
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}\n")
        except:
            print(f"Response: {response.text}\n")
        return response.status_code in [201, 400]  # 400 if user already exists

def test_login():
    """Test user login"""
    print("Testing /auth/login...")
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/auth/login", data=data)
        print(f"Status: {response.status_code}")
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}\n")
            return result.get("access_token")
        except:
            print(f"Response: {response.text}\n")
            return None

def test_create_room(token):
    """Test room creation"""
    print("Testing POST /rooms...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Room",
        "description": "A test room",
        "is_private": False
    }
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/rooms", json=data, headers=headers)
        print(f"Status: {response.status_code}")
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}\n")
            return result.get("id")
        except:
            print(f"Response: {response.text}\n")
            return None

def test_get_rooms(token):
    """Test getting rooms"""
    print("Testing GET /rooms...")
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/rooms", headers=headers)
        print(f"Status: {response.status_code}")
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}\n")
        except:
            print(f"Response: {response.text}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Chat API Test Suite")
    print("=" * 50 + "\n")
    
    # Test health
    if not test_health():
        print("Health check failed!")
        exit(1)
    
    # Test signup
    test_signup()
    
    # Test login
    token = test_login()
    if not token:
        print("Login failed! Cannot continue with authenticated tests.")
        exit(1)
    
    # Test room creation
    room_id = test_create_room(token)
    
    # Test getting rooms
    test_get_rooms(token)
    
    print("=" * 50)
    print("Tests completed!")
    print("=" * 50)

