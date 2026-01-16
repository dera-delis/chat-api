from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.room import Room, RoomMember
from app.models.message import Message
from app.schemas.message import MessageResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/rooms", tags=["messages"])


@router.get("/{room_id}/messages", response_model=List[MessageResponse])
def get_messages(
    room_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated chat history for a room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room",
        )

    messages = db.query(Message, User.username).join(
        User, Message.user_id == User.id
    ).filter(
        Message.room_id == room_id
    ).order_by(
        Message.timestamp.desc()
    ).offset(skip).limit(limit).all()

    result = []
    for message, username in messages:
        result.append(MessageResponse(
            id=message.id,
            room_id=message.room_id,
            user_id=message.user_id,
            content=message.content,
            timestamp=message.timestamp,
            username=username,
        ))

    return list(reversed(result))
