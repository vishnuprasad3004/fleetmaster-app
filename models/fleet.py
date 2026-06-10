"""Fleet model."""

from sqlalchemy import Column, String, Text, ForeignKey, Integer, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.models.base import BaseModel


class FleetTier(str, enum.Enum):
    """Fleet subscription tier."""

    STARTUP = "startup"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class FleetStatus(str, enum.Enum):
    """Fleet status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Fleet(BaseModel):
    """Fleet model."""

    __tablename__ = "fleets"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    registration_number = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    total_vehicles = Column(Integer, default=0)
    total_drivers = Column(Integer, default=0)

    # Location
    country_code = Column(String(2), default="IN", nullable=False)
    state_code = Column(String(5), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)

    # Contact
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)

    # Branding
    logo_url = Column(String, nullable=True)

    # Settings
    settings = Column(JSON, default={})

    # Status
    status = Column(String(50), default=FleetStatus.ACTIVE.value)
    tier = Column(String(50), default=FleetTier.STARTUP.value)
    
    # Relationships
    owner = relationship("User", back_populates="fleets")
    vehicles = relationship("Vehicle", back_populates="fleet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Fleet {self.name}>"
    
    @property
    def active_vehicles_count(self):
        """Get count of active vehicles."""
        return len([v for v in self.vehicles if v.status == 'active']) if self.vehicles else 0
