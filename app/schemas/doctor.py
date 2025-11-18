"""Doctor schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBasic(BaseModel):
    """Basic user info for doctor response"""
    id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


class DoctorBase(BaseModel):
    """Base doctor schema"""
    specialty: str = Field(..., min_length=1, max_length=255, description="Medical specialty")
    image_url: Optional[str] = Field(None, description="Doctor image URL")
    bio: Optional[str] = Field(None, description="Doctor biography")
    experience_years: Optional[int] = Field(None, ge=0, description="Years of experience")
    department_id: int = Field(..., description="Department ID")


class DoctorCreate(DoctorBase):
    """Doctor creation schema"""
    user_id: int = Field(..., description="User ID")


class DoctorUpdate(BaseModel):
    """Doctor update schema"""
    specialty: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None)
    bio: Optional[str] = Field(None)
    experience_years: Optional[int] = Field(None, ge=0)
    department_id: Optional[int] = Field(None)
    is_available: Optional[bool] = Field(None)


class DoctorResponse(DoctorBase):
    """Doctor response schema"""
    id: int
    user_id: int
    user: UserBasic
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DoctorDetailResponse(DoctorResponse):
    """Doctor detail response with user info"""
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    user_email: Optional[str] = None
    department_name: Optional[str] = None
    appointments_count: int = 0
