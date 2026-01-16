# Real-Time Chat API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-blue)
![Redis](https://img.shields.io/badge/Redis-Pub/Sub-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Status](https://img.shields.io/badge/Status-Portfolio_Project-green)

A production-ready real-time chat API built with FastAPI, WebSockets, Redis, and PostgreSQL. This backend supports authenticated users, public and private chat rooms, invite links with approval, real-time messaging, presence tracking, typing indicators, and persistent chat history.

[![Live Deployment](https://img.shields.io/badge/Live%20Deployment-Open-2ea44f?style=for-the-badge)](https://p01--chat-api--jlcf9gxkjgjx.code.run/)

## 🏗️ Architecture

### Tech Stack
- **FastAPI** - Modern, fast web framework for building APIs
- **WebSockets** - Real-time bidirectional communication
- **PostgreSQL** - Relational database for persistent storage
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **Redis** - Pub/Sub for horizontal scaling and presence tracking
- **JWT** - Token-based authentication
- **Docker** - Containerization and orchestration
- **pytest** - Testing framework

### System Architecture
```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       │
┌──────▼─────────────────────────────────────┐
│         FastAPI Application                 │
│  ┌──────────────────────────────────────┐  │
│  │  REST Endpoints                       │  │
│  │  - /auth/* (signup, login)            │  │
│  │  - /rooms/* (rooms, invites)          │  │
│  │  - /rooms/{id}/messages (history)     │  │
│  │  - /presence/{id} (online users)      │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  WebSocket Endpoint                   │  │
│  │  /ws/chat/{room_id}?token=JWT         │  │
│  └──────────────────────────────────────┘  │
└──────┬──────────────────┬──────────────────┘
       │                  │
       │                  │
┌──────▼──────┐    ┌──────▼──────┐
│ PostgreSQL  │    │    Redis     │
│  (Messages, │    │  (Pub/Sub,   │
│   Rooms,    │    │   Presence)  │
│   Users)    │    │              │
└─────────────┘    └──────────────┘
```

### WebSocket Flow Diagram
```
Client                    FastAPI                    Redis                    PostgreSQL
  │                         │                         │                          │
  │───WS Connect───────────>│                         │                          │
  │  (with JWT token)       │                         │                          │
  │                         │───Verify Token──────────│                          │
  │                         │                         │                          │
  │                         │───Check Membership─────>│                          │
  │                         │                         │                          │
  │                         │<──User Valid────────────│                          │
  │                         │                         │                          │
  │<──Connection Accepted───│                         │                          │
  │                         │                         │                          │
  │                         │───Subscribe────────────>│                          │
  │                         │  (room:{id})            │                          │
  │                         │                         │                          │
  │───Send Message─────────>│                         │                          │
  │  {"type": "message",    │                         │                          │
  │   "content": "..."}     │                         │                          │
  │                         │                         │                          │
  │                         │───Save Message─────────>│                          │
  │                         │                         │                          │
  │                         │<──Message Saved─────────│                          │
  │                         │                         │                          │
  │                         │───Publish───────────────>│                          │
  │                         │  (room:{id})            │                          │
  │                         │                         │                          │
  │                         │<──Broadcast─────────────│                          │
  │                         │                         │                          │
  │<──Message Broadcast─────│                         │                          │
```

## 📁 Project Structure
```
chat-api/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── message.py
│   │   └── invite.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── room.py
│   │   └── message.py
│   ├── routers/                # API route handlers
│   │   ├── auth.py
│   │   ├── rooms.py
│   │   ├── messages.py
│   │   └── presence.py
│   ├── websocket/              # WebSocket handlers
│   │   └── chat.py
│   ├── services/               # Business logic services
│   │   ├── redis.py
│   │   └── presence.py
│   └── utils/                  # Utility functions
│       └── jwt.py
├── tests/                      # Test suite
│   ├── test_auth.py
│   ├── test_rooms.py
│   ├── test_messages.py
│   └── test_websocket.py
├── alembic/                    # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Quick Start with Docker
```bash
docker-compose up -d --build
```

The app runs on `http://localhost:8000`.  
Swagger docs: `http://localhost:8000/docs`

> Migrations are applied automatically on container start (`scripts/entrypoint.sh`).

### Local Development
```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## 📡 API Endpoints

### Authentication
#### POST `/auth/signup`
Create a new user account.

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### POST `/auth/login`
Login and receive JWT token.

**Request Body** (JSON):
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/auth/me`
Get the current authenticated user.

### Rooms
#### POST `/rooms`
Create a new chat room.

**Request Body**:
```json
{
  "name": "General Discussion",
  "description": "A room for general chat",
  "is_private": false
}
```

#### GET `/rooms`
Get rooms the user is a member of.

#### GET `/rooms/public`
Get all public rooms.

#### POST `/rooms/{room_id}/join`
Join a public room.

#### POST `/rooms/{room_id}/leave`
Leave a room.

#### DELETE `/rooms/{room_id}`
Delete a room (creator only).

#### Private Room Invites (Approval Flow)
- `POST /rooms/{room_id}/invites` → returns invite token
- `POST /rooms/invites/{token}/request` → create join request
- `GET /rooms/{room_id}/requests` → list pending requests (creator only)
- `POST /rooms/{room_id}/requests/{request_id}/approve`
- `POST /rooms/{room_id}/requests/{request_id}/reject`

### Messages
#### GET `/rooms/{room_id}/messages`
Get paginated chat history for a room.

**Query Parameters**:
- `skip`: Number of messages to skip (default: 0)
- `limit`: Maximum number of messages to return (default: 50, max: 100)

### Presence
#### GET `/presence/{room_id}`
Get list of online users in a room.

## 🔌 WebSocket Usage

### Connection
```
ws://localhost:8000/ws/chat/{room_id}?token={JWT_TOKEN}
```

### Message Types (Client → Server)
```json
{ "type": "message", "content": "Hello, everyone!" }
{ "type": "edit", "message_id": 123, "content": "Updated message" }
{ "type": "typing", "is_typing": true }
```

### Message Types (Server → Client)
```json
{ "type": "message", "id": 123, "room_id": 1, "user_id": 1, "username": "johndoe", "content": "Hello", "timestamp": "2024-01-15T10:30:00Z" }
{ "type": "edit", "id": 123, "room_id": 1, "user_id": 1, "username": "johndoe", "content": "Updated message", "timestamp": "2024-01-15T10:31:00Z", "edited": true }
{ "type": "typing", "room_id": 1, "user_id": 1, "username": "johndoe", "is_typing": true }
{ "type": "connected", "message": "Successfully connected to room", "room_id": 1, "room_name": "General", "username": "johndoe" }
```

## 🧪 Testing
```bash
pytest
```

## 🚀 Deployment
This API is designed for container-based platforms.  
Primary target: **Northflank**, with Redis hosted on **Upstash**.

See `DEPLOYMENT.md` for the full guide and production notes.

## 📈 Scalability
Redis Pub/Sub allows multiple FastAPI instances to broadcast messages across nodes.

## 🐳 Docker Services
The `docker-compose.yml` includes:
- **PostgreSQL** (port 5432)
- **Redis** (port 6379)
- **FastAPI Application** (port 8000)

## 🔄 Database Migrations
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
alembic downgrade -1
```

## 🔗 Frontend Integration
This API is designed to be consumed by a React + WebSocket frontend application.
See: Project 6 – Real-Time Chat App

## 🎯 Why This Project?
This project demonstrates:
- Real-time system design with WebSockets
- Secure, token-authenticated socket connections
- Horizontal scalability using Redis Pub/Sub
- Complex domain logic (invites, approvals, presence)
- Production-ready backend architecture

## 📝 Environment Variables
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## 📄 License
MIT

## 📬 Contact
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/dera-delis)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?style=for-the-badge&logo=github)](https://github.com/dera-delis)

