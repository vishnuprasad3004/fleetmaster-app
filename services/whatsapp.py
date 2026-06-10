"""WhatsApp service for business logic."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.whatsapp import WhatsAppConfig, WhatsAppAlertRule, DailySummaryConfig, AlertType
from app.models.company import Company
from app.schemas.whatsapp import (
    WhatsAppConfigCreate, WhatsAppConfigUpdate, WhatsAppConfigResponse,
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    DailySummaryConfigCreate, DailySummaryConfigUpdate, DailySummaryConfigResponse
)


class WhatsAppService:
    """Service for WhatsApp operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_config(self, company_id: str, user_id: str) -> WhatsAppConfig:
        """Get or create WhatsApp configuration for a company."""
        config = self.db.query(WhatsAppConfig).filter(
            WhatsAppConfig.company_id == company_id
        ).first()
        
        if not config:
            config = WhatsAppConfig(
                company_id=company_id,
                created_by=user_id,
                is_enabled=False,
                daily_summary_enabled=True,
                daily_summary_time="09:00",
                alerts_enabled=True
            )
            self.db.add(config)
            self.db.flush()
            
            # Create default alert rules
            default_alerts = [
                AlertType.INSURANCE_EXPIRY,
                AlertType.PERMIT_EXPIRY,
                AlertType.PUC_EXPIRY,
                AlertType.SERVICE_DUE,
                AlertType.PAYMENT_OVERDUE,
                AlertType.DRIVER_LICENSE_EXPIRY,
                AlertType.VEHICLE_OFFLINE
            ]
            
            for alert_type in default_alerts:
                alert_rule = WhatsAppAlertRule(
                    config_id=config.id,
                    alert_type=alert_type.value,
                    is_enabled=True,
                    notify_days_before=7
                )
                self.db.add(alert_rule)
            
            # Create default daily summary config
            daily_summary = DailySummaryConfig(
                config_id=config.id,
                include_revenue=True,
                include_expenses=True,
                include_profit=True,
                include_outstanding_payments=True,
                include_active_vehicles=True,
                include_critical_alerts=True
            )
            self.db.add(daily_summary)
            
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    def update_config(
        self,
        company_id: str,
        config_data: WhatsAppConfigUpdate
    ) -> Optional[WhatsAppConfig]:
        """Update WhatsApp configuration."""
        config = self.db.query(WhatsAppConfig).filter(
            WhatsAppConfig.company_id == company_id
        ).first()
        
        if not config:
            return None
        
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def get_config(self, company_id: str) -> Optional[WhatsAppConfig]:
        """Get WhatsApp configuration for a company."""
        return self.db.query(WhatsAppConfig).filter(
            WhatsAppConfig.company_id == company_id
        ).first()
    
    def get_alert_rules(self, company_id: str) -> List[WhatsAppAlertRule]:
        """Get all alert rules for a company."""
        config = self.get_config(company_id)
        if not config:
            return []
        
        return self.db.query(WhatsAppAlertRule).filter(
            WhatsAppAlertRule.config_id == config.id
        ).all()
    
    def update_alert_rule(
        self,
        company_id: str,
        alert_type: str,
        rule_data: AlertRuleUpdate
    ) -> Optional[WhatsAppAlertRule]:
        """Update an alert rule."""
        config = self.get_config(company_id)
        if not config:
            return None
        
        alert_rule = self.db.query(WhatsAppAlertRule).filter(
            WhatsAppAlertRule.config_id == config.id,
            WhatsAppAlertRule.alert_type == alert_type
        ).first()
        
        if not alert_rule:
            return None
        
        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(alert_rule, field):
                setattr(alert_rule, field, value)
        
        self.db.commit()
        self.db.refresh(alert_rule)
        return alert_rule
    
    def get_daily_summary_config(self, company_id: str) -> Optional[DailySummaryConfig]:
        """Get daily summary configuration for a company."""
        config = self.get_config(company_id)
        if not config:
            return None
        
        return self.db.query(DailySummaryConfig).filter(
            DailySummaryConfig.config_id == config.id
        ).first()
    
    def update_daily_summary_config(
        self,
        company_id: str,
        summary_data: DailySummaryConfigUpdate
    ) -> Optional[DailySummaryConfig]:
        """Update daily summary configuration."""
        config = self.get_config(company_id)
        if not config:
            return None
        
        daily_summary = self.db.query(DailySummaryConfig).filter(
            DailySummaryConfig.config_id == config.id
        ).first()
        
        if not daily_summary:
            daily_summary = DailySummaryConfig(config_id=config.id)
            self.db.add(daily_summary)
        
        update_data = summary_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(daily_summary, field):
                setattr(daily_summary, field, value)
        
        self.db.commit()
        self.db.refresh(daily_summary)
        return daily_summary
    
    def send_message(self, phone_number: str, message: str) -> dict:
        """Send a WhatsApp message (placeholder for actual API integration)."""
        # In production, this would integrate with WhatsApp Business API
        # For now, return a mock response
        return {
            "success": True,
            "message_id": "mock_message_id",
            "error": None
        }
    
    def send_daily_summary(self, company_id: str) -> dict:
        """Send daily summary to configured phone number."""
        config = self.get_config(company_id)
        if not config or not config.is_enabled or not config.phone_number:
            return {
                "success": False,
                "error": "WhatsApp not configured or enabled"
            }
        
        # In production, this would:
        # 1. Fetch daily summary data
        # 2. Format the message
        # 3. Send via WhatsApp API
        
        return {
            "success": True,
            "message_id": "mock_daily_summary_id",
            "error": None
        }
    
    def send_alert(self, company_id: str, alert_type: str, message: str, phone_number: Optional[str] = None) -> dict:
        """Send an alert notification."""
        config = self.get_config(company_id)
        if not config or not config.is_enabled:
            return {
                "success": False,
                "error": "WhatsApp not configured or enabled"
            }
        
        if not config.alerts_enabled:
            return {
                "success": False,
                "error": "Alerts not enabled"
            }
        
        # Check if this alert type is enabled
        alert_rule = self.db.query(WhatsAppAlertRule).filter(
            WhatsAppAlertRule.config_id == config.id,
            WhatsAppAlertRule.alert_type == alert_type,
            WhatsAppAlertRule.is_enabled == True
        ).first()
        
        if not alert_rule:
            return {
                "success": False,
                "error": "Alert type not enabled"
            }
        
        target_phone = phone_number or config.phone_number
        if not target_phone:
            return {
                "success": False,
                "error": "No phone number configured"
            }
        
        # In production, this would send via WhatsApp API
        return {
            "success": True,
            "message_id": "mock_alert_id",
            "error": None
        }
