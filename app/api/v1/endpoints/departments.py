"""Department endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentDetailResponse,
)
from app.crud.department import department as crud_department
from app.core.dependencies import get_current_admin_user
from app.core.exceptions import NotFoundException, ConflictException
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    List all departments
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **active_only**: Return only active departments
    """
    filters = {"is_active": True} if active_only else None
    departments, _ = await crud_department.get_all(db, skip=skip, limit=limit, filters=filters)
    return departments


@router.get("/{department_id}", response_model=DepartmentDetailResponse)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get department details"""
    department = await crud_department.get(db, department_id)
    if not department:
        raise NotFoundException(detail="Department not found")
    
    # Get doctors count
    doctors_count = len(department.doctors) if department.doctors else 0
    
    return {
        **DepartmentResponse.from_orm(department).dict(),
        "doctors_count": doctors_count
    }


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    department_in: DepartmentCreate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new department (admin only)"""
    # Check if department already exists
    existing = await crud_department.get_by_name(db, department_in.name)
    if existing:
        raise ConflictException(detail="Department with this name already exists")
    
    department = await crud_department.create(db, department_in)
    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_in: DepartmentUpdate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update department (admin only)"""
    department = await crud_department.get(db, department_id)
    if not department:
        raise NotFoundException(detail="Department not found")
    
    # Check if new name already exists
    if department_in.name and department_in.name != department.name:
        existing = await crud_department.get_by_name(db, department_in.name)
        if existing:
            raise ConflictException(detail="Department with this name already exists")
    
    department = await crud_department.update(db, department, department_in)
    return department


@router.delete("/{department_id}", status_code=204)
async def delete_department(
    department_id: int,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete department (admin only)"""
    success = await crud_department.delete(db, department_id)
    if not success:
        raise NotFoundException(detail="Department not found")
