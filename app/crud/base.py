"""Base CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Generic, TypeVar, Type, Optional, List, Any

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD class"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get single record by ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> tuple[List[ModelType], int]:
        """Get all records with pagination and optional filters"""
        query = select(self.model)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        
        # Get total count
        count_query = select(func.count(self.model.id))
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    count_query = count_query.where(getattr(self.model, key) == value)
        
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Create new record"""
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update existing record"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete record by ID"""
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return True
        return False
    
    async def exists(self, db: AsyncSession, **filters) -> bool:
        """Check if record exists"""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await db.execute(query)
        return result.scalars().first() is not None
