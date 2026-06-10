"""Vehicle schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class VehicleType(str, Enum):
    """Vehicle type enumeration."""
    TRUCK = "truck"
    MINI_TRUCK = "mini_truck"
    PICKUP = "pickup"
    TEMPO = "tempo"
    TRAILER = "trailer"
    CONTAINER = "container"
    BUS = "bus"
    MINI_BUS = "mini_bus"
    CAR = "car"
    TAXI = "taxi"
    AUTO = "auto"
    BIKE = "bike"
    OTHER = "other"


class VehicleStatus(str, Enum):
    """Vehicle status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    SOLD = "sold"
    ACCIDENT = "accident"


# Vehicle Document Schemas
class VehicleDocumentBase(BaseModel):
    """Base vehicle document schema."""
    document_type: str = Field(..., description="Type of document (rc, insurance, permit, etc.)")
    document_number: Optional[str] = Field(None, description="Document number")
    issuing_authority: Optional[str] = Field(None, description="Authority that issued the document")
    issue_date: Optional[datetime] = Field(None, description="Document issue date")
    expiry_date: Optional[datetime] = Field(None, description="Document expiry date")
    document_url: Optional[str] = Field(None, description="URL to document file")
    notes: Optional[str] = Field(None, description="Additional notes")


class VehicleDocumentCreate(VehicleDocumentBase):
    """Schema for creating vehicle document."""
    vehicle_id: str = Field(..., description="Vehicle ID this document belongs to")


class VehicleDocumentUpdate(BaseModel):
    """Schema for updating vehicle document."""
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    document_url: Optional[str] = None
    notes: Optional[str] = None


class VehicleDocumentResponse(VehicleDocumentBase):
    """Schema for vehicle document response."""
    id: str
    vehicle_id: str
    created_at: datetime
    updated_at: datetime
    is_expired: bool
    days_to_expiry: Optional[int]

    class Config:
        from_attributes = True


# Vehicle Schemas
class VehicleBase(BaseModel):
    """Base vehicle schema."""
    registration_number: str = Field(..., description="Vehicle registration number")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    brand: Optional[str] = Field(None, description="Vehicle brand")
    model: Optional[str] = Field(None, description="Vehicle model")
    variant: Optional[str] = Field(None, description="Vehicle variant")
    year: Optional[int] = Field(None, description="Manufacturing year")
    color: Optional[str] = Field(None, description="Vehicle color")
    engine_number: Optional[str] = Field(None, description="Engine number")
    chassis_number: Optional[str] = Field(None, description="Chassis number")
    
    # Technical specs
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    fuel_capacity: Optional[float] = Field(None, description="Fuel tank capacity in liters")
    mileage: Optional[float] = Field(None, description="Expected mileage in km/liter")
    engine_capacity: Optional[int] = Field(None, description="Engine capacity in CC")
    max_load: Optional[float] = Field(None, description="Maximum load in tonnes")
    seating_capacity: Optional[int] = Field(None, description="Seating capacity")
    
    # Purchase info
    purchase_date: Optional[datetime] = Field(None, description="Purchase date")
    purchase_price: Optional[float] = Field(None, description="Purchase price")
    dealer_name: Optional[str] = Field(None, description="Dealer name")
    finance_company: Optional[str] = Field(None, description="Finance company")
    loan_amount: Optional[float] = Field(None, description="Loan amount")
    emi_amount: Optional[float] = Field(None, description="EMI amount")
    loan_end_date: Optional[datetime] = Field(None, description="Loan end date")
    
    # Current status
    status: VehicleStatus = Field(VehicleStatus.ACTIVE, description="Vehicle status")
    current_odo: float = Field(0, description="Current odometer reading in km")
    last_service_odo: Optional[float] = Field(None, description="Last service odometer reading")
    next_service_odo: Optional[float] = Field(None, description="Next service odometer reading")


class VehicleCreate(VehicleBase):
    """Schema for creating vehicle."""
    fleet_id: Optional[str] = Field(None, description="Fleet ID (optional)")


class VehicleUpdate(BaseModel):
    """Schema for updating vehicle."""
    registration_number: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    engine_number: Optional[str] = None
    chassis_number: Optional[str] = None
    fuel_type: Optional[str] = None
    fuel_capacity: Optional[float] = None
    mileage: Optional[float] = None
    engine_capacity: Optional[int] = None
    max_load: Optional[float] = None
    seating_capacity: Optional[int] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    dealer_name: Optional[str] = None
    finance_company: Optional[str] = None
    loan_amount: Optional[float] = None
    emi_amount: Optional[float] = None
    loan_end_date: Optional[datetime] = None
    status: Optional[VehicleStatus] = None
    current_odo: Optional[float] = None
    last_service_odo: Optional[float] = None
    next_service_odo: Optional[float] = None
    fleet_id: Optional[str] = None
    current_driver_id: Optional[str] = None


class VehicleResponse(VehicleBase):
    """Schema for vehicle response."""
    id: str
    owner_id: str
    fleet_id: Optional[str]
    current_driver_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    documents: List[VehicleDocumentResponse] = []
    is_document_expired: bool
    next_service_due_km: Optional[float]
    is_service_due: bool

    class Config:
        from_attributes = True


class VehicleListResponse(BaseModel):
    """Schema for vehicle list response."""
    vehicles: List[VehicleResponse]
    total: int
    skip: int
    limit: int


class VehicleStatsResponse(BaseModel):
    """Schema for vehicle statistics response."""
    total_vehicles: int
    active_vehicles: int
    vehicles_in_maintenance: int
    inactive_vehicles: int
    vehicles_with_expired_docs: int
    vehicles_due_for_service: int