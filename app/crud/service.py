"""Service CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Service
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.crud.base import CRUDBase


class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    """CRUD operations for Service model"""
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Service:
        """Get service by name"""
        result = await db.execute(
            select(Service).where(Service.name == name)
        )
        return result.scalars().first()
    
    async def get_active(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> tuple[list[Service], int]:
        """Get active services"""
        return await self.get_all(db, skip, limit, {"is_active": True})


service = CRUDService(Service)
