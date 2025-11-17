"""SQLAlchemy database models"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Date, Time, Enum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.db.base import Base
from app.core.constants import AppointmentStatus, ContactMessageStatus


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    is_doctor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient", foreign_keys="Appointment.patient_id")
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    
    __table_args__ = (
        Index('idx_users_phone_active', 'phone', 'is_active'),
    )


class Department(Base):
    """Department model"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctors = relationship("Doctor", back_populates="department", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="department", cascade="all, delete-orphan")


class Doctor(Base):
    """Doctor model"""
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    specialty = Column(String(255), nullable=False, index=True)
    image_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    is_available = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor", foreign_keys="Appointment.doctor_id")
    
    __table_args__ = (
        Index('idx_doctors_department_available', 'department_id', 'is_available'),
    )


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default=AppointmentStatus.CONFIRMED, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", back_populates="appointments", foreign_keys=[patient_id])
    doctor = relationship("Doctor", back_populates="appointments", foreign_keys=[doctor_id])
    department = relationship("Department", back_populates="appointments")
    
    __table_args__ = (
        Index('idx_appointments_patient_date', 'patient_id', 'appointment_date'),
        Index('idx_appointments_doctor_date', 'doctor_id', 'appointment_date'),
        Index('idx_appointments_status_date', 'status', 'appointment_date'),
    )


class ContactMessage(Base):
    """Contact message model"""
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(50), default=ContactMessageStatus.NEW, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_contact_messages_status_date', 'status', 'created_at'),
    )


class Service(Base):
    """Service model"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit log model for tracking changes"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_audit_logs_user_date', 'user_id', 'created_at'),
        Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
    )
