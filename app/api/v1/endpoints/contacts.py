"""Contact message endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.contact import (
    ContactMessageCreate,
    ContactMessageUpdate,
    ContactMessageResponse,
    ContactMessageListResponse,
)
from app.crud.contact import contact_message as crud_contact
from app.core.dependencies import get_current_admin_user
from app.core.exceptions import NotFoundException
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, ContactMessageStatus

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=ContactMessageListResponse)
async def list_contact_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    status: str = Query(None),
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List contact messages (admin only)
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **status**: Filter by status (new, read, resolved)
    """
    filters = {}
    if status:
        filters["status"] = status
    
    messages, total = await crud_contact.get_all(db, skip, limit, filters)
    
    return ContactMessageListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        items=messages
    )


@router.get("/{message_id}", response_model=ContactMessageResponse)
async def get_contact_message(
    message_id: int,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contact message details (admin only)"""
    message = await crud_contact.get(db, message_id)
    if not message:
        raise NotFoundException(detail="Message not found")
    
    return message


@router.post("", response_model=ContactMessageResponse, status_code=201)
async def create_contact_message(
    message_in: ContactMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit a contact message (public endpoint)"""
    message = await crud_contact.create(db, message_in)
    return message


@router.put("/{message_id}", response_model=ContactMessageResponse)
async def update_contact_message(
    message_id: int,
    message_in: ContactMessageUpdate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update contact message status (admin only)"""
    message = await crud_contact.get(db, message_id)
    if not message:
        raise NotFoundException(detail="Message not found")
    
    message = await crud_contact.update(db, message, message_in)
    return message


@router.delete("/{message_id}", status_code=204)
async def delete_contact_message(
    message_id: int,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete contact message (admin only)"""
    success = await crud_contact.delete(db, message_id)
    if not success:
        raise NotFoundException(detail="Message not found")


@router.get("/email/{email}", response_model=list[ContactMessageResponse])
async def get_messages_by_email(
    email: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages by email (admin only)"""
    messages = await crud_contact.get_by_email(db, email, skip, limit)
    return messages
