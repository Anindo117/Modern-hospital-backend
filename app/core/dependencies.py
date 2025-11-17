"""Dependency injection functions for FastAPI"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError

from app.core.security import TokenUtils, oauth2_scheme
from app.db.session import get_db


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db = Depends(get_db)):
    """Get current authenticated user from token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = TokenUtils.decode_token(token)
        user_id: int = int(payload.get("sub"))
        token_type: str = payload.get("type")
        
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except (ValueError, JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Import here to avoid circular import
    from app.crud.user import user as crud_user
    
    user = await crud_user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    
    return user


async def get_current_admin_user(current_user = Depends(get_current_user)):
    """Get current authenticated admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
