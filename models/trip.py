"""Trip and related models."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

from .base import BaseModel


class TripStatus(enum.Enum):
    """Trip status enumeration."""
    PLANNED = "planned"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class TripType(enum.Enum):
    """Trip type enumeration."""
    GOODS = "goods"
    PASSENGER = "passenger"
    EMPTY = "empty"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


class Trip(BaseModel):
    """Trip model."""

    __tablename__ = "trips"

    # Trip Identification
    trip_number = Column(String(50), unique=True, nullable=False, index=True)
    trip_type = Column(Enum(TripType), default=TripType.GOODS)
    status = Column(Enum(TripStatus), default=TripStatus.PLANNED)
    
    # Route Information
    origin_name = Column(String(255), nullable=False)
    origin_address = Column(Text)
    origin_latitude = Column(Float)
    origin_longitude = Column(Float)
    
    destination_name = Column(String(255), nullable=False)
    destination_address = Column(Text)
    destination_latitude = Column(Float)
    destination_longitude = Column(Float)
    
    # Timing
    planned_start_time = Column(DateTime(timezone=True), nullable=False)
    planned_end_time = Column(DateTime(timezone=True))
    actual_start_time = Column(DateTime(timezone=True))
    actual_end_time = Column(DateTime(timezone=True))
    estimated_duration = Column(Integer)  # minutes
    actual_duration = Column(Integer)  # minutes
    
    # Distance and Route
    planned_distance = Column(Float)  # km
    actual_distance = Column(Float)  # km
    route_data = Column(JSON)  # Store GPS route points
    
    # Load Information
    cargo_type = Column(String(100))
    cargo_weight = Column(Float)  # tonnes
    cargo_value = Column(Float)  # INR
    loading_instructions = Column(Text)
    unloading_instructions = Column(Text)
    
    # Financial
    base_fare = Column(Float, default=0)
    fuel_cost = Column(Float, default=0)
    toll_cost = Column(Float, default=0)
    driver_allowance = Column(Float, default=0)
    other_expenses = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    revenue = Column(Float, default=0)
    profit = Column(Float, default=0)
    
    # Fuel
    start_fuel_level = Column(Float)  # %
    end_fuel_level = Column(Float)  # %
    fuel_consumed = Column(Float)  # liters
    mileage = Column(Float)  # km/liter
    
    # Additional Info
    customer_name = Column(String(255))
    customer_phone = Column(String(20))
    invoice_number = Column(String(50))
    lr_number = Column(String(50))  # Lorry Receipt number
    notes = Column(Text)
    
    # Relationships
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    owner = relationship("User")
    gps_logs = relationship("TripGPSLog", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("TripExpense", back_populates="trip", cascade="all, delete-orphan")
    
    @property
    def is_delayed(self):
        """Check if trip is delayed."""
        if self.status == TripStatus.STARTED and self.planned_start_time:
            return datetime.utcnow() > self.planned_start_time
        return False
    
    @property
    def delay_minutes(self):
        """Calculate delay in minutes."""
        if self.actual_start_time and self.planned_start_time:
            delta = self.actual_start_time - self.planned_start_time
            return max(0, delta.total_seconds() / 60)
        return 0
    
    @property
    def efficiency_score(self):
        """Calculate trip efficiency score (0-100)."""
        score = 100
        
        # Deduct for delays
        if self.delay_minutes > 0:
            score -= min(30, self.delay_minutes)  # Max 30 points deduction
        
        # Deduct for fuel efficiency
        if self.mileage and self.vehicle.mileage:
            efficiency_ratio = self.mileage / self.vehicle.mileage
            if efficiency_ratio < 1:
                score -= (1 - efficiency_ratio) * 20  # Max 20 points deduction
        
        return max(0, score)


class TripGPSLog(BaseModel):
    """GPS tracking log for trips."""

    __tablename__ = "trip_gps_logs"

    # GPS Data
    timestamp = Column(DateTime(timezone=True), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float)  # km/h
    heading = Column(Float)  # degrees
    accuracy = Column(Float)  # meters
    altitude = Column(Float)  # meters
    
    # Vehicle Status
    ignition_on = Column(Boolean, default=True)
    fuel_level = Column(Float)  # %
    odometer = Column(Float)  # km
    engine_rpm = Column(Integer)
    
    # Relationships
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    trip = relationship("Trip", back_populates="gps_logs")


class TripExpense(BaseModel):
    """Trip-specific expenses."""

    __tablename__ = "trip_expenses"

    # Expense Details
    expense_type = Column(String(50), nullable=False)  # fuel, toll, parking, food, etc.
    amount = Column(Float, nullable=False)
    description = Column(Text)
    receipt_url = Column(Text)  # Receipt image/PDF URL
    
    # Location
    location_name = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    trip = relationship("Trip", back_populates="expenses")


class MaintenanceRecord(BaseModel):
    """Vehicle maintenance records."""

    __tablename__ = "maintenance_records"

    # Maintenance Info
    maintenance_type = Column(String(50), nullable=False)  # service, repair, inspection
    service_type = Column(String(100))  # oil_change, brake_service, etc.
    description = Column(Text, nullable=False)
    odometer_reading = Column(Float, nullable=False)
    
    # Service Provider
    service_provider = Column(String(255))
    mechanic_name = Column(String(255))
    service_location = Column(String(255))
    
    # Cost
    labor_cost = Column(Float, default=0)
    parts_cost = Column(Float, default=0)
    other_cost = Column(Float, default=0)
    total_cost = Column(Float, nullable=False)
    
    # Dates
    service_date = Column(DateTime(timezone=True), nullable=False)
    next_service_date = Column(DateTime(timezone=True))
    next_service_odometer = Column(Float)
    
    # Documentation
    bill_number = Column(String(100))
    bill_url = Column(Text)  # Bill/receipt image URL
    parts_replaced = Column(JSON)  # List of parts replaced
    
    # Relationships
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    vehicle = relationship("Vehicle", back_populates="maintenance_records")


class FuelRecord(BaseModel):
    """Fuel consumption records."""

    __tablename__ = "fuel_records"

    # Fuel Info
    fuel_type = Column(String(20), nullable=False)  # petrol, diesel, cng
    quantity = Column(Float, nullable=False)  # liters
    rate_per_liter = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Vehicle Status
    odometer_reading = Column(Float, nullable=False)
    fuel_level_before = Column(Float)  # %
    fuel_level_after = Column(Float)  # %
    
    # Station Info
    station_name = Column(String(255))
    station_location = Column(String(255))
    attendant_name = Column(String(255))
    
    # Trip Association
    is_trip_fuel = Column(Boolean, default=False)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=True)
    
    # Documentation
    receipt_number = Column(String(100))
    receipt_url = Column(Text)
    
    # Relationships
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    vehicle = relationship("Vehicle", back_populates="fuel_records")
    trip = relationship("Trip")
    
    @property
    def mileage(self):
        """Calculate mileage if possible."""
        # This would require previous fuel record to calculate
        return None  # TODO: Implement based on business logic