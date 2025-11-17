#!/usr/bin/env python3
"""
Script to create test users in the database
Creates: 1 Admin, 1 Doctor, 1 Patient
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal, init_db
from app.db.models import User, Department, Doctor
from app.core.security import SecurityUtils


async def create_test_users():
    """Create test users in the database"""
    
    # Initialize database
    print("Initializing database...")
    await init_db()
    print("✓ Database initialized")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if users already exist
            admin_check = await session.execute(
                select(User).where(User.phone == "+11234567890")
            )
            if admin_check.scalars().first():
                print("✗ Admin user already exists")
                return
            
            doctor_check = await session.execute(
                select(User).where(User.phone == "+11234567891")
            )
            if doctor_check.scalars().first():
                print("✗ Doctor user already exists")
                return
            
            patient_check = await session.execute(
                select(User).where(User.phone == "+11234567892")
            )
            if patient_check.scalars().first():
                print("✗ Patient user already exists")
                return
            
            # Create Admin User
            print("\n📝 Creating Admin User...")
            admin_user = User(
                phone="+11234567890",
                hashed_password=SecurityUtils.get_password_hash("Admin@123"),
                full_name="Admin User",
                email="admin@hospital.com",
                is_active=True,
                is_admin=True,
                is_doctor=False,
            )
            session.add(admin_user)
            await session.flush()
            print(f"✓ Admin User Created")
            print(f"  - Phone: +11234567890")
            print(f"  - Password: Admin@123")
            print(f"  - Email: admin@hospital.com")
            print(f"  - ID: {admin_user.id}")
            
            # Create Patient User
            print("\n📝 Creating Patient User...")
            patient_user = User(
                phone="+11234567892",
                hashed_password=SecurityUtils.get_password_hash("Patient@123"),
                full_name="John Patient",
                email="patient@hospital.com",
                is_active=True,
                is_admin=False,
                is_doctor=False,
            )
            session.add(patient_user)
            await session.flush()
            print(f"✓ Patient User Created")
            print(f"  - Phone: +11234567892")
            print(f"  - Password: Patient@123")
            print(f"  - Email: patient@hospital.com")
            print(f"  - ID: {patient_user.id}")
            
            # Create or get Department for Doctor
            print("\n📝 Checking/Creating Department...")
            dept_check = await session.execute(
                select(Department).where(Department.name == "Cardiology")
            )
            department = dept_check.scalars().first()
            
            if not department:
                department = Department(
                    name="Cardiology",
                    description="Heart and cardiovascular diseases",
                    is_active=True,
                )
                session.add(department)
                await session.flush()
                print(f"✓ Department Created: Cardiology (ID: {department.id})")
            else:
                print(f"✓ Department Found: Cardiology (ID: {department.id})")
            
            # Create Doctor User
            print("\n📝 Creating Doctor User...")
            doctor_user = User(
                phone="+11234567891",
                hashed_password=SecurityUtils.get_password_hash("Doctor@123"),
                full_name="Dr. Sarah Smith",
                email="doctor@hospital.com",
                is_active=True,
                is_admin=False,
                is_doctor=True,
            )
            session.add(doctor_user)
            await session.flush()
            print(f"✓ Doctor User Created")
            print(f"  - Phone: +11234567891")
            print(f"  - Password: Doctor@123")
            print(f"  - Email: doctor@hospital.com")
            print(f"  - ID: {doctor_user.id}")
            
            # Create Doctor Profile
            print("\n📝 Creating Doctor Profile...")
            doctor_profile = Doctor(
                user_id=doctor_user.id,
                specialty="Cardiology",
                bio="Experienced cardiologist with 10+ years of practice",
                experience_years=10,
                department_id=department.id,
                is_available=True,
            )
            session.add(doctor_profile)
            await session.flush()
            print(f"✓ Doctor Profile Created")
            print(f"  - Specialty: Cardiology")
            print(f"  - Experience: 10 years")
            print(f"  - Department: {department.name}")
            print(f"  - ID: {doctor_profile.id}")
            
            # Commit all changes
            await session.commit()
            
            print("\n" + "="*60)
            print("✅ ALL TEST USERS CREATED SUCCESSFULLY!")
            print("="*60)
            
            print("\n📋 TEST USER CREDENTIALS:\n")
            
            print("🔐 ADMIN USER:")
            print("   Phone: +11234567890")
            print("   Password: Admin@123")
            print("   Email: admin@hospital.com")
            
            print("\n👨‍⚕️ DOCTOR USER:")
            print("   Phone: +11234567891")
            print("   Password: Doctor@123")
            print("   Email: doctor@hospital.com")
            print("   Specialty: Cardiology")
            
            print("\n👤 PATIENT USER:")
            print("   Phone: +11234567892")
            print("   Password: Patient@123")
            print("   Email: patient@hospital.com")
            
            print("\n" + "="*60)
            print("You can now use these credentials to log in!")
            print("="*60 + "\n")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error creating test users: {e}")
            raise


async def main():
    """Main entry point"""
    try:
        await create_test_users()
    except Exception as e:
        print(f"\n❌ Failed to create test users: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
