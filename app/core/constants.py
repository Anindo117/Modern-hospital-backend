"""Application constants"""

# Appointment Status
class AppointmentStatus:
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no-show"
    PENDING = "pending"
    
    ALL = [CONFIRMED, CANCELLED, COMPLETED, NO_SHOW, PENDING]


# Contact Message Status
class ContactMessageStatus:
    NEW = "new"
    READ = "read"
    RESOLVED = "resolved"
    
    ALL = [NEW, READ, RESOLVED]


# User Roles
class UserRole:
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    STAFF = "staff"
    
    ALL = [ADMIN, DOCTOR, PATIENT, STAFF]


# Error Messages
class ErrorMessages:
    INVALID_CREDENTIALS = "Invalid phone number or password"
    USER_NOT_FOUND = "User not found"
    USER_ALREADY_EXISTS = "User with this phone number already exists"
    INVALID_PHONE = "Invalid phone number format"
    INVALID_PASSWORD = "Invalid password"
    WEAK_PASSWORD = "Password does not meet security requirements"
    UNAUTHORIZED = "Not authorized"
    FORBIDDEN = "Access forbidden"
    NOT_FOUND = "Resource not found"
    CONFLICT = "Resource already exists"
    INTERNAL_ERROR = "Internal server error"
    INVALID_TOKEN = "Invalid or expired token"
    TOKEN_EXPIRED = "Token has expired"
    APPOINTMENT_CONFLICT = "Appointment time slot is not available"
    DOCTOR_NOT_AVAILABLE = "Doctor is not available at this time"


# Success Messages
class SuccessMessages:
    USER_CREATED = "User created successfully"
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    PASSWORD_CHANGED = "Password changed successfully"
    APPOINTMENT_CREATED = "Appointment created successfully"
    APPOINTMENT_UPDATED = "Appointment updated successfully"
    APPOINTMENT_CANCELLED = "Appointment cancelled successfully"
    MESSAGE_SENT = "Message sent successfully"
    PROFILE_UPDATED = "Profile updated successfully"


# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1


# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour
