"""Service schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ServiceBase(BaseModel):
    """Base service schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    icon: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    """Service creation schema"""
    pass


class ServiceUpdate(BaseModel):
    """Service update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    icon: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    """Service response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
