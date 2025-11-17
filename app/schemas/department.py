"""Department schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DepartmentBase(BaseModel):
    """Base department schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Department name")
    description: Optional[str] = Field(None, description="Department description")
    image_url: Optional[str] = Field(None, description="Department image URL")


class DepartmentCreate(DepartmentBase):
    """Department creation schema"""
    pass


class DepartmentUpdate(BaseModel):
    """Department update schema"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)
    image_url: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


class DepartmentResponse(DepartmentBase):
    """Department response schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DepartmentDetailResponse(DepartmentResponse):
    """Department detail response with doctors count"""
    doctors_count: int = 0
