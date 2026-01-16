# Real-Time Chat API

FastAPI + WebSockets chat backend with PostgreSQL, Redis, JWT auth, rooms, invites, and real-time messaging.

## Run (Docker)
```bash
docker-compose up -d --build
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

## Core Endpoints
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `GET /rooms`
- `GET /rooms/public`
- `POST /rooms`
- `GET /rooms/{room_id}`
- `POST /rooms/{room_id}/join`
- `POST /rooms/{room_id}/leave`
- `DELETE /rooms/{room_id}`
- `GET /rooms/{room_id}/messages`
- `GET /presence/{room_id}`

## Private Room Invites
- `POST /rooms/{room_id}/invites`
- `POST /rooms/invites/{token}/request`
- `GET /rooms/{room_id}/requests`
- `POST /rooms/{room_id}/requests/{request_id}/approve`
- `POST /rooms/{room_id}/requests/{request_id}/reject`

## WebSocket
```
ws://localhost:8000/ws/chat/{room_id}?token={JWT}
```

