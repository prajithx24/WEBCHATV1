from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from services.database import get_db
from middleware.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1", tags=["Users"])

class UserResponse(BaseModel):
    id: str
    username: str

class PublicKeyResponse(BaseModel):
    user_id: str
    username: str
    public_key: str

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all users (excluding current user).
    Requires authentication.
    """
    users = db.query(User).filter(User.id != current_user.id).all()
    return [UserResponse(id=user.id, username=user.username) for user in users]

@router.get("/keys/{user_id}", response_model=PublicKeyResponse)
async def get_public_key(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get public key for a specific user.
    Required for encrypting messages to that user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return PublicKeyResponse(
        user_id=user.id,
        username=user.username,
        public_key=user.public_key
    )