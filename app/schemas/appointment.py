"""Appointment schemas"""

from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional
from app.core.constants import AppointmentStatus


class AppointmentBase(BaseModel):
    """Base appointment schema"""
    department_id: int = Field(..., description="Department ID")
    doctor_id: Optional[int] = Field(None, description="Doctor ID")
    appointment_date: date = Field(..., description="Appointment date")
    appointment_time: time = Field(..., description="Appointment time")
    notes: Optional[str] = Field(None, description="Additional notes")


class AppointmentCreate(AppointmentBase):
    """Appointment creation schema"""
    pass


class AppointmentUpdate(BaseModel):
    """Appointment update schema"""
    status: Optional[str] = Field(None, description="Appointment status")
    notes: Optional[str] = Field(None)
    appointment_date: Optional[date] = Field(None)
    appointment_time: Optional[time] = Field(None)


class AppointmentResponse(AppointmentBase):
    """Appointment response schema"""
    id: int
    patient_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentDetailResponse(AppointmentResponse):
    """Appointment detail response with related info"""
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_specialty: Optional[str] = None
    department_name: Optional[str] = None


class AppointmentListResponse(BaseModel):
    """Appointment list response"""
    total: int
    page: int
    page_size: int
    items: list[AppointmentResponse]
