"""WhatsApp models for configuration and alerts."""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class AlertType(str, enum.Enum):
    """Types of alerts for WhatsApp notifications."""
    INSURANCE_EXPIRY = "insurance_expiry"
    PERMIT_EXPIRY = "permit_expiry"
    PUC_EXPIRY = "puc_expiry"
    SERVICE_DUE = "service_due"
    PAYMENT_OVERDUE = "payment_overdue"
    DRIVER_LICENSE_EXPIRY = "driver_license_expiry"
    VEHICLE_OFFLINE = "vehicle_offline"


class WhatsAppConfig(Base):
    """WhatsApp configuration for a company."""
    
    __tablename__ = "whatsapp_configs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, unique=True, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Configuration
    phone_number = Column(String(20), nullable=True)
    is_enabled = Column(Boolean, default=False)
    
    # Daily summary settings
    daily_summary_enabled = Column(Boolean, default=True)
    daily_summary_time = Column(String(10), default="09:00")  # HH:MM format
    
    # Alert settings
    alerts_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="whatsapp_config")
    creator = relationship("User", foreign_keys=[created_by])
    alert_rules = relationship("WhatsAppAlertRule", back_populates="config", cascade="all, delete-orphan")
    daily_summary_config = relationship("DailySummaryConfig", back_populates="config", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WhatsAppConfig(id={self.id}, company_id={self.company_id}, phone_number={self.phone_number})>"


class WhatsAppAlertRule(Base):
    """Alert rules for WhatsApp notifications."""
    
    __tablename__ = "whatsapp_alert_rules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_id = Column(String(36), ForeignKey("whatsapp_configs.id"), nullable=False, index=True)
    
    # Alert configuration
    alert_type = Column(String(50), nullable=False)
    is_enabled = Column(Boolean, default=True)
    
    # Notification timing (days before expiry)
    notify_days_before = Column(Integer, default=7)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    config = relationship("WhatsAppConfig", back_populates="alert_rules")
    
    def __repr__(self):
        return f"<WhatsAppAlertRule(id={self.id}, alert_type={self.alert_type}, is_enabled={self.is_enabled})>"


class DailySummaryConfig(Base):
    """Daily summary configuration for WhatsApp."""
    
    __tablename__ = "daily_summary_configs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_id = Column(String(36), ForeignKey("whatsapp_configs.id"), nullable=False, unique=True, index=True)
    
    # Summary content settings
    include_revenue = Column(Boolean, default=True)
    include_expenses = Column(Boolean, default=True)
    include_profit = Column(Boolean, default=True)
    include_outstanding_payments = Column(Boolean, default=True)
    include_active_vehicles = Column(Boolean, default=True)
    include_critical_alerts = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    config = relationship("WhatsAppConfig", back_populates="daily_summary_config")
    
    def __repr__(self):
        return f"<DailySummaryConfig(id={self.id}, config_id={self.config_id})>"
