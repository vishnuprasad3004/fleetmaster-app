"""WhatsApp schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class AlertType(str, Enum):
    """Types of alerts for WhatsApp notifications."""
    INSURANCE_EXPIRY = "insurance_expiry"
    PERMIT_EXPIRY = "permit_expiry"
    PUC_EXPIRY = "puc_expiry"
    SERVICE_DUE = "service_due"
    PAYMENT_OVERDUE = "payment_overdue"
    DRIVER_LICENSE_EXPIRY = "driver_license_expiry"
    VEHICLE_OFFLINE = "vehicle_offline"


class WhatsAppConfigCreate(BaseModel):
    """Schema for creating WhatsApp configuration."""
    phone_number: Optional[str] = Field(None, max_length=20)
    is_enabled: bool = False
    daily_summary_enabled: bool = True
    daily_summary_time: str = Field("09:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    alerts_enabled: bool = True


class WhatsAppConfigUpdate(BaseModel):
    """Schema for updating WhatsApp configuration."""
    phone_number: Optional[str] = Field(None, max_length=20)
    is_enabled: Optional[bool] = None
    daily_summary_enabled: Optional[bool] = None
    daily_summary_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    alerts_enabled: Optional[bool] = None


class WhatsAppConfigResponse(BaseModel):
    """Schema for WhatsApp configuration response."""
    id: str
    company_id: str
    phone_number: Optional[str]
    is_enabled: bool
    daily_summary_enabled: bool
    daily_summary_time: str
    alerts_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertRuleCreate(BaseModel):
    """Schema for creating an alert rule."""
    alert_type: AlertType
    is_enabled: bool = True
    notify_days_before: int = Field(7, ge=0, le=365)


class AlertRuleUpdate(BaseModel):
    """Schema for updating an alert rule."""
    is_enabled: Optional[bool] = None
    notify_days_before: Optional[int] = Field(None, ge=0, le=365)


class AlertRuleResponse(BaseModel):
    """Schema for alert rule response."""
    id: str
    config_id: str
    alert_type: str
    is_enabled: bool
    notify_days_before: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DailySummaryConfigCreate(BaseModel):
    """Schema for creating daily summary configuration."""
    include_revenue: bool = True
    include_expenses: bool = True
    include_profit: bool = True
    include_outstanding_payments: bool = True
    include_active_vehicles: bool = True
    include_critical_alerts: bool = True


class DailySummaryConfigUpdate(BaseModel):
    """Schema for updating daily summary configuration."""
    include_revenue: Optional[bool] = None
    include_expenses: Optional[bool] = None
    include_profit: Optional[bool] = None
    include_outstanding_payments: Optional[bool] = None
    include_active_vehicles: Optional[bool] = None
    include_critical_alerts: Optional[bool] = None


class DailySummaryConfigResponse(BaseModel):
    """Schema for daily summary configuration response."""
    id: str
    config_id: str
    include_revenue: bool
    include_expenses: bool
    include_profit: bool
    include_outstanding_payments: bool
    include_active_vehicles: bool
    include_critical_alerts: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WhatsAppMessageSend(BaseModel):
    """Schema for sending a WhatsApp message."""
    phone_number: str = Field(..., max_length=20)
    message: str = Field(..., min_length=1, max_length=1000)


class WhatsAppMessageResponse(BaseModel):
    """Schema for WhatsApp message response."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class DailySummarySend(BaseModel):
    """Schema for sending daily summary."""
    company_id: str


class AlertSend(BaseModel):
    """Schema for sending an alert."""
    company_id: str
    alert_type: AlertType
    message: str = Field(..., min_length=1, max_length=500)
    phone_number: Optional[str] = None
