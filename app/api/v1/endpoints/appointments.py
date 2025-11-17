"""Appointment endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.db.session import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentDetailResponse,
    AppointmentListResponse,
)
from app.crud.appointment import appointment as crud_appointment
from app.crud.department import department as crud_department
from app.crud.doctor import doctor as crud_doctor
from app.core.dependencies import get_current_user, get_current_admin_user
from app.core.exceptions import NotFoundException, ValidationException, ConflictException
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, AppointmentStatus

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=AppointmentListResponse)
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    status: str = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List appointments
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **status**: Filter by status
    
    Regular users see only their appointments, admins see all
    """
    filters = {}
    
    # Regular users see only their appointments
    if not current_user.is_admin:
        filters["patient_id"] = current_user.id
    
    if status:
        filters["status"] = status
    
    appointments, total = await crud_appointment.get_all(db, skip, limit, filters)
    
    return AppointmentListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        items=appointments
    )


@router.get("/{appointment_id}", response_model=AppointmentDetailResponse)
async def get_appointment(
    appointment_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get appointment details"""
    appointment = await crud_appointment.get(db, appointment_id)
    if not appointment:
        raise NotFoundException(detail="Appointment not found")
    
    # Check authorization
    if not current_user.is_admin and appointment.patient_id != current_user.id:
        raise NotFoundException(detail="Appointment not found")
    
    # Get related info
    patient = appointment.patient
    doctor = appointment.doctor
    dept = appointment.department
    
    return {
        **AppointmentResponse.from_orm(appointment).dict(),
        "patient_name": patient.full_name if patient else None,
        "patient_phone": patient.phone if patient else None,
        "patient_email": patient.email if patient else None,
        "doctor_name": doctor.user.full_name if doctor and doctor.user else None,
        "doctor_specialty": doctor.specialty if doctor else None,
        "department_name": dept.name if dept else None,
    }


@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    appointment_in: AppointmentCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new appointment"""
    # Verify department exists
    department = await crud_department.get(db, appointment_in.department_id)
    if not department:
        raise NotFoundException(detail="Department not found")
    
    # Verify doctor if provided
    if appointment_in.doctor_id:
        doctor = await crud_doctor.get(db, appointment_in.doctor_id)
        if not doctor:
            raise NotFoundException(detail="Doctor not found")
        
        # Check availability
        is_available = await crud_appointment.check_availability(
            db,
            appointment_in.doctor_id,
            appointment_in.appointment_date,
            appointment_in.appointment_time
        )
        if not is_available:
            raise ConflictException(detail="Doctor is not available at this time")
    
    # Create appointment
    appointment_data = appointment_in.dict()
    appointment_data["patient_id"] = current_user.id
    
    appointment = await crud_appointment.create(
        db,
        AppointmentCreate(**appointment_data)
    )
    
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_in: AppointmentUpdate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update appointment (admin only)"""
    appointment = await crud_appointment.get(db, appointment_id)
    if not appointment:
        raise NotFoundException(detail="Appointment not found")
    
    # Validate status if provided
    if appointment_in.status and appointment_in.status not in AppointmentStatus.ALL:
        raise ValidationException(detail="Invalid appointment status")
    
    appointment = await crud_appointment.update(db, appointment, appointment_in)
    return appointment


@router.delete("/{appointment_id}", status_code=204)
async def cancel_appointment(
    appointment_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel appointment"""
    appointment = await crud_appointment.get(db, appointment_id)
    if not appointment:
        raise NotFoundException(detail="Appointment not found")
    
    # Check authorization
    if not current_user.is_admin and appointment.patient_id != current_user.id:
        raise NotFoundException(detail="Appointment not found")
    
    # Update status to cancelled
    appointment.status = AppointmentStatus.CANCELLED
    db.add(appointment)
    await db.commit()


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
async def get_patient_appointments(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get appointments for a patient (admin only)"""
    appointments = await crud_appointment.get_by_patient(db, patient_id, skip, limit)
    return appointments


@router.get("/doctor/{doctor_id}", response_model=list[AppointmentResponse])
async def get_doctor_appointments(
    doctor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get appointments for a doctor (admin only)"""
    appointments = await crud_appointment.get_by_doctor(db, doctor_id, skip, limit)
    return appointments
