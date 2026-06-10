"""Audit service for logging user actions."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import json

from app.models.auth import AuditLog


class AuditService:
    """Service for audit logging operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log a user action."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
    
    def get_user_audit_logs(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """Get audit logs for a specific user."""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    def get_resource_audit_logs(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> list[AuditLog]:
        """Get audit logs for a specific resource."""
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
