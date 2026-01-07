from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.room import Room, RoomMember
from app.schemas.room import RoomCreate, RoomResponse, RoomMemberResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat room"""
    # Check if room name already exists
    existing_room = db.query(Room).filter(Room.name == room_data.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room name already exists"
        )
    
    # Create room
    db_room = Room(
        name=room_data.name,
        description=room_data.description,
        is_private=room_data.is_private,
        created_by=current_user.id
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    # Add creator as member
    membership = RoomMember(room_id=db_room.id, user_id=current_user.id)
    db.add(membership)
    db.commit()
    
    return db_room


@router.get("", response_model=List[RoomResponse])
def get_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rooms the user is a member of"""
    rooms = db.query(Room).join(RoomMember).filter(
        RoomMember.user_id == current_user.id
    ).all()
    return rooms


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific room by ID"""
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if user is a member
    membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room"
        )
    
    return room


@router.post("/{room_id}/join", response_model=RoomMemberResponse, status_code=status.HTTP_201_CREATED)
def join_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a chat room"""
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if room is private
    if room.is_private:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot join private room. Invitation required."
        )
    
    # Check if already a member
    existing_membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this room"
        )
    
    # Add membership
    membership = RoomMember(room_id=room_id, user_id=current_user.id)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    return membership


@router.post("/{room_id}/leave", status_code=status.HTTP_200_OK)
def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a chat room"""
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if user is a member
    membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a member of this room"
        )
    
    # Remove membership
    db.delete(membership)
    db.commit()
    
    return {"message": "Successfully left the room"}


@router.get("/{room_id}/members", response_model=List[RoomMemberResponse])
def get_room_members(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of a room"""
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if user is a member
    membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this room"
        )
    
    # Get all members
    members = db.query(RoomMember).filter(RoomMember.room_id == room_id).all()
    return members

