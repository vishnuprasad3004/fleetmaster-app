"""Fleet service."""

from typing import List
from sqlalchemy.orm import Session

from app.models import Fleet
from app.repositories import FleetRepository
from app.core import NotFoundException, ForbiddenException


class FleetService:
    """Fleet service."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = FleetRepository(db)

    def create(self, owner_id: str, name: str, **kwargs) -> Fleet:
        """Create a new fleet."""
        fleet_data = {
            "owner_id": owner_id,
            "name": name,
            **kwargs,
        }
        return self.repository.create(fleet_data)

    def get_by_id(self, fleet_id: str, owner_id: str = None) -> Fleet:
        """Get fleet by id with optional owner verification."""
        if owner_id:
            fleet = self.repository.get_by_id_and_owner(fleet_id, owner_id)
        else:
            fleet = self.repository.get_by_id(fleet_id)

        if not fleet:
            raise NotFoundException("Fleet not found")

        return fleet

    def get_user_fleets(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Fleet]:
        """Get all fleets for a user."""
        return self.repository.get_by_owner_id(owner_id, skip, limit)

    def get_user_fleets_count(self, owner_id: str) -> int:
        """Get count of fleets for a user."""
        return self.repository.get_count_by_owner(owner_id)

    def update(self, fleet_id: str, owner_id: str, update_data: dict) -> Fleet:
        """Update a fleet."""
        # Verify ownership
        fleet = self.get_by_id(fleet_id, owner_id)

        updated_fleet = self.repository.update(fleet_id, update_data)
        if not updated_fleet:
            raise NotFoundException("Fleet not found")

        return updated_fleet

    def delete(self, fleet_id: str, owner_id: str) -> bool:
        """Delete a fleet (soft delete)."""
        # Verify ownership
        fleet = self.get_by_id(fleet_id, owner_id)

        return self.repository.delete(fleet_id)
