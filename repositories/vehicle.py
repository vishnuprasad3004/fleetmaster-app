"""Vehicle repository."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, case, desc
from datetime import datetime, timedelta

from app.models.vehicle import Vehicle, VehicleDocument, VehicleStatus
from app.repositories.base import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    """Repository for vehicle operations."""

    def __init__(self, session: Session):
        super().__init__(session, Vehicle)

    def get_by_registration_number(self, registration_number: str) -> Optional[Vehicle]:
        """Get vehicle by registration number."""
        return (
            self.session.query(self.model)
            .filter(self.model.registration_number == registration_number)
            .first()
        )

    def get_by_owner(
        self, 
        owner_id: str, 
        status: Optional[VehicleStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Vehicle]:
        """Get vehicles by owner with optional status filter."""
        query = self.session.query(self.model).filter(self.model.owner_id == owner_id)
        
        if status:
            query = query.filter(self.model.status == status)
            
        return (
            query.options(selectinload(self.model.documents))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_fleet(
        self, 
        fleet_id: str, 
        status: Optional[VehicleStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Vehicle]:
        """Get vehicles by fleet with optional status filter."""
        query = self.session.query(self.model).filter(self.model.fleet_id == fleet_id)
        
        if status:
            query = query.filter(self.model.status == status)
            
        return (
            query.options(selectinload(self.model.documents))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_vehicles_with_expired_documents(self, owner_id: str) -> List[Vehicle]:
        """Get vehicles with expired documents."""
        from datetime import datetime
        
        return (
            self.session.query(self.model)
            .join(VehicleDocument)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    VehicleDocument.expiry_date < datetime.utcnow(),
                    self.model.deleted_at.is_(None)
                )
            )
            .options(selectinload(self.model.documents))
            .all()
        )

    def get_vehicles_due_for_service(self, owner_id: str) -> List[Vehicle]:
        """Get vehicles due for service."""
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.current_odo >= self.model.next_service_odo,
                    self.model.next_service_odo.isnot(None),
                    self.model.deleted_at.is_(None)
                )
            )
            .all()
        )

    def search_vehicles(
        self, 
        owner_id: str, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Vehicle]:
        """Search vehicles by registration, brand, model."""
        search_pattern = f"%{search_term}%"
        
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    or_(
                        self.model.registration_number.ilike(search_pattern),
                        self.model.brand.ilike(search_pattern),
                        self.model.model.ilike(search_pattern)
                    ),
                    self.model.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_vehicle_stats(self, owner_id: str) -> Dict[str, Any]:
        """Get vehicle statistics for dashboard."""
        from sqlalchemy import func, case
        
        stats = (
            self.session.query(
                func.count(self.model.id).label('total'),
                func.count(
                    case((self.model.status == VehicleStatus.ACTIVE, 1))
                ).label('active'),
                func.count(
                    case((self.model.status == VehicleStatus.MAINTENANCE, 1))
                ).label('in_maintenance'),
                func.count(
                    case((self.model.status == VehicleStatus.INACTIVE, 1))
                ).label('inactive')
            )
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.deleted_at.is_(None)
                )
            )
            .first()
        )
        
        return {
            'total_vehicles': stats.total or 0,
            'active_vehicles': stats.active or 0,
            'vehicles_in_maintenance': stats.in_maintenance or 0,
            'inactive_vehicles': stats.inactive or 0
        }


class VehicleDocumentRepository(BaseRepository[VehicleDocument]):
    """Repository for vehicle document operations."""

    def __init__(self, session: Session):
        super().__init__(session, VehicleDocument)

    def get_by_vehicle(self, vehicle_id: str) -> List[VehicleDocument]:
        """Get all documents for a vehicle."""
        return (
            self.session.query(self.model)
            .filter(self.model.vehicle_id == vehicle_id)
            .all()
        )

    def get_expired_documents(self, owner_id: str) -> List[VehicleDocument]:
        """Get all expired documents for owner's vehicles."""
        from datetime import datetime
        
        return (
            self.session.query(self.model)
            .join(Vehicle)
            .filter(
                and_(
                    Vehicle.owner_id == owner_id,
                    self.model.expiry_date < datetime.utcnow(),
                    self.model.deleted_at.is_(None)
                )
            )
            .all()
        )

    def get_expiring_soon(self, owner_id: str, days: int = 30) -> List[VehicleDocument]:
        """Get documents expiring within specified days."""
        from datetime import datetime, timedelta
        
        expiry_threshold = datetime.utcnow() + timedelta(days=days)
        
        return (
            self.session.query(self.model)
            .join(Vehicle)
            .filter(
                and_(
                    Vehicle.owner_id == owner_id,
                    self.model.expiry_date <= expiry_threshold,
                    self.model.expiry_date > datetime.utcnow(),
                    self.model.deleted_at.is_(None)
                )
            )
            .all()
        )