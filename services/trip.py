"""Trip service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.trip import Trip, TripExpense, TripGPSLog, MaintenanceRecord, FuelRecord, TripStatus
from app.repositories.trip import TripRepository, MaintenanceRepository, FuelRepository
from app.schemas.trip import TripCreate, TripUpdate, TripExpenseCreate, TripGPSLogCreate, MaintenanceRecordCreate, FuelRecordCreate
from app.services.vehicle import VehicleService
from app.services.driver import DriverService


class TripService:
    """Service for trip operations."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = TripRepository(session)
        self.vehicle_service = VehicleService(session)
        self.driver_service = DriverService(session)

    def create_trip(self, trip_data: TripCreate, owner_id: str) -> Trip:
        """Create a new trip."""
        # Verify vehicle ownership
        self.vehicle_service.get_vehicle(trip_data.vehicle_id, owner_id)
        
        # Verify driver ownership
        self.driver_service.get_driver(trip_data.driver_id, owner_id)
        
        # Check if trip number already exists
        existing_trip = self.repository.get_by_trip_number(trip_data.trip_number)
        if existing_trip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip with this trip number already exists"
            )

        # Calculate total cost and profit
        trip_dict = trip_data.dict()
        total_cost = (
            trip_dict.get('fuel_cost', 0) +
            trip_dict.get('toll_cost', 0) +
            trip_dict.get('driver_allowance', 0) +
            trip_dict.get('other_expenses', 0)
        )
        profit = trip_dict.get('revenue', 0) - total_cost
        
        trip = Trip(
            **trip_dict,
            owner_id=owner_id,
            total_cost=total_cost,
            profit=profit
        )
        return self.repository.create(trip)

    def get_trip(self, trip_id: str, owner_id: str) -> Trip:
        """Get trip by ID."""
        trip = self.repository.get(trip_id)
        if not trip or trip.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        return trip

    def get_trips(
        self, 
        owner_id: str,
        status: Optional[TripStatus] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips for owner."""
        return self.repository.get_by_owner(
            owner_id=owner_id,
            status=status,
            skip=skip,
            limit=limit
        )

    def update_trip(
        self, 
        trip_id: str, 
        trip_data: TripUpdate, 
        owner_id: str
    ) -> Trip:
        """Update trip."""
        trip = self.get_trip(trip_id, owner_id)
        
        # Check trip number uniqueness if being updated
        if (trip_data.trip_number and 
            trip_data.trip_number != trip.trip_number):
            existing_trip = self.repository.get_by_trip_number(trip_data.trip_number)
            if existing_trip and existing_trip.id != trip_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Trip with this trip number already exists"
                )

        update_data = trip_data.dict(exclude_unset=True)
        
        # Recalculate total cost and profit if financial fields updated
        financial_fields = ['fuel_cost', 'toll_cost', 'driver_allowance', 'other_expenses', 'revenue']
        if any(field in update_data for field in financial_fields):
            total_cost = (
                update_data.get('fuel_cost', trip.fuel_cost) +
                update_data.get('toll_cost', trip.toll_cost) +
                update_data.get('driver_allowance', trip.driver_allowance) +
                update_data.get('other_expenses', trip.other_expenses)
            )
            profit = update_data.get('revenue', trip.revenue) - total_cost
            update_data.update({
                'total_cost': total_cost,
                'profit': profit
            })

        return self.repository.update(trip, update_data)

    def delete_trip(self, trip_id: str, owner_id: str) -> bool:
        """Soft delete trip."""
        trip = self.get_trip(trip_id, owner_id)
        return self.repository.delete(trip)

    def get_trips_by_vehicle(
        self, 
        vehicle_id: str, 
        owner_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips by vehicle."""
        # Verify vehicle ownership
        self.vehicle_service.get_vehicle(vehicle_id, owner_id)
        return self.repository.get_by_vehicle(vehicle_id, skip, limit)

    def get_trips_by_driver(
        self, 
        driver_id: str, 
        owner_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips by driver."""
        # Verify driver ownership
        self.driver_service.get_driver(driver_id, owner_id)
        return self.repository.get_by_driver(driver_id, skip, limit)

    def get_active_trips(self, owner_id: str) -> List[Trip]:
        """Get currently active trips."""
        return self.repository.get_active_trips(owner_id)

    def get_trips_by_date_range(
        self, 
        owner_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Trip]:
        """Get trips within date range."""
        return self.repository.get_trips_by_date_range(owner_id, start_date, end_date)

    def start_trip(self, trip_id: str, owner_id: str, start_time: datetime = None) -> Trip:
        """Start a trip."""
        trip = self.get_trip(trip_id, owner_id)
        
        if trip.status != TripStatus.PLANNED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only planned trips can be started"
            )
        
        start_time = start_time or datetime.utcnow()
        update_data = {
            'status': TripStatus.STARTED,
            'actual_start_time': start_time
        }
        
        return self.repository.update(trip, update_data)

    def complete_trip(
        self, 
        trip_id: str, 
        owner_id: str, 
        end_time: datetime = None,
        actual_distance: Optional[float] = None
    ) -> Trip:
        """Complete a trip."""
        trip = self.get_trip(trip_id, owner_id)
        
        if trip.status not in [TripStatus.STARTED, TripStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only started/in-progress trips can be completed"
            )
        
        end_time = end_time or datetime.utcnow()
        update_data = {
            'status': TripStatus.COMPLETED,
            'actual_end_time': end_time
        }
        
        if actual_distance:
            update_data['actual_distance'] = actual_distance
        
        # Calculate actual duration
        if trip.actual_start_time:
            duration = (end_time - trip.actual_start_time).total_seconds() / 60
            update_data['actual_duration'] = int(duration)
        
        return self.repository.update(trip, update_data)

    def get_trip_stats(self, owner_id: str, days: int = 30) -> dict:
        """Get trip statistics."""
        return self.repository.get_trip_stats(owner_id, days)

    def get_profit_analysis(self, owner_id: str, days: int = 30) -> dict:
        """Get profit analysis."""
        return self.repository.get_profit_analysis(owner_id, days)


class MaintenanceService:
    """Service for maintenance operations."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = MaintenanceRepository(session)
        self.vehicle_service = VehicleService(session)

    def create_maintenance_record(
        self, 
        maintenance_data: MaintenanceRecordCreate, 
        owner_id: str
    ) -> MaintenanceRecord:
        """Create maintenance record."""
        # Verify vehicle ownership
        self.vehicle_service.get_vehicle(maintenance_data.vehicle_id, owner_id)
        
        maintenance = MaintenanceRecord(**maintenance_data.dict())
        return self.repository.create(maintenance)

    def get_maintenance_records(
        self, 
        vehicle_id: str, 
        owner_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[MaintenanceRecord]:
        """Get maintenance records for a vehicle."""
        # Verify vehicle ownership
        self.vehicle_service.get_vehicle(vehicle_id, owner_id)
        return self.repository.get_by_vehicle(vehicle_id, skip, limit)

    def get_maintenance_stats(self, owner_id: str, days: int = 30) -> dict:
        """Get maintenance statistics."""
        return self.repository.get_maintenance_stats(owner_id, days)


class FuelService:
    """Service for fuel operations."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = FuelRepository(session)
        self.vehicle_service = VehicleService(session)

    def create_fuel_record(
        self, 
        fuel_data: FuelRecordCreate, 
        owner_id: str
    ) -> FuelRecord:
        """Create fuel record."""
        # Verify vehicle ownership
        vehicle = self.vehicle_service.get_vehicle(fuel_data.vehicle_id, owner_id)
        
        fuel_record = FuelRecord(**fuel_data.dict())
        
        # Update vehicle's current odometer if this reading is higher
        if fuel_record.odometer_reading > vehicle.current_odo:
            from app.schemas.vehicle import VehicleUpdate
            self.vehicle_service.update_vehicle(
                fuel_data.vehicle_id,
                VehicleUpdate(current_odo=fuel_record.odometer_reading),
                owner_id
            )
        
        return self.repository.create(fuel_record)

    def get_fuel_records(
        self, 
        vehicle_id: str, 
        owner_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[FuelRecord]:
        """Get fuel records for a vehicle."""
        # Verify vehicle ownership
        self.vehicle_service.get_vehicle(vehicle_id, owner_id)
        return self.repository.get_by_vehicle(vehicle_id, skip, limit)

    def get_fuel_stats(self, owner_id: str, days: int = 30) -> dict:
        """Get fuel consumption statistics."""
        return self.repository.get_fuel_stats(owner_id, days)