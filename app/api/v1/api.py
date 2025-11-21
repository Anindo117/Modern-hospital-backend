"""API v1 router"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, departments, doctors, appointments, contacts, admin, services, ambulance, eye_product

api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(departments.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(contacts.router)
api_router.include_router(services.router)
api_router.include_router(ambulance.router)
api_router.include_router(eye_product.router)
api_router.include_router(admin.router)
