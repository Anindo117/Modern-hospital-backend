"""Appointment CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date
from typing import Optional

from app.db.models import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from .base import CRUDBase


class CRUDAppointment(CRUDBase[Appointment, AppointmentCreate, AppointmentUpdate]):
    """Appointment CRUD operations"""
    
    async def create(self, db: AsyncSession, obj_in: AppointmentCreate, patient_id: Optional[int] = None) -> Appointment:
        """Create new appointment with optional patient_id override"""
        obj_data = obj_in.dict()
        if patient_id is not None:
            obj_data["patient_id"] = patient_id
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_patient(self, db: AsyncSession, patient_id: int, skip: int = 0, limit: int = 100):
        """Get appointments by patient"""
        result = await db.execute(
            select(Appointment)
            .where(Appointment.patient_id == patient_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_doctor(self, db: AsyncSession, doctor_id: int, skip: int = 0, limit: int = 100):
        """Get appointments by doctor"""
        result = await db.execute(
            select(Appointment)
            .where(Appointment.doctor_id == doctor_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_date_range(
        self,
        db: AsyncSession,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100
    ):
        """Get appointments by date range"""
        result = await db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.appointment_date >= start_date,
                    Appointment.appointment_date <= end_date
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(self, db: AsyncSession, status: str, skip: int = 0, limit: int = 100):
        """Get appointments by status"""
        result = await db.execute(
            select(Appointment)
            .where(Appointment.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def check_availability(
        self,
        db: AsyncSession,
        doctor_id: int,
        appointment_date: date,
        appointment_time: str
    ) -> bool:
        """Check if doctor is available at given time"""
        result = await db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date == appointment_date,
                    Appointment.appointment_time == appointment_time,
                    Appointment.status.in_(["confirmed", "pending"])
                )
            )
        )
        return result.scalars().first() is None


appointment = CRUDAppointment(Appointment)
