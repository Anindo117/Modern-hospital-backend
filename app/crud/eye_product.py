"""Eye Product CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import EyeProduct
from app.schemas.eye_product import EyeProductCreate, EyeProductUpdate
from app.crud.base import CRUDBase


class CRUDEyeProduct(CRUDBase[EyeProduct, EyeProductCreate, EyeProductUpdate]):
    """CRUD operations for EyeProduct model"""
    
    async def get_by_category(self, db: AsyncSession, category: str, skip: int = 0, limit: int = 10) -> tuple[list[EyeProduct], int]:
        """Get eye products by category"""
        return await self.get_all(db, skip, limit, {"category": category, "is_active": True})
    
    async def get_by_brand(self, db: AsyncSession, brand: str, skip: int = 0, limit: int = 10) -> tuple[list[EyeProduct], int]:
        """Get eye products by brand"""
        return await self.get_all(db, skip, limit, {"brand": brand, "is_active": True})
    
    async def get_available(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> tuple[list[EyeProduct], int]:
        """Get available eye products"""
        return await self.get_all(db, skip, limit, {"is_available": True, "is_active": True})
    
    async def get_active(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> tuple[list[EyeProduct], int]:
        """Get active eye products"""
        return await self.get_all(db, skip, limit, {"is_active": True})


eye_product = CRUDEyeProduct(EyeProduct)
