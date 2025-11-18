"""Doctor CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from .base import CRUDBase


class CRUDDoctor(CRUDBase[Doctor, DoctorCreate, DoctorUpdate]):
    """Doctor CRUD operations"""
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int):
        """Get doctor by user ID"""
        result = await db.execute(
            select(Doctor)
            .where(Doctor.user_id == user_id)
            .options(selectinload(Doctor.user))
        )
        return result.scalars().first()
    
    async def get_by_department(self, db: AsyncSession, department_id: int, skip: int = 0, limit: int = 100):
        """Get doctors by department"""
        result = await db.execute(
            select(Doctor)
            .where(Doctor.department_id == department_id)
            .where(Doctor.is_available == True)
            .options(selectinload(Doctor.user))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_available(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        """Get all available doctors"""
        result = await db.execute(
            select(Doctor)
            .where(Doctor.is_available == True)
            .options(selectinload(Doctor.user))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


doctor = CRUDDoctor(Doctor)
