"""Service endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)
from app.crud.service import service as crud_service
from app.core.dependencies import get_current_admin_user
from app.core.exceptions import NotFoundException, ConflictException
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    List all services
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **active_only**: Return only active services
    """
    filters = {"is_active": True} if active_only else None
    services, _ = await crud_service.get_all(db, skip=skip, limit=limit, filters=filters)
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get service details"""
    service = await crud_service.get(db, service_id)
    if not service:
        raise NotFoundException(detail="Service not found")
    
    return service


@router.post("", response_model=ServiceResponse, status_code=201)
async def create_service(
    service_in: ServiceCreate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new service (admin only)"""
    # Check if service already exists
    existing = await crud_service.get_by_name(db, service_in.name)
    if existing:
        raise ConflictException(detail="Service with this name already exists")
    
    service = await crud_service.create(db, service_in)
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update service (admin only)"""
    service = await crud_service.get(db, service_id)
    if not service:
        raise NotFoundException(detail="Service not found")
    
    # Check if new name already exists
    if service_in.name and service_in.name != service.name:
        existing = await crud_service.get_by_name(db, service_in.name)
        if existing:
            raise ConflictException(detail="Service with this name already exists")
    
    service = await crud_service.update(db, service, service_in)
    return service


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: int,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete service (admin only)"""
    success = await crud_service.delete(db, service_id)
    if not success:
        raise NotFoundException(detail="Service not found")
