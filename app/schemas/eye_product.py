"""Eye Product schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EyeProductBase(BaseModel):
    """Base eye product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=255)
    price: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)
    stock_quantity: int = Field(0, ge=0)
    is_available: bool = True
    is_active: bool = True


class EyeProductCreate(EyeProductBase):
    """Eye product creation schema"""
    pass


class EyeProductUpdate(BaseModel):
    """Eye product update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=255)
    price: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None


class EyeProductResponse(EyeProductBase):
    """Eye product response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
