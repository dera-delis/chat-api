from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.room import Room, RoomMember
from app.models.invite import RoomInvite, RoomJoinRequest
from app.schemas.room import (
    RoomCreate,
    RoomResponse,
    RoomMemberResponse,
    RoomInviteRequest,
    RoomInviteResponse,
    RoomJoinRequestResponse,
)
from datetime import datetime, timedelta, timezone
import secrets
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


@router.get("/public", response_model=List[RoomResponse])
def get_public_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all public rooms"""
    rooms = db.query(Room).filter(Room.is_private == False).all()
    return rooms


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific room by ID"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
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


@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
def delete_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a room (creator only)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    if room.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the room creator can delete this room"
        )
    
    db.delete(room)
    db.commit()
    return {"message": "Room deleted"}


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


@router.post("/{room_id}/members", response_model=RoomMemberResponse, status_code=status.HTTP_201_CREATED)
def add_room_member(
    room_id: int,
    invite: RoomInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to a room by username or email (creator only for private rooms)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    if room.is_private and room.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the room creator can invite members to this private room"
        )

    if not invite.username and not invite.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide a username or email"
        )

    user_query = db.query(User)
    if invite.username:
        user_query = user_query.filter(User.username == invite.username)
    elif invite.email:
        user_query = user_query.filter(User.email == invite.email)

    target_user = user_query.first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == target_user.id
    ).first()
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this room"
        )

    membership = RoomMember(room_id=room_id, user_id=target_user.id)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/{room_id}/invites", response_model=RoomInviteResponse, status_code=status.HTTP_201_CREATED)
def create_room_invite(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a shareable invite link token (creator only for private rooms)."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room.is_private and room.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the room creator can create invites for this private room"
        )

    token = secrets.token_urlsafe(24)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    invite = RoomInvite(
        room_id=room_id,
        token=token,
        created_by=current_user.id,
        expires_at=expires_at,
        is_active=True,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return RoomInviteResponse(token=invite.token, room_id=room_id, expires_at=invite.expires_at)


@router.post("/invites/{token}/request", response_model=RoomJoinRequestResponse, status_code=status.HTTP_201_CREATED)
def request_join_by_invite(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request to join a private room using an invite token."""
    invite = db.query(RoomInvite).filter(RoomInvite.token == token, RoomInvite.is_active == True).first()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    if invite.expires_at and invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite has expired")

    room = db.query(Room).filter(Room.id == invite.room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    existing_membership = db.query(RoomMember).filter(
        RoomMember.room_id == room.id,
        RoomMember.user_id == current_user.id
    ).first()
    if existing_membership:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of this room")

    existing_request = db.query(RoomJoinRequest).filter(
        RoomJoinRequest.room_id == room.id,
        RoomJoinRequest.user_id == current_user.id
    ).first()
    if existing_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Join request already exists")

    join_request = RoomJoinRequest(
        room_id=room.id,
        user_id=current_user.id,
        status="pending",
    )
    db.add(join_request)
    db.commit()
    db.refresh(join_request)
    return RoomJoinRequestResponse(
        id=join_request.id,
        room_id=join_request.room_id,
        user_id=join_request.user_id,
        status=join_request.status,
        created_at=join_request.created_at,
        username=current_user.username,
    )


@router.get("/{room_id}/requests", response_model=List[RoomJoinRequestResponse])
def get_join_requests(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List pending join requests for a room (creator only)."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the room creator can view requests")

    requests = db.query(RoomJoinRequest, User.username).join(
        User, RoomJoinRequest.user_id == User.id
    ).filter(
        RoomJoinRequest.room_id == room_id,
        RoomJoinRequest.status == "pending",
    ).all()

    result = []
    for req, username in requests:
        result.append(RoomJoinRequestResponse(
            id=req.id,
            room_id=req.room_id,
            user_id=req.user_id,
            status=req.status,
            created_at=req.created_at,
            username=username,
        ))
    return result


@router.post("/{room_id}/requests/{request_id}/approve", response_model=RoomMemberResponse)
def approve_join_request(
    room_id: int,
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a join request (creator only)."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the room creator can approve requests")

    join_request = db.query(RoomJoinRequest).filter(
        RoomJoinRequest.id == request_id,
        RoomJoinRequest.room_id == room_id,
        RoomJoinRequest.status == "pending",
    ).first()
    if not join_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found")

    existing_membership = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == join_request.user_id
    ).first()
    if existing_membership:
        join_request.status = "approved"
        db.commit()
        return existing_membership

    membership = RoomMember(room_id=room_id, user_id=join_request.user_id)
    db.add(membership)
    join_request.status = "approved"
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/{room_id}/requests/{request_id}/reject", status_code=status.HTTP_200_OK)
def reject_join_request(
    room_id: int,
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a join request (creator only)."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the room creator can reject requests")

    join_request = db.query(RoomJoinRequest).filter(
        RoomJoinRequest.id == request_id,
        RoomJoinRequest.room_id == room_id,
        RoomJoinRequest.status == "pending",
    ).first()
    if not join_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Join request not found")

    join_request.status = "rejected"
    db.commit()
    return {"message": "Request rejected"}

