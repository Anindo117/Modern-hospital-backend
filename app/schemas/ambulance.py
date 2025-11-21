"""Ambulance Service schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AmbulanceServiceBase(BaseModel):
    """Base ambulance service schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    phone: str = Field(..., min_length=10, max_length=20)
    location: Optional[str] = Field(None, max_length=500)
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    available_24_7: bool = True
    ambulance_count: int = Field(1, ge=1)
    is_active: bool = True


class AmbulanceServiceCreate(AmbulanceServiceBase):
    """Ambulance service creation schema"""
    pass


class AmbulanceServiceUpdate(BaseModel):
    """Ambulance service update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    location: Optional[str] = Field(None, max_length=500)
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    available_24_7: Optional[bool] = None
    ambulance_count: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class AmbulanceServiceResponse(AmbulanceServiceBase):
    """Ambulance service response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
