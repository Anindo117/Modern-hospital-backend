"""User schemas"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    email: Optional[str] = Field(None, description="Email address")


class PatientProfileCreate(BaseModel):
    """Patient profile schema with Bangladeshi fields (all optional)"""
    nid: Optional[str] = Field(None, max_length=20, description="National ID")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, max_length=20, description="Gender (Male/Female/Other)")
    blood_group: Optional[str] = Field(None, max_length=10, description="Blood group (A+, A-, B+, B-, O+, O-, AB+, AB-)")
    division: Optional[str] = Field(None, max_length=100, description="Division (Dhaka, Chittagong, etc.)")
    district: Optional[str] = Field(None, max_length=100, description="District")
    upazila: Optional[str] = Field(None, max_length=100, description="Upazila")
    village: Optional[str] = Field(None, max_length=255, description="Village/Area")
    address: Optional[str] = Field(None, description="Full address")
    emergency_contact_name: Optional[str] = Field(None, max_length=255, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    
    @field_validator('nid', 'gender', 'blood_group', 'division', 'district', 'upazila', 'village', 'address', 'emergency_contact_name', 'emergency_contact_phone', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None"""
        if isinstance(v, str) and v.strip() == '':
            return None
        return v
    
    @field_validator('date_of_birth', mode='before')
    @classmethod
    def validate_date_of_birth(cls, v):
        """Convert empty strings to None for date fields"""
        if isinstance(v, str) and v.strip() == '':
            return None
        return v


class UserCreate(UserBase, PatientProfileCreate):
    """User creation schema"""
    password: str = Field(..., min_length=8, description="Password")
    
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
    
    @field_validator('password', mode='before')
    @classmethod
    def truncate_password(cls, v):
        """Truncate password to 72 bytes for bcrypt compatibility"""
        if isinstance(v, str):
            password_bytes = v.encode('utf-8')
            if len(password_bytes) > 72:
                # Truncate to 72 bytes
                v = password_bytes[:72].decode('utf-8', errors='ignore')
        return v


class UserResponse(UserBase, PatientProfileCreate):
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
