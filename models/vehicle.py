"""Vehicle model."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import BaseModel


class VehicleType(enum.Enum):
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


class VehicleStatus(enum.Enum):
    """Vehicle status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    SOLD = "sold"
    ACCIDENT = "accident"


class Vehicle(BaseModel):
    """Vehicle model."""

    __tablename__ = "vehicles"

    # Basic Info
    registration_number = Column(String(20), unique=True, nullable=False, index=True)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    variant = Column(String(100))
    year = Column(Integer)
    color = Column(String(50))
    engine_number = Column(String(50))
    chassis_number = Column(String(50), unique=True)
    
    # Technical Specifications
    fuel_type = Column(String(20))  # petrol, diesel, cng, electric
    fuel_capacity = Column(Float)  # liters
    mileage = Column(Float)  # km/liter
    engine_capacity = Column(Integer)  # cc
    max_load = Column(Float)  # tonnes
    seating_capacity = Column(Integer)
    
    # Purchase Info
    purchase_date = Column(DateTime(timezone=True))
    purchase_price = Column(Float)
    dealer_name = Column(String(255))
    finance_company = Column(String(255))
    loan_amount = Column(Float)
    emi_amount = Column(Float)
    loan_end_date = Column(DateTime(timezone=True))
    
    # Current Status
    status = Column(Enum(VehicleStatus), default=VehicleStatus.ACTIVE)
    current_odo = Column(Float, default=0)  # Current odometer reading in km
    last_service_odo = Column(Float)
    next_service_odo = Column(Float)
    
    # Relationships
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True)
    fleet_id = Column(UUID(as_uuid=True), ForeignKey("fleets.id"))
    current_driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="vehicles")
    company = relationship("Company", back_populates="vehicles")
    fleet = relationship("Fleet", back_populates="vehicles")
    current_driver = relationship("Driver", back_populates="assigned_vehicles")
    documents = relationship("VehicleDocument", back_populates="vehicle", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="vehicle", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle", cascade="all, delete-orphan")
    fuel_records = relationship("FuelRecord", back_populates="vehicle", cascade="all, delete-orphan")
    
    @property
    def is_document_expired(self):
        """Check if any critical documents are expired."""
        from datetime import datetime
        critical_docs = ['rc', 'insurance', 'permit', 'fitness', 'puc']
        
        for doc in self.documents:
            if doc.document_type in critical_docs and doc.expiry_date:
                if doc.expiry_date < datetime.utcnow():
                    return True
        return False
    
    @property
    def next_service_due_km(self):
        """Calculate kilometers remaining for next service."""
        if self.next_service_odo and self.current_odo:
            return max(0, self.next_service_odo - self.current_odo)
        return None
    
    @property
    def is_service_due(self):
        """Check if service is due."""
        if self.next_service_odo and self.current_odo:
            return self.current_odo >= self.next_service_odo
        return False


class VehicleDocument(BaseModel):
    """Vehicle document model."""

    __tablename__ = "vehicle_documents"

    # Document Info
    document_type = Column(String(50), nullable=False)  # rc, insurance, permit, fitness, puc, etc.
    document_number = Column(String(100))
    issuing_authority = Column(String(255))
    issue_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    document_url = Column(Text)  # S3 URL or file path
    notes = Column(Text)
    
    # Relationships
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    vehicle = relationship("Vehicle", back_populates="documents")
    
    @property
    def is_expired(self):
        """Check if document is expired."""
        from datetime import datetime
        return self.expiry_date and self.expiry_date < datetime.utcnow()
    
    @property
    def days_to_expiry(self):
        """Calculate days remaining until expiry."""
        if self.expiry_date:
            from datetime import datetime
            delta = self.expiry_date - datetime.utcnow()
            return delta.days
        return None
    
    @property
    def is_expiring_soon(self, days=30):
        """Check if document is expiring within specified days."""
        days_left = self.days_to_expiry
        return days_left is not None and 0 <= days_left <= days