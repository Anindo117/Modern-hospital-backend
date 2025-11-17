"""Custom exception classes"""

from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API exception"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "An error occurred",
        headers: dict = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ValidationException(APIException):
    """Validation error exception"""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class AuthenticationException(APIException):
    """Authentication error exception"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(APIException):
    """Authorization error exception"""
    
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(APIException):
    """Resource not found exception"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(APIException):
    """Resource conflict exception"""
    
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InternalServerException(APIException):
    """Internal server error exception"""
    
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
