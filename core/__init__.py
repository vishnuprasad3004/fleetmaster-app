"""Core module containing security, exceptions, and common schemas."""

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    validate_password,
)
from app.core.exceptions import (
    BaseException,
    ValidationException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    InternalServerException,
    RateLimitException,
)
from app.core.schemas import (
    SuccessResponse,
    DataResponse,
    ErrorResponse,
    PaginatedResponse,
)
from app.core.logging_config import logger, log_audit


__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "validate_password",
    # Exceptions
    "BaseException",
    "ValidationException",
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "ConflictException",
    "InternalServerException",
    "RateLimitException",
    # Schemas
    "SuccessResponse",
    "DataResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "logger",
    "log_audit",
]

