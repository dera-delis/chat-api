import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.room import Room, RoomMember
from app.models.message import Message
from app.utils.jwt import verify_token
from app.services.redis import redis_service
from app.services.presence import presence_service


class ConnectionManager:
    """Manages WebSocket connections for chat rooms"""
    
    def __init__(self):
        # room_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # WebSocket -> (user_id, username, room_id)
        self.connection_info: Dict[WebSocket, tuple] = {}
    
    async def connect(self, websocket: WebSocket, room_id: int, user_id: int, username: str):
        """Connect a user to a room"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        
        self.active_connections[room_id].add(websocket)
        self.connection_info[websocket] = (user_id, username, room_id)
        
        # Set user online
        presence_service.set_user_online(room_id, user_id, username)
        
        # Notify others in room
        await self.broadcast_system_message(
            room_id,
            f"{username} joined the room",
            exclude_websocket=websocket
        )
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user from a room"""
        if websocket not in self.connection_info:
            return
        
        user_id, username, room_id = self.connection_info[websocket]
        
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        del self.connection_info[websocket]
        
        # Set user offline
        presence_service.set_user_offline(room_id, user_id)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific WebSocket connection"""
        await websocket.send_json(message)
    
    async def broadcast_to_room(self, room_id: int, message: dict, exclude_websocket: WebSocket = None):
        """Broadcast message to all connections in a room"""
        if room_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[room_id]:
            if connection == exclude_websocket:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_system_message(self, room_id: int, content: str, exclude_websocket: WebSocket = None):
        """Broadcast a system message to the room"""
        message = {
            "type": "system",
            "content": content,
            "timestamp": None
        }
        await self.broadcast_to_room(room_id, message, exclude_websocket)


# Global connection manager
manager = ConnectionManager()


async def get_current_user_websocket(
    token: str,
    db: Session
) -> User:
    """Get current user from WebSocket token"""
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def websocket_chat_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str,
    db: Session
):
    """WebSocket endpoint for real-time chat"""
    # Authenticate user
    try:
        user = await get_current_user_websocket(token, db)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room not found")
        return
    
    # Check if user is a member
    membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == user.id
    ).first()
    
    if not membership:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Not a member of this room")
        return
    
    # Connect to room
    await manager.connect(websocket, room_id, user.id, user.username)
    
    # Subscribe to Redis pub/sub for this room
    pubsub = redis_service.create_pubsub()
    redis_service.subscribe_to_room(pubsub, room_id)
    
    try:
        # Start Redis message listener task
        async def listen_redis():
            while True:
                try:
                    message = redis_service.get_message(pubsub, timeout=0.1)
                    if message:
                        # Broadcast message received from Redis to all WebSocket connections
                        await manager.broadcast_to_room(room_id, message, exclude_websocket=websocket)
                except Exception as e:
                    print(f"Redis listener error: {e}")
                    break
        
        redis_task = asyncio.create_task(listen_redis())
        
        # Main message loop
        while True:
            try:
                # Receive message from WebSocket
                data = await websocket.receive_json()
                
                if data.get("type") == "message" and "content" in data:
                    content = data["content"].strip()
                    if not content:
                        continue
                    
                    # Save message to database
                    db_message = Message(
                        room_id=room_id,
                        user_id=user.id,
                        content=content
                    )
                    db.add(db_message)
                    db.commit()
                    db.refresh(db_message)
                    
                    # Prepare message for broadcasting
                    message_data = {
                        "type": "message",
                        "id": db_message.id,
                        "room_id": room_id,
                        "user_id": user.id,
                        "username": user.username,
                        "content": content,
                        "timestamp": db_message.timestamp.isoformat()
                    }
                    
                    # Publish to Redis for horizontal scaling
                    redis_service.publish_message(room_id, message_data)
                    
                    # Broadcast to all connections in this room (including sender)
                    await manager.broadcast_to_room(room_id, message_data)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
        
        # Cancel Redis listener
        redis_task.cancel()
        try:
            await redis_task
        except asyncio.CancelledError:
            pass
    
    finally:
        # Cleanup
        redis_service.unsubscribe_from_room(pubsub, room_id)
        redis_service.close_pubsub(pubsub)
        manager.disconnect(websocket)
        
        # Notify others that user left
        await manager.broadcast_system_message(
            room_id,
            f"{user.username} left the room"
        )

