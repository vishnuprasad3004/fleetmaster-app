"""Company (tenant) models for multi-tenant SaaS."""

import enum

from sqlalchemy import Boolean, Column, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CompanyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CompanyRole(str, enum.Enum):
    """Member role within a company."""

    OWNER = "owner"
    FLEET_MANAGER = "fleet_manager"
    DRIVER = "driver"
    ADMIN = "admin"


class Company(BaseModel):
    """Transport business tenant."""

    __tablename__ = "companies"

    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255), nullable=True)
    gst_number = Column(String(15), nullable=True, index=True)
    pan_number = Column(String(10), nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)

    address_line1 = Column(Text, nullable=True)
    address_line2 = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state_code = Column(String(5), nullable=True)
    pincode = Column(String(10), nullable=True)
    country_code = Column(String(2), default="IN", nullable=False)

    logo_url = Column(Text, nullable=True)
    settings = Column(JSON, default=dict, nullable=False)
    status = Column(String(50), default=CompanyStatus.ACTIVE.value, nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    owner = relationship("User", back_populates="owned_companies", foreign_keys=[owner_id])
    members = relationship("CompanyMember", back_populates="company", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="company")
    drivers = relationship("Driver", back_populates="company")
    audit_logs = relationship("AuditLog", back_populates="company", cascade="all, delete-orphan")
    whatsapp_config = relationship("WhatsAppConfig", back_populates="company", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company {self.name}>"


class CompanyMember(BaseModel):
    """User membership in a company with RBAC role."""

    __tablename__ = "company_members"
    __table_args__ = (UniqueConstraint("company_id", "user_id", name="uq_company_user"),)

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False, default=CompanyRole.OWNER.value)
    is_active = Column(Boolean, default=True, nullable=False)
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    company = relationship("Company", back_populates="members")
    user = relationship("User", back_populates="company_memberships", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<CompanyMember {self.user_id}@{self.company_id} role={self.role}>"
