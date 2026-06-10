"""Driver repository."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, case

from app.models.driver import Driver, DriverAttendance
from app.repositories.base import BaseRepository


class DriverRepository(BaseRepository[Driver]):
    """Repository for driver operations."""

    def __init__(self, session: Session):
        super().__init__(session, Driver)

    def get_by_employee_id(self, employee_id: str) -> Optional[Driver]:
        """Get driver by employee ID."""
        return (
            self.session.query(self.model)
            .filter(self.model.employee_id == employee_id)
            .first()
        )

    def get_by_license_number(self, license_number: str) -> Optional[Driver]:
        """Get driver by license number."""
        return (
            self.session.query(self.model)
            .filter(self.model.license_number == license_number)
            .first()
        )

    def get_by_owner(
        self, 
        owner_id: str, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Driver]:
        """Get drivers by owner with optional status filter."""
        query = self.session.query(self.model).filter(self.model.owner_id == owner_id)
        
        if status:
            query = query.filter(self.model.status == status)
            
        return (
            query.options(selectinload(self.model.assigned_vehicles))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_available_drivers(self, owner_id: str) -> List[Driver]:
        """Get drivers without assigned vehicles."""
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.status == 'active',
                    self.model.current_driver_id.is_(None),  # No assigned vehicle
                    self.model.deleted_at.is_(None)
                )
            )
            .all()
        )

    def get_drivers_with_expired_license(self, owner_id: str) -> List[Driver]:
        """Get drivers with expired licenses."""
        from datetime import datetime
        
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.license_expiry_date < datetime.utcnow(),
                    self.model.deleted_at.is_(None)
                )
            )
            .all()
        )

    def get_drivers_license_expiring_soon(self, owner_id: str, days: int = 30) -> List[Driver]:
        """Get drivers whose licenses are expiring soon."""
        from datetime import datetime, timedelta
        
        expiry_threshold = datetime.utcnow() + timedelta(days=days)
        
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    self.model.license_expiry_date <= expiry_threshold,
                    self.model.license_expiry_date > datetime.utcnow(),
                    self.model.deleted_at.is_(None)
                )
            )
            .all()
        )

    def search_drivers(
        self, 
        owner_id: str, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Driver]:
        """Search drivers by name, employee ID, phone."""
        search_pattern = f"%{search_term}%"
        
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.owner_id == owner_id,
                    or_(
                        self.model.first_name.ilike(search_pattern),
                        self.model.last_name.ilike(search_pattern),
                        self.model.employee_id.ilike(search_pattern),
                        self.model.phone_number.ilike(search_pattern)
                    ),
                    self.model.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_driver_stats(self, owner_id: str) -> Dict[str, Any]:
        """Get driver statistics for dashboard."""
        from sqlalchemy import case
        
        stats = (
            self.session.query(
                func.count(self.model.id).label('total'),
                func.count(
                    case((self.model.status == 'active', 1))
                ).label('active'),
                func.count(
                    case((self.model.status == 'inactive', 1))
                ).label('inactive'),
                func.avg(self.model.avg_rating).label('avg_rating'),
                func.sum(self.model.total_trips).label('total_trips'),
                func.sum(self.model.total_distance).label('total_distance')
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
            'total_drivers': stats.total or 0,
            'active_drivers': stats.active or 0,
            'inactive_drivers': stats.inactive or 0,
            'avg_driver_rating': round(stats.avg_rating or 0, 2),
            'total_trips_completed': stats.total_trips or 0,
            'total_distance_covered': stats.total_distance or 0
        }


class DriverAttendanceRepository(BaseRepository[DriverAttendance]):
    """Repository for driver attendance operations."""

    def __init__(self, session: Session):
        super().__init__(session, DriverAttendance)

    def get_by_driver_and_date(self, driver_id: str, date: str) -> Optional[DriverAttendance]:
        """Get attendance record for driver on specific date."""
        from datetime import datetime
        
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.driver_id == driver_id,
                    func.date(self.model.date) == target_date
                )
            )
            .first()
        )

    def get_driver_attendance_range(
        self, 
        driver_id: str, 
        start_date: str, 
        end_date: str
    ) -> List[DriverAttendance]:
        """Get attendance records for driver within date range."""
        from datetime import datetime
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.driver_id == driver_id,
                    self.model.date >= start,
                    self.model.date <= end
                )
            )
            .order_by(self.model.date)
            .all()
        )

    def get_monthly_attendance_stats(self, driver_id: str, month: int, year: int) -> Dict[str, Any]:
        """Get monthly attendance statistics for a driver."""
        from calendar import monthrange
        from datetime import datetime
        
        start_date = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day)
        
        stats = (
            self.session.query(
                func.count(self.model.id).label('total_days'),
                func.count(
                    case((self.model.status == 'present', 1))
                ).label('present_days'),
                func.count(
                    case((self.model.status == 'absent', 1))
                ).label('absent_days'),
                func.count(
                    case((self.model.status == 'late', 1))
                ).label('late_days'),
                func.sum(self.model.total_hours).label('total_hours'),
                func.sum(self.model.overtime_hours).label('overtime_hours')
            )
            .filter(
                and_(
                    self.model.driver_id == driver_id,
                    self.model.date >= start_date,
                    self.model.date <= end_date
                )
            )
            .first()
        )
        
        working_days = last_day  # Assuming all days are working days
        attendance_percentage = ((stats.present_days or 0) / working_days) * 100 if working_days > 0 else 0
        
        return {
            'total_working_days': working_days,
            'present_days': stats.present_days or 0,
            'absent_days': stats.absent_days or 0,
            'late_days': stats.late_days or 0,
            'attendance_percentage': round(attendance_percentage, 2),
            'total_hours_worked': stats.total_hours or 0,
            'overtime_hours': stats.overtime_hours or 0
        }