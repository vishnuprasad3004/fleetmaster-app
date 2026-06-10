"""Maintenance models for tracking service and repair records."""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class MaintenanceType(str, enum.Enum):
    """Types of maintenance records."""
    SERVICE = "service"
    REPAIR = "repair"
    INSPECTION = "inspection"
    TYRE_REPLACEMENT = "tyre_replacement"
    BATTERY_REPLACEMENT = "battery_replacement"
    OIL_CHANGE = "oil_change"
    OTHER = "other"


class MaintenanceRecord(Base):
    """Maintenance and repair records for vehicles."""
    
    __tablename__ = "maintenance_records"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String(36), ForeignKey("vehicles.id"), nullable=False, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Maintenance details
    type = Column(SQLEnum(MaintenanceType), nullable=False, default=MaintenanceType.SERVICE)
    date = Column(DateTime, nullable=False, index=True)
    cost = Column(Float, nullable=False, default=0.0)
    
    # Workshop details
    workshop_name = Column(String(255), nullable=True)
    workshop_contact = Column(String(50), nullable=True)
    workshop_address = Column(Text, nullable=True)
    
    # Vehicle details at time of service
    odometer_reading = Column(Integer, nullable=True)
    
    # Description and notes
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Spare parts (stored as JSON)
    spare_parts = Column(JSON, nullable=True, default=list)
    
    # Next service scheduling
    next_service_date = Column(DateTime, nullable=True)
    next_service_odometer = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    company = relationship("Company", back_populates="maintenance_records")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<MaintenanceRecord(id={self.id}, vehicle_id={self.vehicle_id}, type={self.type}, date={self.date})>"


class SparePart(Base):
    """Spare parts used in maintenance."""
    
    __tablename__ = "spare_parts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    maintenance_record_id = Column(String(36), ForeignKey("maintenance_records.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    part_number = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    cost_per_unit = Column(Float, nullable=False, default=0.0)
    total_cost = Column(Float, nullable=False, default=0.0)
    
    # Supplier details
    supplier_name = Column(String(255), nullable=True)
    supplier_contact = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SparePart(id={self.id}, name={self.name}, quantity={self.quantity})>"
