"""Company repository."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.company import Company, CompanyMember, CompanyRole
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db: Session):
        super().__init__(db, Company)

    def get_by_owner(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Company]:
        return (
            self.db.query(Company)
            .filter(Company.owner_id == owner_id, Company.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_companies(self, user_id: str) -> List[Company]:
        return (
            self.db.query(Company)
            .outerjoin(
                CompanyMember,
                (CompanyMember.company_id == Company.id) & (CompanyMember.user_id == user_id),
            )
            .filter(
                Company.deleted_at.is_(None),
                (Company.owner_id == user_id) | (CompanyMember.is_active.is_(True)),
            )
            .distinct()
            .all()
        )


class CompanyMemberRepository(BaseRepository[CompanyMember]):
    def __init__(self, db: Session):
        super().__init__(db, CompanyMember)

    def add_member(
        self,
        company_id: str,
        user_id: str,
        role: str = CompanyRole.OWNER.value,
        invited_by_id: Optional[str] = None,
    ) -> CompanyMember:
        member = CompanyMember(
            company_id=company_id,
            user_id=user_id,
            role=role,
            invited_by_id=invited_by_id,
        )
        self.db.add(member)
        self.db.flush()
        return member

    def get_membership(self, company_id: str, user_id: str) -> Optional[CompanyMember]:
        return (
            self.db.query(CompanyMember)
            .filter(
                CompanyMember.company_id == company_id,
                CompanyMember.user_id == user_id,
                CompanyMember.is_active.is_(True),
            )
            .first()
        )
