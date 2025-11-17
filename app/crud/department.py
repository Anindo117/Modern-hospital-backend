"""Department CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from .base import CRUDBase


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    """Department CRUD operations"""
    
    async def get_by_name(self, db: AsyncSession, name: str):
        """Get department by name"""
        result = await db.execute(select(Department).where(Department.name == name))
        return result.scalars().first()
    
    async def get_active(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        """Get all active departments"""
        result = await db.execute(
            select(Department)
            .where(Department.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


department = CRUDDepartment(Department)
