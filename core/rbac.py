"""RBAC: roles, permissions, and authorization helpers."""

from __future__ import annotations

import uuid
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.models.auth import Permission, Role, role_permissions, user_roles
from app.models.company import CompanyMember, CompanyRole
from app.models.user import User

SYSTEM_ROLES = (
    ("owner", "Business owner", 0),
    ("admin", "Platform administrator", 0),
    ("fleet_manager", "Fleet operations manager", 10),
    ("driver", "Driver app user", 50),
)

RESOURCES = ("companies", "vehicles", "drivers", "users")
ACTIONS = ("create", "read", "update", "delete")

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {f"{r}:{a}" for r in RESOURCES for a in ACTIONS},
    "admin": {f"{r}:{a}" for r in RESOURCES for a in ACTIONS},
    "fleet_manager": {
        "vehicles:create", "vehicles:read", "vehicles:update", "vehicles:delete",
        "drivers:create", "drivers:read", "drivers:update", "drivers:delete",
        "companies:read",
    },
    "driver": {
        "vehicles:read",
        "drivers:read",
        "companies:read",
    },
}


def seed_rbac(db: Session) -> None:
    """Idempotently seed roles and permissions."""
    if db.query(Role).filter(Role.name == "owner").first():
        return

    role_by_name: dict[str, Role] = {}
    for name, desc, level in SYSTEM_ROLES:
        role = Role(
            id=uuid.uuid4(),
            name=name,
            description=desc,
            hierarchy_level=level,
            is_system_role=True,
        )
        db.add(role)
        role_by_name[name] = role
    db.flush()

    perm_by_name: dict[str, Permission] = {}
    for resource in RESOURCES:
        for action in ACTIONS:
            name = f"{resource}:{action}"
            perm = Permission(
                id=uuid.uuid4(),
                name=name,
                description=f"{action} {resource}",
                resource=resource,
                action=action,
            )
            db.add(perm)
            perm_by_name[name] = perm
    db.flush()

    for role_name, perm_names in ROLE_PERMISSIONS.items():
        role = role_by_name[role_name]
        for perm_name in perm_names:
            perm = perm_by_name[perm_name]
            db.execute(
                role_permissions.insert().values(
                    id=uuid.uuid4(),
                    role_id=role.id,
                    permission_id=perm.id,
                )
            )
    db.commit()


def assign_user_role(db: Session, user_id: str, role_name: str) -> None:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        return
    exists = (
        db.query(user_roles)
        .filter(user_roles.c.user_id == user_id, user_roles.c.role_id == role.id)
        .first()
    )
    if not exists:
        db.execute(
            user_roles.insert().values(id=uuid.uuid4(), user_id=user_id, role_id=role.id)
        )
        db.commit()


def get_company_role(db: Session, user_id: str, company_id: str) -> Optional[str]:
    member = (
        db.query(CompanyMember)
        .filter(
            CompanyMember.user_id == user_id,
            CompanyMember.company_id == company_id,
            CompanyMember.is_active.is_(True),
        )
        .first()
    )
    return member.role if member else None


def user_has_permission(
    db: Session,
    user: User,
    resource: str,
    action: str,
    company_id: Optional[str] = None,
) -> bool:
    """Check permission via global role and company membership."""
    perm_name = f"{resource}:{action}"

    for role in user.roles or []:
        if any(p.name == perm_name for p in role.permissions):
            return True

    cid = company_id or (str(user.active_company_id) if user.active_company_id else None)
    if cid:
        company_role = get_company_role(db, str(user.id), cid)
        if company_role:
            allowed = ROLE_PERMISSIONS.get(company_role, set())
            if perm_name in allowed:
                return True
            if company_role == CompanyRole.OWNER.value:
                return True

    return False


def require_company_access(db: Session, user: User, company_id: str) -> bool:
    if str(user.active_company_id) == company_id:
        return True
    return (
        db.query(CompanyMember)
        .filter(
            CompanyMember.user_id == user.id,
            CompanyMember.company_id == company_id,
            CompanyMember.is_active.is_(True),
        )
        .first()
        is not None
    )
