import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.room import Room, RoomMember
from app.models.message import Message
from app.utils.jwt import verify_token
from app.services.redis import redis_service
from app.services.presence import presence_service


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.connection_info: Dict[WebSocket, tuple[int, str, int]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int, username: str):
        self.active_connections.setdefault(room_id, set()).add(websocket)
        self.connection_info[websocket] = (user_id, username, room_id)
        await asyncio.to_thread(presence_service.set_user_online, room_id, user_id, username)
        await self.broadcast_system_message(
            room_id,
            f"{username} joined the room",
            exclude_websocket=websocket,
        )

    def disconnect(self, websocket: WebSocket):
        if websocket not in self.connection_info:
            return
        user_id, username, room_id = self.connection_info.pop(websocket)
        self.active_connections.get(room_id, set()).discard(websocket)
        if not self.active_connections.get(room_id):
            self.active_connections.pop(room_id, None)
        # Run in thread to avoid blocking the event loop
        asyncio.create_task(asyncio.to_thread(presence_service.set_user_offline, room_id, user_id))

    async def broadcast_to_room(self, room_id: int, message: dict, exclude_websocket: WebSocket | None = None):
        connections = self.active_connections.get(room_id, set())
        disconnected = set()
        for connection in connections:
            if connection == exclude_websocket:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_system_message(self, room_id: int, content: str, exclude_websocket: WebSocket | None = None):
        await self.broadcast_to_room(
            room_id,
            {"type": "system", "content": content, "timestamp": None},
            exclude_websocket=exclude_websocket,
        )


manager = ConnectionManager()


def get_user_from_token(token: str, db: Session) -> User:
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def websocket_chat_endpoint(websocket: WebSocket, room_id: int):
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    try:
        user = get_user_from_token(token, db)
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        membership = db.query(RoomMember).filter(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user.id,
        ).first()
        if not membership:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    finally:
        db.close()

    await manager.connect(websocket, room_id, user.id, user.username)

    pubsub = None
    redis_task = None
    try:
        pubsub = await asyncio.to_thread(redis_service.create_pubsub)
        await asyncio.to_thread(redis_service.subscribe_to_room, pubsub, room_id)

        await websocket.send_json({
            "type": "connected",
            "message": "Successfully connected to room",
            "room_id": room_id,
            "room_name": room.name,
            "username": user.username,
        })

        async def listen_redis():
            while True:
                message = await asyncio.to_thread(redis_service.get_message, pubsub, 0.1)
                if message:
                    await manager.broadcast_to_room(room_id, message, exclude_websocket=websocket)

        redis_task = asyncio.create_task(listen_redis())

        def save_message(room_id: int, user_id: int, content: str) -> dict:
            message_db = SessionLocal()
            try:
                db_message = Message(room_id=room_id, user_id=user_id, content=content)
                message_db.add(db_message)
                message_db.commit()
                message_db.refresh(db_message)
                return {"id": db_message.id, "timestamp": db_message.timestamp.isoformat()}
            finally:
                message_db.close()

        def edit_message(room_id: int, user_id: int, message_id: int, content: str) -> dict | None:
            message_db = SessionLocal()
            try:
                db_message = message_db.query(Message).filter(
                    Message.id == message_id,
                    Message.room_id == room_id,
                    Message.user_id == user_id,
                ).first()
                if not db_message:
                    return None
                db_message.content = content
                message_db.commit()
                message_db.refresh(db_message)
                return {"id": db_message.id, "timestamp": db_message.timestamp.isoformat()}
            finally:
                message_db.close()

        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "message" and "content" in data:
                content = data["content"].strip()
                if not content:
                    continue

                message_data = {
                    "type": "message",
                    "id": None,
                    "room_id": room_id,
                    "user_id": user.id,
                    "username": user.username,
                    "content": content,
                    "timestamp": None,
                    "edited": False,
                }
                saved = await asyncio.to_thread(save_message, room_id, user.id, content)
                message_data["id"] = saved["id"]
                message_data["timestamp"] = saved["timestamp"]

                await asyncio.to_thread(redis_service.publish_message, room_id, message_data)
                await manager.broadcast_to_room(room_id, message_data)
                continue

            if message_type == "typing" and "is_typing" in data:
                typing_data = {
                    "type": "typing",
                    "room_id": room_id,
                    "user_id": user.id,
                    "username": user.username,
                    "is_typing": bool(data.get("is_typing")),
                }
                await manager.broadcast_to_room(room_id, typing_data, exclude_websocket=websocket)
                continue

            if message_type == "edit" and "content" in data and "message_id" in data:
                content = data["content"].strip()
                if not content:
                    continue
                try:
                    message_id = int(data["message_id"])
                except (TypeError, ValueError):
                    continue

                updated = await asyncio.to_thread(edit_message, room_id, user.id, message_id, content)
                if not updated:
                    continue

                edit_data = {
                    "type": "edit",
                    "id": updated["id"],
                    "room_id": room_id,
                    "user_id": user.id,
                    "username": user.username,
                    "content": content,
                    "timestamp": updated["timestamp"],
                    "edited": True,
                }

                await asyncio.to_thread(redis_service.publish_message, room_id, edit_data)
                await manager.broadcast_to_room(room_id, edit_data)
                continue

    except WebSocketDisconnect:
        pass
    finally:
        if redis_task:
            redis_task.cancel()
        if pubsub:
            await asyncio.to_thread(redis_service.unsubscribe_from_room, pubsub, room_id)
            await asyncio.to_thread(redis_service.close_pubsub, pubsub)
        manager.disconnect(websocket)
        await manager.broadcast_system_message(room_id, f"{user.username} left the room")
