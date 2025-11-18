"""Doctor endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Doctor
from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorDetailResponse,
)
from app.crud.doctor import doctor as crud_doctor
from app.crud.user import user as crud_user
from app.crud.department import department as crud_department
from app.core.dependencies import get_current_admin_user
from app.core.exceptions import NotFoundException, ValidationException
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorResponse])
async def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    department_id: int = Query(None),
    available_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    List all doctors
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **department_id**: Filter by department
    - **available_only**: Return only available doctors
    """
    if department_id:
        doctors = await crud_doctor.get_by_department(db, department_id, skip, limit)
    elif available_only:
        doctors = await crud_doctor.get_available(db, skip, limit)
    else:
        doctors, _ = await crud_doctor.get_all(db, skip, limit)
    
    return doctors


@router.get("/{doctor_id}", response_model=DoctorDetailResponse)
async def get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get doctor details"""
    # Eagerly load user and department relationships
    result = await db.execute(
        select(Doctor)
        .where(Doctor.id == doctor_id)
        .options(selectinload(Doctor.user), selectinload(Doctor.department))
    )
    doctor = result.scalars().first()
    
    if not doctor:
        raise NotFoundException(detail="Doctor not found")
    
    # Get user info
    user = doctor.user
    department = doctor.department
    
    return {
        **DoctorResponse.from_orm(doctor).dict(),
        "user_name": user.full_name if user else None,
        "user_phone": user.phone if user else None,
        "user_email": user.email if user else None,
        "department_name": department.name if department else None,
        "appointments_count": len(doctor.appointments) if doctor.appointments else 0,
    }


@router.get("/department/{department_id}", response_model=list[DoctorResponse])
async def get_doctors_by_department(
    department_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: AsyncSession = Depends(get_db)
):
    """Get doctors by department"""
    # Verify department exists
    department = await crud_department.get(db, department_id)
    if not department:
        raise NotFoundException(detail="Department not found")
    
    doctors = await crud_doctor.get_by_department(db, department_id, skip, limit)
    return doctors


@router.post("", response_model=DoctorResponse, status_code=201)
async def create_doctor(
    doctor_in: DoctorCreate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new doctor (admin only)"""
    # Verify user exists
    user = await crud_user.get(db, doctor_in.user_id)
    if not user:
        raise NotFoundException(detail="User not found")
    
    # Verify department exists
    department = await crud_department.get(db, doctor_in.department_id)
    if not department:
        raise NotFoundException(detail="Department not found")
    
    # Check if user is already a doctor
    existing_doctor = await crud_doctor.get_by_user_id(db, doctor_in.user_id)
    if existing_doctor:
        raise ValidationException(detail="User is already a doctor")
    
    doctor = await crud_doctor.create(db, doctor_in)
    
    # Update user to mark as doctor
    user.is_doctor = True
    db.add(user)
    await db.commit()
    
    # Refresh to load relationships
    await db.refresh(doctor)
    
    return doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_in: DoctorUpdate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update doctor (admin only)"""
    doctor = await crud_doctor.get(db, doctor_id)
    if not doctor:
        raise NotFoundException(detail="Doctor not found")
    
    # Verify department if provided
    if doctor_in.department_id:
        department = await crud_department.get(db, doctor_in.department_id)
        if not department:
            raise NotFoundException(detail="Department not found")
    
    doctor = await crud_doctor.update(db, doctor, doctor_in)
    
    # Refresh to load relationships
    await db.refresh(doctor)
    
    return doctor


@router.delete("/{doctor_id}", status_code=204)
async def delete_doctor(
    doctor_id: int,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete doctor (admin only)"""
    doctor = await crud_doctor.get(db, doctor_id)
    if not doctor:
        raise NotFoundException(detail="Doctor not found")
    
    # Update user to remove doctor status
    user = doctor.user
    user.is_doctor = False
    db.add(user)
    
    success = await crud_doctor.delete(db, doctor_id)
    if not success:
        raise NotFoundException(detail="Doctor not found")
    
    await db.commit()
