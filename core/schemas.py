"""Common response schemas."""

from typing import Any, Optional, List
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail schema."""

    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""

    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None


class SuccessResponse(BaseModel):
    """Base success response schema."""

    success: bool = True
    message: Optional[str] = None


class DataResponse(SuccessResponse):
    """Response with data."""

    data: Any


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(SuccessResponse):
    """Paginated response schema."""

    data: List[Any]
    pagination: PaginationMeta
