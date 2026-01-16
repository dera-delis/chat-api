from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False


class RoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_private: bool
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoomMemberResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    joined_at: datetime
    
    class Config:
        from_attributes = True


class RoomInviteRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class RoomInviteResponse(BaseModel):
    token: str
    room_id: int
    expires_at: Optional[datetime] = None


class RoomJoinRequestResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    status: str
    created_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True

