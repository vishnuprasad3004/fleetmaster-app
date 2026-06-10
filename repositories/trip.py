"""Trip repository."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta

from app.models.trip import Trip, TripStatus, MaintenanceRecord, FuelRecord
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):
    """Repository for trip operations."""

    def __init__(self, session: Session):
        super().__init__(session, Trip)

    def get_by_trip_number(self, trip_number: str) -> Optional[Trip]:
        """Get trip by trip number."""
        return (
            self.session.query(self.model)
            .filter(self.model.trip_number == trip_number)
            .first()
        )

    def get_by_owner(
        self, 
        owner_id: str,
        status: Optional[TripStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips by owner with optional status filter."""
        query = self.session.query(self.model).filter(self.model.owner_id == owner_id)
        
        if status:
            query = query.filter(self.model.status == status)
            
        return (
            query.options(
                selectinload(self.model.vehicle),
                selectinload(self.model.driver)
            )
            .order_by(desc(self.model.planned_start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_vehicle(
        self, 
        vehicle_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips by vehicle."""
        return (
            self.session.query(self.model)
            .filter(self.model.vehicle_id == vehicle_id)
            .order_by(desc(self.model.planned_start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_driver(
        self, 
        driver_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips by driver."""
        return (
            self.session.query(self.model)
            .filter(self.model.driver_id == driver_id)
            .order_by(desc(self.model.planned_start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_trips(self, owner_id: str) -> List[Trip]:
        """Get currently active trips."""
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.status.in_([TripStatus.STARTED, TripStatus.IN_PROGRESS]),
                    self.model.deleted_at.is_(None)
                )
            )
            .options(
                selectinload(self.model.vehicle),
                selectinload(self.model.driver)
            )
            .all()
        )

    def get_trips_by_date_range(
        self, 
        owner_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Trip]:
        """Get trips within date range."""
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.planned_start_time >= start_date,
                    self.model.planned_start_time <= end_date,
                    self.model.deleted_at.is_(None)
                )
            )
            .order_by(self.model.planned_start_time)
            .all()
        )

    def get_trip_stats(self, owner_id: str, days: int = 30) -> Dict[str, Any]:
        """Get trip statistics for dashboard."""
        from sqlalchemy import case
        
        # Get stats for the last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stats = (
            self.session.query(
                func.count(self.model.id).label('total'),
                func.count(
                    case((self.model.status == TripStatus.COMPLETED, 1))
                ).label('completed'),
                func.count(
                    case((self.model.status == TripStatus.IN_PROGRESS, 1))
                ).label('in_progress'),
                func.count(
                    case((self.model.status == TripStatus.CANCELLED, 1))
                ).label('cancelled'),
                func.sum(self.model.revenue).label('total_revenue'),
                func.sum(self.model.total_cost).label('total_cost'),
                func.sum(self.model.profit).label('total_profit'),
                func.sum(self.model.actual_distance).label('total_distance'),
                func.avg(self.model.efficiency_score).label('avg_efficiency')
            )
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.planned_start_time >= start_date,
                    self.model.deleted_at.is_(None)
                )
            )
            .first()
        )
        
        return {
            'total_trips': stats.total or 0,
            'completed_trips': stats.completed or 0,
            'trips_in_progress': stats.in_progress or 0,
            'cancelled_trips': stats.cancelled or 0,
            'total_revenue': stats.total_revenue or 0,
            'total_costs': stats.total_cost or 0,
            'total_profit': stats.total_profit or 0,
            'total_distance': stats.total_distance or 0,
            'avg_efficiency_score': round(stats.avg_efficiency or 0, 2)
        }

    def get_profit_analysis(self, owner_id: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed profit analysis."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Most profitable vehicle
        most_profitable_vehicle = (
            self.session.query(
                self.model.vehicle_id,
                func.sum(self.model.profit).label('total_profit')
            )
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.planned_start_time >= start_date,
                    self.model.deleted_at.is_(None)
                )
            )
            .group_by(self.model.vehicle_id)
            .order_by(desc('total_profit'))
            .first()
        )
        
        # Least profitable vehicle
        least_profitable_vehicle = (
            self.session.query(
                self.model.vehicle_id,
                func.sum(self.model.profit).label('total_profit')
            )
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.planned_start_time >= start_date,
                    self.model.deleted_at.is_(None)
                )
            )
            .group_by(self.model.vehicle_id)
            .order_by('total_profit')
            .first()
        )
        
        return {
            'most_profitable_vehicle_id': most_profitable_vehicle.vehicle_id if most_profitable_vehicle else None,
            'most_profitable_amount': most_profitable_vehicle.total_profit if most_profitable_vehicle else 0,
            'least_profitable_vehicle_id': least_profitable_vehicle.vehicle_id if least_profitable_vehicle else None,
            'least_profitable_amount': least_profitable_vehicle.total_profit if least_profitable_vehicle else 0
        }


class MaintenanceRepository(BaseRepository[MaintenanceRecord]):
    """Repository for maintenance operations."""

    def __init__(self, session: Session):
        super().__init__(session, MaintenanceRecord)

    def get_by_vehicle(
        self, 
        vehicle_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[MaintenanceRecord]:
        """Get maintenance records by vehicle."""
        return (
            self.session.query(self.model)
            .filter(self.model.vehicle_id == vehicle_id)
            .order_by(desc(self.model.service_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_maintenance_stats(self, owner_id: str, days: int = 30) -> Dict[str, Any]:
        """Get maintenance statistics."""
        from app.models.vehicle import Vehicle
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stats = (
            self.session.query(
                func.count(self.model.id).label('total_services'),
                func.sum(self.model.total_cost).label('total_cost'),
                func.avg(self.model.total_cost).label('avg_cost_per_service')
            )
            .join(Vehicle)
            .filter(
                and_(
                    Vehicle.owner_id == owner_id,
                    self.model.service_date >= start_date,
                    self.model.deleted_at.is_(None)
                )
            )
            .first()
        )
        
        return {
            'total_services': stats.total_services or 0,
            'total_maintenance_cost': stats.total_cost or 0,
            'avg_cost_per_service': round(stats.avg_cost_per_service or 0, 2)
        }


class FuelRepository(BaseRepository[FuelRecord]):
    """Repository for fuel operations."""

    def __init__(self, session: Session):
        super().__init__(session, FuelRecord)

    def get_by_vehicle(
        self, 
        vehicle_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[FuelRecord]:
        """Get fuel records by vehicle."""
        return (
            self.session.query(self.model)
            .filter(self.model.vehicle_id == vehicle_id)
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_fuel_stats(self, owner_id: str, days: int = 30) -> Dict[str, Any]:
        """Get fuel consumption statistics."""
        from app.models.vehicle import Vehicle
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stats = (
            self.session.query(
                func.count(self.model.id).label('total_refuels'),
                func.sum(self.model.quantity).label('total_fuel'),
                func.sum(self.model.total_amount).label('total_amount'),
                func.avg(self.model.rate_per_liter).label('avg_rate')
            )
            .join(Vehicle)
            .filter(
                and_(
                    Vehicle.owner_id == owner_id,
                    self.model.created_at >= start_date,
                    self.model.deleted_at.is_(None)
                )
            )
            .first()
        )
        
        return {
            'total_refuels': stats.total_refuels or 0,
            'total_fuel_consumed': stats.total_fuel or 0,
            'total_fuel_cost': stats.total_amount or 0,
            'avg_fuel_rate': round(stats.avg_rate or 0, 2)
        }