from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    content: str
    timestamp: datetime
    username: Optional[str] = None
    
    class Config:
        from_attributes = True

