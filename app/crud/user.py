"""User CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import SecurityUtils
from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User CRUD operations"""
    
    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[User]:
        """Get user by phone number"""
        # Normalize phone number
        normalized_phone = SecurityUtils.normalize_phone(phone)
        result = await db.execute(select(User).where(User.phone == normalized_phone))
        return result.scalars().first()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """Create new user"""
        # Normalize phone number
        normalized_phone = SecurityUtils.normalize_phone(obj_in.phone)
        
        # Hash password
        hashed_password = SecurityUtils.get_password_hash(obj_in.password)
        
        db_obj = User(
            phone=normalized_phone,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            email=obj_in.email,
            nid=obj_in.nid,
            date_of_birth=obj_in.date_of_birth,
            gender=obj_in.gender,
            blood_group=obj_in.blood_group,
            division=obj_in.division,
            district=obj_in.district,
            upazila=obj_in.upazila,
            village=obj_in.village,
            address=obj_in.address,
            emergency_contact_name=obj_in.emergency_contact_name,
            emergency_contact_phone=obj_in.emergency_contact_phone,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def authenticate(self, db: AsyncSession, phone: str, password: str) -> Optional[User]:
        """Authenticate user with phone and password"""
        user = await self.get_by_phone(db, phone)
        if not user:
            return None
        
        if not SecurityUtils.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def change_password(
        self,
        db: AsyncSession,
        user: User,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        if not SecurityUtils.verify_password(old_password, user.hashed_password):
            return False
        
        user.hashed_password = SecurityUtils.get_password_hash(new_password)
        db.add(user)
        await db.commit()
        return True
    
    async def get_active_users(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        """Get all active users"""
        result = await db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


user = CRUDUser(User)
