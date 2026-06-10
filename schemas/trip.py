"""Trip schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TripStatus(str, Enum):
    """Trip status enumeration."""
    PLANNED = "planned"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class TripType(str, Enum):
    """Trip type enumeration."""
    GOODS = "goods"
    PASSENGER = "passenger"
    EMPTY = "empty"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


# Trip Expense Schemas
class TripExpenseBase(BaseModel):
    """Base trip expense schema."""
    expense_type: str = Field(..., description="Type of expense")
    amount: float = Field(..., description="Expense amount")
    description: Optional[str] = Field(None, description="Expense description")
    receipt_url: Optional[str] = Field(None, description="Receipt image URL")
    location_name: Optional[str] = Field(None, description="Location name")
    latitude: Optional[float] = Field(None, description="Location latitude")
    longitude: Optional[float] = Field(None, description="Location longitude")


class TripExpenseCreate(TripExpenseBase):
    """Schema for creating trip expense."""
    trip_id: str = Field(..., description="Trip ID")


class TripExpenseResponse(TripExpenseBase):
    """Schema for trip expense response."""
    id: str
    trip_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# GPS Log Schemas
class TripGPSLogBase(BaseModel):
    """Base GPS log schema."""
    timestamp: datetime = Field(..., description="GPS timestamp")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    speed: Optional[float] = Field(None, description="Speed in km/h")
    heading: Optional[float] = Field(None, description="Heading in degrees")
    accuracy: Optional[float] = Field(None, description="GPS accuracy in meters")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    ignition_on: bool = Field(True, description="Ignition status")
    fuel_level: Optional[float] = Field(None, description="Fuel level percentage")
    odometer: Optional[float] = Field(None, description="Odometer reading in km")
    engine_rpm: Optional[int] = Field(None, description="Engine RPM")


class TripGPSLogCreate(TripGPSLogBase):
    """Schema for creating GPS log."""
    trip_id: str = Field(..., description="Trip ID")


class TripGPSLogResponse(TripGPSLogBase):
    """Schema for GPS log response."""
    id: str
    trip_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Trip Schemas
class TripBase(BaseModel):
    """Base trip schema."""
    trip_number: str = Field(..., description="Trip number")
    trip_type: TripType = Field(TripType.GOODS, description="Type of trip")
    status: TripStatus = Field(TripStatus.PLANNED, description="Trip status")
    
    # Route information
    origin_name: str = Field(..., description="Origin location name")
    origin_address: Optional[str] = Field(None, description="Origin address")
    origin_latitude: Optional[float] = Field(None, description="Origin latitude")
    origin_longitude: Optional[float] = Field(None, description="Origin longitude")
    destination_name: str = Field(..., description="Destination location name")
    destination_address: Optional[str] = Field(None, description="Destination address")
    destination_latitude: Optional[float] = Field(None, description="Destination latitude")
    destination_longitude: Optional[float] = Field(None, description="Destination longitude")
    
    # Timing
    planned_start_time: datetime = Field(..., description="Planned start time")
    planned_end_time: Optional[datetime] = Field(None, description="Planned end time")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    
    # Distance and route
    planned_distance: Optional[float] = Field(None, description="Planned distance in km")
    route_data: Optional[Dict[str, Any]] = Field(None, description="Route GPS data")
    
    # Load information
    cargo_type: Optional[str] = Field(None, description="Type of cargo")
    cargo_weight: Optional[float] = Field(None, description="Cargo weight in tonnes")
    cargo_value: Optional[float] = Field(None, description="Cargo value in INR")
    loading_instructions: Optional[str] = Field(None, description="Loading instructions")
    unloading_instructions: Optional[str] = Field(None, description="Unloading instructions")
    
    # Financial
    base_fare: float = Field(0, description="Base fare")
    fuel_cost: float = Field(0, description="Fuel cost")
    toll_cost: float = Field(0, description="Toll cost")
    driver_allowance: float = Field(0, description="Driver allowance")
    other_expenses: float = Field(0, description="Other expenses")
    revenue: float = Field(0, description="Total revenue")
    
    # Customer info
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    lr_number: Optional[str] = Field(None, description="Lorry Receipt number")
    notes: Optional[str] = Field(None, description="Additional notes")


class TripCreate(TripBase):
    """Schema for creating trip."""
    vehicle_id: str = Field(..., description="Vehicle ID")
    driver_id: str = Field(..., description="Driver ID")


class TripUpdate(BaseModel):
    """Schema for updating trip."""
    trip_number: Optional[str] = None
    trip_type: Optional[TripType] = None
    status: Optional[TripStatus] = None
    origin_name: Optional[str] = None
    origin_address: Optional[str] = None
    origin_latitude: Optional[float] = None
    origin_longitude: Optional[float] = None
    destination_name: Optional[str] = None
    destination_address: Optional[str] = None
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    planned_distance: Optional[float] = None
    actual_distance: Optional[float] = None
    route_data: Optional[Dict[str, Any]] = None
    cargo_type: Optional[str] = None
    cargo_weight: Optional[float] = None
    cargo_value: Optional[float] = None
    loading_instructions: Optional[str] = None
    unloading_instructions: Optional[str] = None
    base_fare: Optional[float] = None
    fuel_cost: Optional[float] = None
    toll_cost: Optional[float] = None
    driver_allowance: Optional[float] = None
    other_expenses: Optional[float] = None
    revenue: Optional[float] = None
    start_fuel_level: Optional[float] = None
    end_fuel_level: Optional[float] = None
    fuel_consumed: Optional[float] = None
    mileage: Optional[float] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    invoice_number: Optional[str] = None
    lr_number: Optional[str] = None
    notes: Optional[str] = None


class TripResponse(TripBase):
    """Schema for trip response."""
    id: str
    vehicle_id: str
    driver_id: str
    owner_id: str
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    actual_duration: Optional[int]
    actual_distance: Optional[float]
    total_cost: float
    profit: float
    start_fuel_level: Optional[float]
    end_fuel_level: Optional[float]
    fuel_consumed: Optional[float]
    mileage: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    # Calculated properties
    is_delayed: bool
    delay_minutes: float
    efficiency_score: float
    
    # Relationships
    expenses: List[TripExpenseResponse] = []
    gps_logs: List[TripGPSLogResponse] = []

    class Config:
        from_attributes = True


class TripListResponse(BaseModel):
    """Schema for trip list response."""
    trips: List[TripResponse]
    total: int
    skip: int
    limit: int


class TripStatsResponse(BaseModel):
    """Schema for trip statistics response."""
    total_trips: int
    completed_trips: int
    trips_in_progress: int
    cancelled_trips: int
    total_revenue: float
    total_costs: float
    total_profit: float
    total_distance: float
    avg_efficiency_score: float


class ProfitAnalysisResponse(BaseModel):
    """Schema for profit analysis response."""
    most_profitable_vehicle_id: Optional[str]
    most_profitable_amount: float
    least_profitable_vehicle_id: Optional[str]
    least_profitable_amount: float


# Maintenance Schemas
class MaintenanceRecordBase(BaseModel):
    """Base maintenance record schema."""
    maintenance_type: str = Field(..., description="Type of maintenance")
    service_type: Optional[str] = Field(None, description="Service type")
    description: str = Field(..., description="Maintenance description")
    odometer_reading: float = Field(..., description="Odometer reading at service")
    service_provider: Optional[str] = Field(None, description="Service provider")
    mechanic_name: Optional[str] = Field(None, description="Mechanic name")
    service_location: Optional[str] = Field(None, description="Service location")
    labor_cost: float = Field(0, description="Labor cost")
    parts_cost: float = Field(0, description="Parts cost")
    other_cost: float = Field(0, description="Other costs")
    total_cost: float = Field(..., description="Total maintenance cost")
    service_date: datetime = Field(..., description="Service date")
    next_service_date: Optional[datetime] = Field(None, description="Next service date")
    next_service_odometer: Optional[float] = Field(None, description="Next service odometer")
    bill_number: Optional[str] = Field(None, description="Bill number")
    bill_url: Optional[str] = Field(None, description="Bill image URL")
    parts_replaced: Optional[List[str]] = Field(None, description="Parts replaced")


class MaintenanceRecordCreate(MaintenanceRecordBase):
    """Schema for creating maintenance record."""
    vehicle_id: str = Field(..., description="Vehicle ID")


class MaintenanceRecordResponse(MaintenanceRecordBase):
    """Schema for maintenance record response."""
    id: str
    vehicle_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Fuel Schemas
class FuelRecordBase(BaseModel):
    """Base fuel record schema."""
    fuel_type: str = Field(..., description="Fuel type")
    quantity: float = Field(..., description="Fuel quantity in liters")
    rate_per_liter: float = Field(..., description="Rate per liter")
    total_amount: float = Field(..., description="Total amount")
    odometer_reading: float = Field(..., description="Odometer reading")
    fuel_level_before: Optional[float] = Field(None, description="Fuel level before filling")
    fuel_level_after: Optional[float] = Field(None, description="Fuel level after filling")
    station_name: Optional[str] = Field(None, description="Fuel station name")
    station_location: Optional[str] = Field(None, description="Station location")
    attendant_name: Optional[str] = Field(None, description="Attendant name")
    is_trip_fuel: bool = Field(False, description="Is this fuel for a trip")
    trip_id: Optional[str] = Field(None, description="Associated trip ID")
    receipt_number: Optional[str] = Field(None, description="Receipt number")
    receipt_url: Optional[str] = Field(None, description="Receipt image URL")


class FuelRecordCreate(FuelRecordBase):
    """Schema for creating fuel record."""
    vehicle_id: str = Field(..., description="Vehicle ID")


class FuelRecordResponse(FuelRecordBase):
    """Schema for fuel record response."""
    id: str
    vehicle_id: str
    created_at: datetime
    updated_at: datetime
    mileage: Optional[float]

    class Config:
        from_attributes = True


class FuelStatsResponse(BaseModel):
    """Schema for fuel statistics response."""
    total_refuels: int
    total_fuel_consumed: float
    total_fuel_cost: float
    avg_fuel_rate: float


class MaintenanceStatsResponse(BaseModel):
    """Schema for maintenance statistics response."""
    total_services: int
    total_maintenance_cost: float
    avg_cost_per_service: float