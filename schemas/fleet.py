"""Fleet request and response schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FleetCreate(BaseModel):
    """Fleet creation schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    registration_number: Optional[str] = None

    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    city: Optional[str] = None
    state_code: Optional[str] = None
    address: Optional[str] = None


class FleetUpdate(BaseModel):
    """Fleet update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    address: Optional[str] = None


class FleetResponse(BaseModel):
    """Fleet response schema."""

    id: str
    name: str
    description: Optional[str]
    owner_id: str
    industry: Optional[str]
    total_vehicles: int
    total_drivers: int
    phone_number: Optional[str]
    email: Optional[str]
    city: Optional[str]
    state_code: Optional[str]
    address: Optional[str]
    status: str
    tier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
