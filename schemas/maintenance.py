"""Maintenance schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class MaintenanceType(str, Enum):
    """Types of maintenance records."""
    SERVICE = "service"
    REPAIR = "repair"
    INSPECTION = "inspection"
    TYRE_REPLACEMENT = "tyre_replacement"
    BATTERY_REPLACEMENT = "battery_replacement"
    OIL_CHANGE = "oil_change"
    OTHER = "other"


class SparePartCreate(BaseModel):
    """Schema for creating a spare part."""
    name: str = Field(..., min_length=1, max_length=255)
    part_number: Optional[str] = Field(None, max_length=100)
    quantity: int = Field(..., ge=1)
    cost_per_unit: float = Field(..., ge=0)
    supplier_name: Optional[str] = Field(None, max_length=255)
    supplier_contact: Optional[str] = Field(None, max_length=50)
    
    @validator('total_cost', pre=True, always=True)
    def calculate_total_cost(cls, v, values):
        """Calculate total cost from quantity and cost per unit."""
        if 'quantity' in values and 'cost_per_unit' in values:
            return values['quantity'] * values['cost_per_unit']
        return 0.0


class SparePartResponse(BaseModel):
    """Schema for spare part response."""
    id: str
    name: str
    part_number: Optional[str]
    quantity: int
    cost_per_unit: float
    total_cost: float
    supplier_name: Optional[str]
    supplier_contact: Optional[str]
    
    class Config:
        from_attributes = True


class MaintenanceRecordCreate(BaseModel):
    """Schema for creating a maintenance record."""
    vehicle_id: str
    type: MaintenanceType
    date: datetime
    cost: float = Field(..., ge=0)
    workshop_name: Optional[str] = Field(None, max_length=255)
    workshop_contact: Optional[str] = Field(None, max_length=50)
    workshop_address: Optional[str] = None
    odometer_reading: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    notes: Optional[str] = None
    spare_parts: List[SparePartCreate] = []
    next_service_date: Optional[datetime] = None
    next_service_odometer: Optional[int] = Field(None, ge=0)


class MaintenanceRecordUpdate(BaseModel):
    """Schema for updating a maintenance record."""
    type: Optional[MaintenanceType] = None
    date: Optional[datetime] = None
    cost: Optional[float] = Field(None, ge=0)
    workshop_name: Optional[str] = Field(None, max_length=255)
    workshop_contact: Optional[str] = Field(None, max_length=50)
    workshop_address: Optional[str] = None
    odometer_reading: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    notes: Optional[str] = None
    spare_parts: Optional[List[SparePartCreate]] = None
    next_service_date: Optional[datetime] = None
    next_service_odometer: Optional[int] = Field(None, ge=0)


class MaintenanceRecordResponse(BaseModel):
    """Schema for maintenance record response."""
    id: str
    vehicle_id: str
    vehicle_number: Optional[str] = None
    type: MaintenanceType
    date: datetime
    cost: float
    workshop_name: Optional[str]
    workshop_contact: Optional[str]
    odometer_reading: Optional[int]
    description: Optional[str]
    notes: Optional[str]
    spare_parts: List[SparePartResponse] = []
    next_service_date: Optional[datetime]
    next_service_odometer: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MaintenanceDashboardResponse(BaseModel):
    """Schema for maintenance dashboard response."""
    service_due_today: int = 0
    service_due_this_week: int = 0
    total_maintenance_cost: float = 0.0
    vehicles_in_service: int = 0
    cost_trend: List[float] = []
    top_cost_vehicle: dict = {}
    
    class Config:
        from_attributes = True


class VehicleCostModel(BaseModel):
    """Schema for vehicle cost information."""
    vehicle_number: str
    cost: float
    cost_change: float


class MaintenanceAlert(BaseModel):
    """Schema for maintenance alert."""
    vehicle_id: str
    vehicle_number: str
    alert_type: str
    message: str
    urgency: str  # urgent, warning, info
    days_until: Optional[int] = None


class MaintenanceAlertsResponse(BaseModel):
    """Schema for maintenance alerts response."""
    alerts: List[MaintenanceAlert] = []
    total_count: int = 0
