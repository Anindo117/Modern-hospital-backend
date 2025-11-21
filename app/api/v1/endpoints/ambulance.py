"""Ambulance Service endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ambulance import (
    AmbulanceServiceCreate,
    AmbulanceServiceUpdate,
    AmbulanceServiceResponse,
)
from app.crud.ambulance import ambulance_service as crud_ambulance
from app.core.dependencies import get_current_admin_user
from app.core.exceptions import NotFoundException, ConflictException
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/ambulance-services", tags=["ambulance-services"])


@router.get("", response_model=list[AmbulanceServiceResponse])
async def list_ambulance_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    active_only: bool = Query(True),
    available_24_7: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    List all ambulance services
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **active_only**: Return only active services
    - **available_24_7**: Return only 24/7 available services
    """
    if available_24_7:
        services, _ = await crud_ambulance.get_available_24_7(db, skip=skip, limit=limit)
    else:
        filters = {"is_active": True} if active_only else None
        services, _ = await crud_ambulance.get_all(db, skip=skip, limit=limit, filters=filters)
    return services


@router.get("/{service_id}", response_model=AmbulanceServiceResponse)
async def get_ambulance_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get ambulance service details"""
    service = await crud_ambulance.get(db, service_id)
    if not service:
        raise NotFoundException(detail="Ambulance service not found")
    
    return service


@router.post("", response_model=AmbulanceServiceResponse, status_code=201)
async def create_ambulance_service(
    service_in: AmbulanceServiceCreate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new ambulance service (admin only)"""
    # Check if service already exists
    existing = await crud_ambulance.get_by_name(db, service_in.name)
    if existing:
        raise ConflictException(detail="Ambulance service with this name already exists")
    
    service = await crud_ambulance.create(db, service_in)
    return service


@router.put("/{service_id}", response_model=AmbulanceServiceResponse)
async def update_ambulance_service(
    service_id: int,
    service_in: AmbulanceServiceUpdate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update ambulance service (admin only)"""
    service = await crud_ambulance.get(db, service_id)
    if not service:
        raise NotFoundException(detail="Ambulance service not found")
    
    # Check if new name already exists
    if service_in.name and service_in.name != service.name:
        existing = await crud_ambulance.get_by_name(db, service_in.name)
        if existing:
            raise ConflictException(detail="Ambulance service with this name already exists")
    
    service = await crud_ambulance.update(db, service, service_in)
    return service


@router.delete("/{service_id}", status_code=204)
async def delete_ambulance_service(
    service_id: int,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete ambulance service (admin only)"""
    success = await crud_ambulance.delete(db, service_id)
    if not success:
        raise NotFoundException(detail="Ambulance service not found")
