"""Fuel models for tracking fuel logs and analytics."""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class FuelType(str, enum.Enum):
    """Types of fuel."""
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class FuelLog(Base):
    """Fuel log entries for vehicles."""
    
    __tablename__ = "fuel_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String(36), ForeignKey("vehicles.id"), nullable=False, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=True, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Fuel details
    date = Column(DateTime, nullable=False, index=True)
    fuel_type = Column(SQLEnum(FuelType), nullable=False, default=FuelType.DIESEL)
    quantity = Column(Float, nullable=False, default=0.0)  # in liters
    cost_per_liter = Column(Float, nullable=False, default=0.0)
    total_cost = Column(Float, nullable=False, default=0.0)
    
    # Vehicle details at time of fueling
    odometer_reading = Column(Integer, nullable=True)
    
    # Fuel station details
    fuel_station_name = Column(String(255), nullable=True)
    fuel_station_location = Column(String(255), nullable=True)
    fuel_station_contact = Column(String(50), nullable=True)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    company = relationship("Company", back_populates="fuel_logs")
    driver = relationship("Driver", back_populates="fuel_logs")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<FuelLog(id={self.id}, vehicle_id={self.vehicle_id}, date={self.date}, quantity={self.quantity})>"
