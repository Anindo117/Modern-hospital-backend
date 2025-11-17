"""Security utilities for authentication and password management"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import re

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """
        Validate phone number format
        Accepts formats like: 1234567890, +11234567890, (123) 456-7890, 123-456-7890
        """
        # Remove common formatting characters
        cleaned_phone = re.sub(r"[\s\-\(\)\.]+", "", phone)
        
        # Check if it's a valid phone number (digits only, with optional + prefix)
        if not re.match(r"^\+?\d{10,15}$", cleaned_phone):
            return False, f"Invalid phone number format. Must be {settings.PHONE_MIN_LENGTH}-{settings.PHONE_MAX_LENGTH} digits"
        
        # Check length
        digits_only = re.sub(r"\D", "", cleaned_phone)
        if len(digits_only) < settings.PHONE_MIN_LENGTH or len(digits_only) > settings.PHONE_MAX_LENGTH:
            return False, f"Phone number must be {settings.PHONE_MIN_LENGTH}-{settings.PHONE_MAX_LENGTH} digits"
        
        return True, "Phone number is valid"
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number to standard format"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d\+]", "", phone)
        
        # If it doesn't start with +, add country code
        if not cleaned.startswith("+"):
            # Remove leading 1 if present (for US numbers)
            if cleaned.startswith("1") and len(cleaned) == 11:
                cleaned = cleaned[1:]
            cleaned = settings.PHONE_COUNTRY_CODE + cleaned
        
        return cleaned


class TokenUtils:
    """Utility class for JWT token operations"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def create_tokens(user_id: int, phone: str) -> Dict[str, str]:
        """Create both access and refresh tokens"""
        access_token = TokenUtils.create_access_token(
            data={"sub": str(user_id), "phone": phone}
        )
        refresh_token = TokenUtils.create_refresh_token(
            data={"sub": str(user_id), "phone": phone}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


