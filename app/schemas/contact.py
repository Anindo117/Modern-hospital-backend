"""Contact message schemas"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class ContactMessageBase(BaseModel):
    """Base contact message schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    phone: Optional[str] = Field(None, max_length=20, description="Sender phone")
    subject: Optional[str] = Field(None, max_length=255, description="Message subject")
    message: str = Field(..., min_length=1, description="Message content")


class ContactMessageCreate(ContactMessageBase):
    """Contact message creation schema"""
    pass


class ContactMessageUpdate(BaseModel):
    """Contact message update schema"""
    status: Optional[str] = Field(None, description="Message status")


class ContactMessageResponse(ContactMessageBase):
    """Contact message response schema"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContactMessageListResponse(BaseModel):
    """Contact message list response"""
    total: int
    page: int
    page_size: int
    items: list[ContactMessageResponse]
