"""Admin endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db.models import Appointment, ContactMessage, User, Doctor, Department, Service
from app.core.dependencies import get_current_admin_user
from app.core.constants import AppointmentStatus

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics (admin only)"""
    
    try:
        # Total users
        users_result = await db.execute(select(func.count(User.id)))
        total_users = users_result.scalar() or 0
        
        # Active users
        active_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_result.scalar() or 0
        
        # Total appointments
        appointments_result = await db.execute(select(func.count(Appointment.id)))
        total_appointments = appointments_result.scalar() or 0
        
        # Confirmed appointments
        confirmed_result = await db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        )
        confirmed_appointments = confirmed_result.scalar() or 0
        
        # Pending appointments
        pending_result = await db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.PENDING
            )
        )
        pending_appointments = pending_result.scalar() or 0
        
        # Pending messages
        pending_messages_result = await db.execute(
            select(func.count(ContactMessage.id)).where(
                ContactMessage.status == "new"
            )
        )
        pending_messages = pending_messages_result.scalar() or 0
        
        # Total doctors
        doctors_result = await db.execute(select(func.count(Doctor.id)))
        total_doctors = doctors_result.scalar() or 0
        
        # Total departments
        departments_result = await db.execute(select(func.count(Department.id)))
        total_departments = departments_result.scalar() or 0
        
        # Total services
        services_result = await db.execute(select(func.count(Service.id)))
        total_services = services_result.scalar() or 0
        
        # Appointments this month
        today = datetime.utcnow()
        month_start = today.replace(day=1)
        month_appointments_result = await db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.created_at >= month_start
            )
        )
        month_appointments = month_appointments_result.scalar() or 0
        
        # Appointments this week
        week_start = today - timedelta(days=today.weekday())
        week_appointments_result = await db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.created_at >= week_start
            )
        )
        week_appointments = week_appointments_result.scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_appointments": total_appointments,
            "confirmed_appointments": confirmed_appointments,
            "pending_appointments": pending_appointments,
            "pending_messages": pending_messages,
            "total_doctors": total_doctors,
            "total_departments": total_departments,
            "total_services": total_services,
            "month_appointments": month_appointments,
            "week_appointments": week_appointments,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error in dashboard stats: {e}")
        raise


@router.get("/appointments/stats")
async def get_appointment_stats(
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get appointment statistics (admin only)"""
    
    try:
        # Appointments by status
        statuses = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.PENDING,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED,
            AppointmentStatus.NO_SHOW
        ]
        
        stats = {}
        for status in statuses:
            result = await db.execute(
                select(func.count(Appointment.id)).where(
                    Appointment.status == status
                )
            )
            stats[status] = result.scalar() or 0
        
        # Appointments in last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        recent_result = await db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.created_at >= start_date
            )
        )
        recent_appointments = recent_result.scalar() or 0
        
        return {
            "by_status": stats,
            f"last_{days}_days": recent_appointments,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error in appointment stats: {e}")
        raise


@router.get("/users/stats")
async def get_user_stats(
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user statistics (admin only)"""
    
    try:
        # Total users
        total_result = await db.execute(select(func.count(User.id)))
        total_users = total_result.scalar() or 0
        
        # Active users
        active_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_result.scalar() or 0
        
        # Admin users
        admin_result = await db.execute(
            select(func.count(User.id)).where(User.is_admin == True)
        )
        admin_users = admin_result.scalar() or 0
        
        # Doctor users
        doctor_result = await db.execute(
            select(func.count(User.id)).where(User.is_doctor == True)
        )
        doctor_users = doctor_result.scalar() or 0
        
        # Patient users (not admin, not doctor)
        patient_result = await db.execute(
            select(func.count(User.id)).where(
                (User.is_admin == False) & (User.is_doctor == False)
            )
        )
        patient_users = patient_result.scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "doctor_users": doctor_users,
            "patient_users": patient_users,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error in user stats: {e}")
        raise


@router.get("/messages/stats")
async def get_message_stats(
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contact message statistics (admin only)"""
    
    try:
        statuses = ["new", "read", "resolved"]
        stats = {}
        
        for status in statuses:
            result = await db.execute(
                select(func.count(ContactMessage.id)).where(
                    ContactMessage.status == status
                )
            )
            stats[status] = result.scalar() or 0
        
        return {
            "by_status": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error in message stats: {e}")
        raise


@router.get("/system/health")
async def get_system_health(
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system health status (admin only)"""
    
    try:
        # Check database connection
        await db.execute(select(func.count(User.id)))
        db_status = "operational"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "api_status": "operational",
        "database_status": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }
