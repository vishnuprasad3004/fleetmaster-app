"""Company service — tenant lifecycle."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.rbac import assign_user_role, require_company_access, user_has_permission
from app.models.company import Company, CompanyMember, CompanyRole
from app.models.user import User
from app.repositories.company import CompanyMemberRepository, CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, db: Session):
        self.db = db
        self.companies = CompanyRepository(db)
        self.members = CompanyMemberRepository(db)

    def create_company(self, owner: User, data: CompanyCreate) -> Company:
        if not user_has_permission(self.db, owner, "companies", "create"):
            assign_user_role(self.db, str(owner.id), "owner")

        company = self.companies.create(
            {
                "name": data.name,
                "legal_name": data.legal_name or data.name,
                "gst_number": data.gst_number,
                "pan_number": data.pan_number,
                "phone_number": data.phone_number,
                "email": data.email,
                "website": data.website,
                "address_line1": data.address_line1,
                "address_line2": data.address_line2,
                "city": data.city,
                "state_code": data.state_code,
                "pincode": data.pincode,
                "country_code": data.country_code,
                "owner_id": owner.id,
            }
        )
        self.members.add_member(str(company.id), str(owner.id), CompanyRole.OWNER.value)
        owner.active_company_id = company.id
        assign_user_role(self.db, str(owner.id), "owner")
        self.db.commit()
        self.db.refresh(company)
        return company

    def create_default_for_user(self, owner: User, company_name: str) -> Company:
        """Create tenant company on registration."""
        existing = self.companies.get_by_owner(str(owner.id), limit=1)
        if existing:
            company = existing[0]
            if not owner.active_company_id:
                owner.active_company_id = company.id
                self.db.commit()
            return company

        return self.create_company(
            owner,
            CompanyCreate(name=company_name),
        )

    def list_for_user(self, user: User) -> List[Company]:
        return self.companies.get_user_companies(str(user.id))

    def get_company(self, user: User, company_id: str) -> Company:
        company = self.companies.get_by_id(company_id)
        if not company:
            raise NotFoundException("Company not found")
        if not require_company_access(self.db, user, company_id):
            raise ForbiddenException("Access denied to this company")
        return company

    def update_company(self, user: User, company_id: str, data: CompanyUpdate) -> Company:
        if not user_has_permission(self.db, user, "companies", "update", company_id):
            raise ForbiddenException("Insufficient permissions")
        company = self.get_company(user, company_id)
        updated = self.companies.update(company_id, data.model_dump(exclude_none=True))
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def set_active_company(self, user: User, company_id: str) -> User:
        if not require_company_access(self.db, user, company_id):
            raise ForbiddenException("Access denied to this company")
        user.active_company_id = company_id
        self.db.commit()
        self.db.refresh(user)
        return user
