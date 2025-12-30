# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### 1. Start Services with Docker

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- FastAPI app on port 8000

### 2. Run Database Migrations

```bash
docker-compose exec app alembic upgrade head
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 Example Usage

### 1. Create a User

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "password123"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=password123"
```

Save the `access_token` from the response.

### 3. Create a Room

```bash
curl -X POST "http://localhost:8000/rooms" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "General Chat",
    "description": "A general discussion room",
    "is_private": false
  }'
```

Save the `id` from the response (this is your `room_id`).

### 4. Connect via WebSocket

Use a WebSocket client or browser console:

```javascript
const token = "YOUR_TOKEN_HERE";
const roomId = 1; // Your room ID
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}?token=${token}`);

ws.onopen = () => console.log("Connected!");
ws.onmessage = (event) => console.log("Message:", JSON.parse(event.data));

// Send a message
ws.send(JSON.stringify({
  type: "message",
  content: "Hello, world!"
}));
```

## 🧪 Run Tests

```bash
# Run all tests
docker-compose exec app pytest

# Run with coverage
docker-compose exec app pytest --cov=app
```

## 🛑 Stop Services

```bash
docker-compose down
```

To also remove volumes (clears database):

```bash
docker-compose down -v
```

