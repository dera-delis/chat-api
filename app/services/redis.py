import redis
import json
from typing import Optional
from app.config import settings


class RedisService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def publish_message(self, room_id: int, message: dict):
        """Publish message to Redis channel for a room"""
        channel = f"room:{room_id}"
        self.redis_client.publish(channel, json.dumps(message))
    
    def create_pubsub(self):
        """Create a new pubsub instance for a connection"""
        return self.redis_client.pubsub()
    
    def subscribe_to_room(self, pubsub, room_id: int):
        """Subscribe to Redis channel for a room"""
        channel = f"room:{room_id}"
        pubsub.subscribe(channel)
    
    def unsubscribe_from_room(self, pubsub, room_id: int):
        """Unsubscribe from Redis channel for a room"""
        channel = f"room:{room_id}"
        pubsub.unsubscribe(channel)
    
    def get_message(self, pubsub, timeout: float = 1.0) -> Optional[dict]:
        """Get message from subscribed channels"""
        message = pubsub.get_message(timeout=timeout)
        if message and message["type"] == "message":
            return json.loads(message["data"])
        return None
    
    def close_pubsub(self, pubsub):
        """Close a pubsub instance"""
        pubsub.close()
    
    def close(self):
        """Close Redis connection"""
        self.redis_client.close()


# Global Redis service instance
redis_service = RedisService()

