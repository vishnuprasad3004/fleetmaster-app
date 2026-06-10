"""Driver model."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from .base import BaseModel


class Driver(BaseModel):
    """Driver model."""

    __tablename__ = "drivers"

    # Personal Info
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    date_of_birth = Column(DateTime(timezone=True))
    phone_number = Column(String(20), nullable=False)
    alternate_phone = Column(String(20))
    email = Column(String(255))
    profile_picture_url = Column(Text)
    
    # Address
    current_address = Column(Text)
    permanent_address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # License Info
    license_number = Column(String(50), unique=True, nullable=False, index=True)
    license_type = Column(String(20))  # LMV, HMV, PSV, etc.
    license_issue_date = Column(DateTime(timezone=True))
    license_expiry_date = Column(DateTime(timezone=True))
    license_issuing_state = Column(String(100))
    license_document_url = Column(Text, nullable=True)
    
    # Employment Info
    joining_date = Column(DateTime(timezone=True), nullable=False)
    employment_type = Column(String(20), default="permanent")  # permanent, contract, daily
    salary_type = Column(String(20), default="monthly")  # monthly, daily, per_trip
    basic_salary = Column(Float, default=0)
    experience_years = Column(Integer, default=0)
    previous_company = Column(String(255))
    
    # Emergency Contact
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(100))
    
    # Bank Details
    bank_account_number = Column(String(50))
    bank_ifsc_code = Column(String(20))
    bank_name = Column(String(255))
    bank_branch = Column(String(255))
    
    # Status
    status = Column(String(20), default="active")  # active, inactive, suspended, terminated
    termination_date = Column(DateTime(timezone=True))
    termination_reason = Column(Text)
    
    # Performance Metrics (calculated fields)
    total_trips = Column(Integer, default=0)
    total_distance = Column(Float, default=0)  # km
    avg_rating = Column(Float, default=0)
    total_earnings = Column(Float, default=0)
    
    # Relationships
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True)
    
    # Relationships
    owner = relationship("User", back_populates="drivers")
    company = relationship("Company", back_populates="drivers")
    assigned_vehicles = relationship("Vehicle", back_populates="current_driver")
    trips = relationship("Trip", back_populates="driver", cascade="all, delete-orphan")
    attendance_records = relationship("DriverAttendance", back_populates="driver", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """Get driver's full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def age(self):
        """Calculate driver's age."""
        if self.date_of_birth:
            today = datetime.utcnow()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    @property
    def is_license_expired(self):
        """Check if license is expired."""
        return self.license_expiry_date and self.license_expiry_date < datetime.utcnow()
    
    @property
    def license_days_to_expiry(self):
        """Calculate days remaining until license expiry."""
        if self.license_expiry_date:
            delta = self.license_expiry_date - datetime.utcnow()
            return delta.days
        return None
    
    @property
    def is_license_expiring_soon(self, days=30):
        """Check if license is expiring within specified days."""
        days_left = self.license_days_to_expiry
        return days_left is not None and 0 <= days_left <= days
    
    @property
    def current_vehicle_registration(self):
        """Get current assigned vehicle registration number."""
        if self.assigned_vehicles:
            return self.assigned_vehicles[0].registration_number  # Assuming one vehicle per driver
        return None


class DriverAttendance(BaseModel):
    """Driver attendance model."""

    __tablename__ = "driver_attendance"

    # Attendance Info
    date = Column(DateTime(timezone=True), nullable=False)
    check_in_time = Column(DateTime(timezone=True))
    check_out_time = Column(DateTime(timezone=True))
    total_hours = Column(Float, default=0)
    overtime_hours = Column(Float, default=0)
    status = Column(String(20), default="present")  # present, absent, half_day, late, on_leave
    notes = Column(Text)
    
    # Location (if GPS tracking enabled)
    check_in_latitude = Column(Float)
    check_in_longitude = Column(Float)
    check_out_latitude = Column(Float)
    check_out_longitude = Column(Float)
    
    # Relationships
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    driver = relationship("Driver", back_populates="attendance_records")
    
    @property
    def is_overtime(self):
        """Check if driver worked overtime."""
        return self.overtime_hours > 0
    
    @property
    def worked_hours(self):
        """Calculate total worked hours."""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            return delta.total_seconds() / 3600  # Convert to hours
        return 0