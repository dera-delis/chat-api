# Real-Time Chat API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-blue)
![Redis](https://img.shields.io/badge/Redis-Pub/Sub-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Status](https://img.shields.io/badge/Status-Portfolio_Project-green)

A production-ready real-time chat API built with FastAPI, WebSockets, Redis, and PostgreSQL. This backend supports authenticated users, multiple chat rooms, real-time messaging, and persistent chat history.

> ⚠️ **Status / Scope:** This project is designed as a backend-only service intended for integration with web or mobile clients.

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
│  │  - /rooms/* (CRUD operations)         │  │
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
  │                         │                         │                          │
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
│   │   └── message.py
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
├── .env.example
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Quick Start with Docker

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update the `SECRET_KEY` for production.

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**:
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - API Documentation (Swagger): http://localhost:8000/docs
   - Alternative Docs (ReDoc): http://localhost:8000/redoc

### Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis**:
   - Install PostgreSQL and Redis locally, or
   - Use Docker Compose to run only the database services:
     ```bash
     docker-compose up -d postgres redis
     ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   Update `DATABASE_URL` and `REDIS_URL` to point to your local instances.

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**:
   ```bash
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

**Response**: `201 Created`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "is_active": true
}
```

#### POST `/auth/login`
Login and receive JWT token.

**Request Body** (form data):
```
username: johndoe
password: securepassword123
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Rooms

#### POST `/rooms`
Create a new chat room.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "General Discussion",
  "description": "A room for general chat",
  "is_private": false
}
```

#### GET `/rooms`
Get all rooms the authenticated user is a member of.

**Headers**: `Authorization: Bearer <token>`

#### POST `/rooms/{room_id}/join`
Join a public room.

**Headers**: `Authorization: Bearer <token>`

#### POST `/rooms/{room_id}/leave`
Leave a room.

**Headers**: `Authorization: Bearer <token>`

### Messages

#### GET `/rooms/{room_id}/messages`
Get paginated chat history for a room.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `skip`: Number of messages to skip (default: 0)
- `limit`: Maximum number of messages to return (default: 50, max: 100)

**Example**: `/rooms/1/messages?skip=0&limit=20`

### Presence

#### GET `/presence/{room_id}`
Get list of online users in a room.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
[
  {
    "user_id": 1,
    "username": "johndoe"
  },
  {
    "user_id": 2,
    "username": "janedoe"
  }
]
```

## 🔌 WebSocket Usage

### Connection

Connect to a chat room using WebSocket:

```
ws://localhost:8000/ws/chat/{room_id}?token={JWT_TOKEN}
```

> **Note:** WebSocket connections require a valid JWT token passed as a query parameter. Unauthorized connections are rejected during handshake.

### Message Format

**Send Message**:
```json
{
  "type": "message",
  "content": "Hello, everyone!"
}
```

**Receive Message**:
```json
{
  "type": "message",
  "id": 123,
  "room_id": 1,
  "user_id": 1,
  "username": "johndoe",
  "content": "Hello, everyone!",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**System Message**:
```json
{
  "type": "system",
  "content": "johndoe joined the room",
  "timestamp": null
}
```

### Example WebSocket Client (JavaScript)

```javascript
const token = "your-jwt-token";
const roomId = 1;
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}?token=${token}`);

ws.onopen = () => {
  console.log("Connected to chat room");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received:", message);
  
  if (message.type === "message") {
    // Display chat message
    displayMessage(message);
  } else if (message.type === "system") {
    // Display system notification
    displaySystemMessage(message.content);
  }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Disconnected from chat room");
};

// Send a message
function sendMessage(content) {
  ws.send(JSON.stringify({
    type: "message",
    content: content
  }));
}
```

### Example WebSocket Client (Python)

```python
import asyncio
import websockets
import json

async def chat_client():
    token = "your-jwt-token"
    room_id = 1
    uri = f"ws://localhost:8000/ws/chat/{room_id}?token={token}"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to chat room")
        
        # Send a message
        message = {
            "type": "message",
            "content": "Hello from Python!"
        }
        await websocket.send(json.dumps(message))
        
        # Listen for messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

# Run the client
asyncio.run(chat_client())
```

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Coverage

- ✅ Authentication (signup, login, JWT validation)
- ✅ Room creation and management
- ✅ Message persistence and retrieval
- ✅ WebSocket authentication

## 🐳 Docker Services

The `docker-compose.yml` includes:

1. **PostgreSQL** (port 5432)
   - Database: `chat_db`
   - User: `chat_user`
   - Password: `chat_password`

2. **Redis** (port 6379)
   - Pub/Sub, presence tracking, room broadcasts

3. **FastAPI Application** (port 8000)
   - Auto-reloads on code changes
   - Runs database migrations on startup

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password storage
- **WebSocket Authentication**: Token validation on WebSocket connections
- **Room Access Control**: Users can only access rooms they're members of
- **Private Rooms**: Invite-only room support

## 📈 Scalability

- **Horizontal Scaling**: Redis Pub/Sub allows multiple FastAPI instances to share messages
- **Connection Management**: Efficient WebSocket connection handling
- **Database Indexing**: Optimized queries with proper indexes
- **Presence Tracking**: Redis-based presence for real-time status

## 🔄 Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## 📝 Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## 🚧 Future Enhancements

- [ ] Private room invitations
- [ ] Message reactions and editing
- [ ] File attachments
- [ ] Typing indicators
- [ ] Message search
- [ ] User profiles and avatars
- [ ] Rate limiting
- [ ] Message encryption

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🎯 Why This Project?

This project demonstrates:
- **Real-time system design** - WebSocket-based bidirectional communication
- **WebSocket authentication** - Secure token-based authentication for real-time connections
- **Redis-based horizontal scaling** - Pub/Sub architecture for multi-instance deployments
- **Clean FastAPI architecture** - Modular, maintainable code structure
- **Production-ready backend practices** - Docker, migrations, testing, and comprehensive documentation

---

**Built with ❤️ using FastAPI, WebSockets, Redis, and PostgreSQL**

