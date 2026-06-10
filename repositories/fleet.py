"""Fleet repository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Fleet
from app.repositories.base import BaseRepository


class FleetRepository(BaseRepository[Fleet]):
    """Fleet repository."""

    def __init__(self, db: Session):
        super().__init__(db, Fleet)

    def get_by_owner_id(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Fleet]:
        """Get fleets by owner id."""
        return self.db.query(Fleet).filter(
            and_(Fleet.owner_id == owner_id, Fleet.deleted_at.is_(None))
        ).offset(skip).limit(limit).all()

    def get_count_by_owner(self, owner_id: str) -> int:
        """Count fleets by owner."""
        return self.db.query(Fleet).filter(
            and_(Fleet.owner_id == owner_id, Fleet.deleted_at.is_(None))
        ).count()

    def get_by_id_and_owner(self, fleet_id: str, owner_id: str) -> Optional[Fleet]:
        """Get fleet by id and owner (authorization check)."""
        return self.db.query(Fleet).filter(
            and_(
                Fleet.id == fleet_id,
                Fleet.owner_id == owner_id,
                Fleet.deleted_at.is_(None)
            )
        ).first()
