# Real-Time Chat API

Production-ready chat backend built with FastAPI, WebSockets, Redis, and PostgreSQL. It supports JWT auth, public/private rooms, invite links with approval, presence tracking, typing indicators, and message editing.

## Features
- JWT authentication (`/auth/signup`, `/auth/login`, `/auth/me`)
- Public and private rooms
- Invite links with join requests + approvals
- Real-time messaging via WebSockets
- Typing indicators and message editing
- Presence tracking per room
- PostgreSQL + SQLAlchemy + Alembic migrations
- Redis Pub/Sub for scalable broadcasts

## Tech Stack
- FastAPI
- PostgreSQL + SQLAlchemy + Alembic
- Redis (Pub/Sub + presence)
- JWT authentication
- Docker / Docker Compose

## Quick Start (Docker)
```bash
docker-compose up -d --build
```

The app runs on `http://localhost:8000`.  
Swagger docs: `http://localhost:8000/docs`

> Migrations are applied automatically on container start (`scripts/entrypoint.sh`).

## Local Development
```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

You will need local PostgreSQL + Redis, or run them via Docker.

## API Endpoints (Summary)

### Auth
- `POST /auth/signup`
- `POST /auth/login` (JSON: username/email + password)
- `POST /auth/token` (OAuth2 form)
- `GET /auth/me`

### Rooms
- `GET /rooms` (rooms you belong to)
- `GET /rooms/public`
- `POST /rooms` (create room, supports `is_private`)
- `GET /rooms/{room_id}`
- `POST /rooms/{room_id}/join` (public only)
- `POST /rooms/{room_id}/leave`
- `DELETE /rooms/{room_id}` (creator only)
- `GET /rooms/{room_id}/members`
- `POST /rooms/{room_id}/members` (invite by username/email)

### Private Room Invites (Approval Flow)
- `POST /rooms/{room_id}/invites` → returns invite token
- `POST /rooms/invites/{token}/request` → create join request
- `GET /rooms/{room_id}/requests` → list pending requests (creator only)
- `POST /rooms/{room_id}/requests/{request_id}/approve`
- `POST /rooms/{room_id}/requests/{request_id}/reject`

### Messages
- `GET /rooms/{room_id}/messages?skip=0&limit=50`

### Presence
- `GET /presence/{room_id}`

## WebSocket
Connect:
```
ws://localhost:8000/ws/chat/{room_id}?token={JWT}
```

Message types:
```json
{ "type": "message", "content": "Hello" }
{ "type": "edit", "message_id": 123, "content": "Updated" }
{ "type": "typing", "is_typing": true }
```

Broadcast events:
```json
{ "type": "message", "id": 1, "room_id": 1, "user_id": 2, "username": "alex", "content": "Hi", "timestamp": "..." }
{ "type": "edit", "id": 1, "room_id": 1, "user_id": 2, "username": "alex", "content": "Updated", "timestamp": "...", "edited": true }
{ "type": "typing", "room_id": 1, "user_id": 2, "username": "alex", "is_typing": true }
{ "type": "connected", "message": "Successfully connected to room", "room_id": 1, "room_name": "General", "username": "alex" }
```

## Project Structure
```
chat-api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── message.py
│   │   └── invite.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── rooms.py
│   │   ├── messages.py
│   │   └── presence.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── room.py
│   │   └── message.py
│   ├── services/
│   │   ├── redis.py
│   │   └── presence.py
│   └── websocket/
│       └── chat.py
├── alembic/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Tests
```bash
pytest
```

## Environment Variables
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## License
MIT

