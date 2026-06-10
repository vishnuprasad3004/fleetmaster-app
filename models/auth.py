"""Authentication and authorization models."""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, DateTime, Table, func, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import BaseModel


class Permission(BaseModel):
    """Permission model."""

    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    resource = Column(String(100), nullable=False)  # vehicles, drivers, trips, etc.
    action = Column(String(50), nullable=False)     # create, read, update, delete

    def __repr__(self):
        return f"<Permission {self.name}>"


class Role(BaseModel):
    """Role model."""

    __tablename__ = "roles"

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    hierarchy_level = Column(Integer, default=0)  # Lower = more privileged
    is_system_role = Column(Boolean, default=False)

    # Relationships
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"


# Association tables
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint('role_id', 'permission_id')
)

user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), nullable=False),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    UniqueConstraint('user_id', 'role_id')
)


class UserSession(BaseModel):
    """User session tracking for security."""

    __tablename__ = "user_sessions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="sessions")


class LoginAttempt(BaseModel):
    """Track login attempts for security."""

    __tablename__ = "login_attempts"

    email = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    success = Column(Boolean, default=False)
    failure_reason = Column(String(255))
    user_agent = Column(Text)

    class Config:
        indexes = [
            # Composite index for rate limiting
            ("email", "created_at"),
            ("ip_address", "created_at"),
        ]


class AuditLog(BaseModel):
    """Audit log for tracking user actions."""

    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(100), nullable=False)  # vehicles, drivers, trips, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    old_values = Column(Text)  # JSON string of old values
    new_values = Column(Text)  # JSON string of new values
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Relationships
    user = relationship("User")