"""Ambulance Service CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import AmbulanceService
from app.schemas.ambulance import AmbulanceServiceCreate, AmbulanceServiceUpdate
from app.crud.base import CRUDBase


class CRUDAmbulanceService(CRUDBase[AmbulanceService, AmbulanceServiceCreate, AmbulanceServiceUpdate]):
    """CRUD operations for AmbulanceService model"""
    
    async def get_by_name(self, db: AsyncSession, name: str) -> AmbulanceService:
        """Get ambulance service by name"""
        result = await db.execute(
            select(AmbulanceService).where(AmbulanceService.name == name)
        )
        return result.scalars().first()
    
    async def get_active(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> tuple[list[AmbulanceService], int]:
        """Get active ambulance services"""
        return await self.get_all(db, skip, limit, {"is_active": True})
    
    async def get_available_24_7(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> tuple[list[AmbulanceService], int]:
        """Get 24/7 available ambulance services"""
        return await self.get_all(db, skip, limit, {"is_active": True, "available_24_7": True})


ambulance_service = CRUDAmbulanceService(AmbulanceService)
