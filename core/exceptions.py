"""Custom exceptions for the application."""

from typing import Any, Optional


class BaseException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, code: str = "ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(BaseException):
    """Raised when validation fails."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, code, 422)


class NotFoundException(BaseException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message, code, 404)


class UnauthorizedException(BaseException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized", code: str = "UNAUTHORIZED"):
        super().__init__(message, code, 401)


class ForbiddenException(BaseException):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Forbidden", code: str = "FORBIDDEN"):
        super().__init__(message, code, 403)


class ConflictException(BaseException):
    """Raised when there's a resource conflict."""

    def __init__(self, message: str = "Conflict", code: str = "CONFLICT"):
        super().__init__(message, code, 409)


class InternalServerException(BaseException):
    """Raised for internal server errors."""

    def __init__(self, message: str = "Internal server error", code: str = "INTERNAL_ERROR"):
        super().__init__(message, code, 500)


class RateLimitException(BaseException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", code: str = "RATE_LIMIT"):
        super().__init__(message, code, 429)
