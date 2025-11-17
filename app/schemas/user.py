"""User schemas"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    email: Optional[str] = Field(None, description="Email address")


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=255, description="Password")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number"""
        if not v or len(v) < 10:
            raise ValueError('Invalid phone number')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    phone: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_admin: bool
    is_doctor: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None)


class PasswordChange(BaseModel):
    """Password change schema"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")


class TokenRefreshResponse(BaseModel):
    """Token refresh response schema"""
    access_token: str
    token_type: str = "bearer"
