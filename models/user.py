"""User model."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ARRAY, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum

from app.models.base import BaseModel


class UserStatus(str, enum.Enum):
    """User status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    profile_picture_url = Column(Text, nullable=True)

    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)

    phone_verified = Column(Boolean, default=False)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)

    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32), nullable=True)
    two_factor_backup_codes = Column(ARRAY(Text))

    last_login_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default=UserStatus.ACTIVE.value, nullable=False)
    
    # Business info
    business_name = Column(String(255))
    business_type = Column(String(100))  # logistics, taxi, goods, etc.
    gst_number = Column(String(50))
    pan_number = Column(String(20))
    
    # Address
    country_code = Column(String(2), default="IN")
    state_code = Column(String(5))
    city = Column(String(100))
    address = Column(Text)
    pincode = Column(String(10))

    active_company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)

    # Relationships
    fleets = relationship("Fleet", back_populates="owner", cascade="all, delete-orphan")
    owned_companies = relationship(
        "Company",
        back_populates="owner",
        foreign_keys="Company.owner_id",
        cascade="all, delete-orphan",
    )
    company_memberships = relationship(
        "CompanyMember",
        back_populates="user",
        foreign_keys="CompanyMember.user_id",
        cascade="all, delete-orphan",
    )
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    drivers = relationship("Driver", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def is_active(self):
        return self.status == UserStatus.ACTIVE.value

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username
    
    @property
    def total_vehicles(self):
        """Get total number of vehicles."""
        return len(self.vehicles) if self.vehicles else 0
    
    @property
    def total_drivers(self):
        """Get total number of drivers."""
        return len(self.drivers) if self.drivers else 0
