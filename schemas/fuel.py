"""Fuel schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class FuelType(str, Enum):
    """Types of fuel."""
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class FuelLogCreate(BaseModel):
    """Schema for creating a fuel log."""
    vehicle_id: str
    date: datetime
    fuel_type: FuelType
    quantity: float = Field(..., gt=0)
    cost_per_liter: float = Field(..., ge=0)
    odometer_reading: Optional[int] = Field(None, ge=0)
    fuel_station_name: Optional[str] = Field(None, max_length=255)
    fuel_station_location: Optional[str] = Field(None, max_length=255)
    fuel_station_contact: Optional[str] = Field(None, max_length=50)
    driver_id: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('total_cost', pre=True, always=True)
    def calculate_total_cost(cls, v, values):
        """Calculate total cost from quantity and cost per liter."""
        if 'quantity' in values and 'cost_per_liter' in values:
            return values['quantity'] * values['cost_per_liter']
        return 0.0


class FuelLogUpdate(BaseModel):
    """Schema for updating a fuel log."""
    date: Optional[datetime] = None
    fuel_type: Optional[FuelType] = None
    quantity: Optional[float] = Field(None, gt=0)
    cost_per_liter: Optional[float] = Field(None, ge=0)
    odometer_reading: Optional[int] = Field(None, ge=0)
    fuel_station_name: Optional[str] = Field(None, max_length=255)
    fuel_station_location: Optional[str] = Field(None, max_length=255)
    fuel_station_contact: Optional[str] = Field(None, max_length=50)
    driver_id: Optional[str] = None
    notes: Optional[str] = None


class FuelLogResponse(BaseModel):
    """Schema for fuel log response."""
    id: str
    vehicle_id: str
    vehicle_number: Optional[str] = None
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    date: datetime
    fuel_type: FuelType
    quantity: float
    cost_per_liter: float
    total_cost: float
    odometer_reading: Optional[int]
    fuel_station_name: Optional[str]
    fuel_station_location: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FuelDashboardResponse(BaseModel):
    """Schema for fuel dashboard response."""
    total_fuel_cost: float = 0.0
    total_quantity: float = 0.0
    average_mileage: float = 0.0
    cost_per_km: float = 0.0
    best_mileage_vehicle: dict = {}
    worst_mileage_vehicle: dict = {}
    cost_trend: List[float] = []
    
    class Config:
        from_attributes = True


class VehicleFuelModel(BaseModel):
    """Schema for vehicle fuel information."""
    vehicle_id: str
    vehicle_number: str
    total_fuel_cost: float
    total_quantity: float
    average_mileage: float
    cost_per_km: float


class VehicleFuelAnalyticsResponse(BaseModel):
    """Schema for vehicle fuel analytics response."""
    vehicle_id: str
    vehicle_number: str
    total_fuel_cost: float
    total_quantity: float
    average_mileage: float
    cost_per_km: float
    fuel_logs: List[FuelLogResponse] = []
    mileage_trend: List[float] = []
    cost_trend: List[float] = []
    
    class Config:
        from_attributes = True


class CostPerKMResponse(BaseModel):
    """Schema for cost per KM analysis."""
    vehicle_id: str
    vehicle_number: str
    cost_per_km: float
    fuel_cost_per_km: float
    maintenance_cost_per_km: float
    total_cost_per_km: float
