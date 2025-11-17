"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    TokenRefreshResponse,
    PasswordChange,
)
from app.crud.user import user as crud_user
from app.core.security import (
    SecurityUtils,
    TokenUtils,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    ValidationException,
    AuthenticationException,
    ConflictException,
)
from app.core.constants import ErrorMessages, SuccessMessages

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with phone number and password
    
    - **phone**: Phone number (10-20 digits)
    - **password**: Password (min 8 characters with uppercase, lowercase, digit, special char)
    - **full_name**: Optional full name
    - **email**: Optional email address
    """
    # Validate phone number
    is_valid, message = SecurityUtils.validate_phone(user_in.phone)
    if not is_valid:
        raise ValidationException(detail=message)
    
    # Validate password strength
    is_valid, message = SecurityUtils.validate_password(user_in.password)
    if not is_valid:
        raise ValidationException(detail=message)
    
    # Check if user already exists
    existing_user = await crud_user.get_by_phone(db, user_in.phone)
    if existing_user:
        raise ConflictException(detail=ErrorMessages.USER_ALREADY_EXISTS)
    
    # Create user
    user = await crud_user.create(db, user_in)
    
    # Create tokens
    tokens = TokenUtils.create_tokens(user.id, user.phone)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse.from_orm(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with phone number and password
    
    - **phone**: Phone number
    - **password**: Password
    """
    # Authenticate user
    user = await crud_user.authenticate(db, credentials.phone, credentials.password)
    if not user:
        raise AuthenticationException(detail=ErrorMessages.INVALID_CREDENTIALS)
    
    if not user.is_active:
        raise AuthenticationException(detail="User account is inactive")
    
    # Create tokens
    tokens = TokenUtils.create_tokens(user.id, user.phone)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse.from_orm(user),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    try:
        payload = TokenUtils.decode_token(request.refresh_token)
        token_type = payload.get("type")
        
        if token_type != "refresh":
            raise AuthenticationException(detail="Invalid token type")
        
        user_id = int(payload.get("sub"))
        user = await crud_user.get(db, user_id)
        
        if not user or not user.is_active:
            raise AuthenticationException(detail="User not found or inactive")
        
        # Create new access token
        access_token = TokenUtils.create_access_token(
            data={"sub": str(user.id), "phone": user.phone}
        )
        
        return TokenRefreshResponse(
            access_token=access_token,
            token_type="bearer",
        )
    except Exception as e:
        raise AuthenticationException(detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    
    - **old_password**: Current password
    - **new_password**: New password
    - **confirm_password**: Confirm new password
    """
    # Validate passwords match
    if password_change.new_password != password_change.confirm_password:
        raise ValidationException(detail="New passwords do not match")
    
    # Validate new password strength
    is_valid, message = SecurityUtils.validate_password(password_change.new_password)
    if not is_valid:
        raise ValidationException(detail=message)
    
    # Change password
    success = await crud_user.change_password(
        db,
        current_user,
        password_change.old_password,
        password_change.new_password
    )
    
    if not success:
        raise AuthenticationException(detail="Invalid current password")
    
    return {"message": SuccessMessages.PASSWORD_CHANGED}


@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout user (client should discard tokens)"""
    return {"message": SuccessMessages.LOGOUT_SUCCESS}
