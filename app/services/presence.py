import redis
from typing import Set
from app.config import settings
from app.services.redis import redis_service


class PresenceService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.presence_key_prefix = "presence:room:"
        self.user_key_prefix = "user:room:"
    
    def set_user_online(self, room_id: int, user_id: int, username: str):
        """Mark user as online in a room"""
        room_key = f"{self.presence_key_prefix}{room_id}"
        user_key = f"{self.user_key_prefix}{user_id}:room:{room_id}"
        
        # Add user to room's online set
        self.redis_client.sadd(room_key, user_id)
        # Store username mapping
        self.redis_client.set(user_key, username, ex=3600)  # Expire after 1 hour
    
    def set_user_offline(self, room_id: int, user_id: int):
        """Mark user as offline in a room"""
        room_key = f"{self.presence_key_prefix}{room_id}"
        user_key = f"{self.user_key_prefix}{user_id}:room:{room_id}"
        
        # Remove user from room's online set
        self.redis_client.srem(room_key, user_id)
        # Remove username mapping
        self.redis_client.delete(user_key)
    
    def get_online_users(self, room_id: int) -> list:
        """Get list of online users in a room"""
        room_key = f"{self.presence_key_prefix}{room_id}"
        user_ids = self.redis_client.smembers(room_key)
        
        online_users = []
        for user_id in user_ids:
            user_key = f"{self.user_key_prefix}{user_id}:room:{room_id}"
            username = self.redis_client.get(user_key)
            if username:
                online_users.append({
                    "user_id": int(user_id),
                    "username": username
                })
        
        return online_users
    
    def is_user_online(self, room_id: int, user_id: int) -> bool:
        """Check if user is online in a room"""
        room_key = f"{self.presence_key_prefix}{room_id}"
        return self.redis_client.sismember(room_key, user_id)


# Global presence service instance
presence_service = PresenceService()

