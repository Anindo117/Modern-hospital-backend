"""Contact message CRUD operations"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import ContactMessage
from app.schemas.contact import ContactMessageCreate, ContactMessageUpdate
from .base import CRUDBase


class CRUDContactMessage(CRUDBase[ContactMessage, ContactMessageCreate, ContactMessageUpdate]):
    """Contact message CRUD operations"""
    
    async def get_by_status(self, db: AsyncSession, status: str, skip: int = 0, limit: int = 100):
        """Get messages by status"""
        result = await db.execute(
            select(ContactMessage)
            .where(ContactMessage.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_email(self, db: AsyncSession, email: str, skip: int = 0, limit: int = 100):
        """Get messages by email"""
        result = await db.execute(
            select(ContactMessage)
            .where(ContactMessage.email == email)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


contact_message = CRUDContactMessage(ContactMessage)
