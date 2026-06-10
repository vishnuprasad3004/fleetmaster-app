"""Fuel service for business logic."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.models.fuel import FuelLog, FuelType
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.schemas.fuel import (
    FuelLogCreate, FuelLogUpdate, FuelLogResponse,
    FuelDashboardResponse, VehicleFuelModel, VehicleFuelAnalyticsResponse
)


class FuelService:
    """Service for fuel operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_fuel_log(
        self,
        log_data: FuelLogCreate,
        user_id: str,
        company_id: str
    ) -> FuelLog:
        """Create a new fuel log."""
        # Verify vehicle belongs to company
        vehicle = self.db.query(Vehicle).filter(
            Vehicle.id == log_data.vehicle_id,
            Vehicle.company_id == company_id
        ).first()
        
        if not vehicle:
            raise ValueError("Vehicle not found or access denied")
        
        # Verify driver belongs to company if provided
        if log_data.driver_id:
            driver = self.db.query(Driver).filter(
                Driver.id == log_data.driver_id,
                Driver.company_id == company_id
            ).first()
            if not driver:
                raise ValueError("Driver not found or access denied")
        
        # Create fuel log
        log = FuelLog(
            vehicle_id=log_data.vehicle_id,
            company_id=company_id,
            driver_id=log_data.driver_id,
            created_by=user_id,
            date=log_data.date,
            fuel_type=log_data.fuel_type,
            quantity=log_data.quantity,
            cost_per_liter=log_data.cost_per_liter,
            total_cost=log_data.quantity * log_data.cost_per_liter,
            odometer_reading=log_data.odometer_reading,
            fuel_station_name=log_data.fuel_station_name,
            fuel_station_location=log_data.fuel_station_location,
            fuel_station_contact=log_data.fuel_station_contact,
            notes=log_data.notes,
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_fuel_logs(
        self,
        company_id: str,
        vehicle_id: Optional[str] = None,
        driver_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FuelLog]:
        """Get fuel logs with filters."""
        query = self.db.query(FuelLog).filter(
            FuelLog.company_id == company_id
        )
        
        if vehicle_id:
            query = query.filter(FuelLog.vehicle_id == vehicle_id)
        
        if driver_id:
            query = query.filter(FuelLog.driver_id == driver_id)
        
        query = query.order_by(desc(FuelLog.date))
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_fuel_log(self, log_id: str, company_id: str) -> Optional[FuelLog]:
        """Get a specific fuel log."""
        return self.db.query(FuelLog).filter(
            FuelLog.id == log_id,
            FuelLog.company_id == company_id
        ).first()
    
    def update_fuel_log(
        self,
        log_id: str,
        log_data: FuelLogUpdate,
        company_id: str
    ) -> Optional[FuelLog]:
        """Update a fuel log."""
        log = self.get_fuel_log(log_id, company_id)
        if not log:
            return None
        
        # Update fields
        update_data = log_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(log, field):
                setattr(log, field, value)
        
        # Recalculate total cost if quantity or cost_per_liter changed
        if 'quantity' in update_data or 'cost_per_liter' in update_data:
            log.total_cost = log.quantity * log.cost_per_liter
        
        log.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def delete_fuel_log(self, log_id: str, company_id: str) -> bool:
        """Delete a fuel log."""
        log = self.get_fuel_log(log_id, company_id)
        if not log:
            return False
        
        self.db.delete(log)
        self.db.commit()
        return True
    
    def get_dashboard(self, company_id: str) -> FuelDashboardResponse:
        """Get fuel dashboard data."""
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        
        # Total fuel cost (last 30 days)
        total_cost = self.db.query(func.sum(FuelLog.total_cost)).filter(
            FuelLog.company_id == company_id,
            FuelLog.date >= thirty_days_ago
        ).scalar() or 0.0
        
        # Total quantity (last 30 days)
        total_quantity = self.db.query(func.sum(FuelLog.quantity)).filter(
            FuelLog.company_id == company_id,
            FuelLog.date >= thirty_days_ago
        ).scalar() or 0.0
        
        # Average mileage (last 30 days) - simplified calculation
        # In production, this would use trip data
        average_mileage = 4.5  # Placeholder - would calculate from actual trip data
        
        # Cost per KM
        cost_per_km = total_cost / 10000 if total_cost > 0 else 0.0  # Placeholder
        
        # Cost trend (last 7 days)
        cost_trend = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_cost = self.db.query(func.sum(FuelLog.total_cost)).filter(
                FuelLog.company_id == company_id,
                FuelLog.date >= day_start,
                FuelLog.date < day_end
            ).scalar() or 0.0
            cost_trend.append(float(day_cost))
        
        # Best mileage vehicle (simplified)
        best_mileage_vehicle = {
            'vehicle_number': 'TN38AB1234',
            'mileage': 5.2
        }
        
        # Worst mileage vehicle (simplified)
        worst_mileage_vehicle = {
            'vehicle_number': 'TN45CD6789',
            'mileage': 3.8
        }
        
        return FuelDashboardResponse(
            total_fuel_cost=total_cost,
            total_quantity=total_quantity,
            average_mileage=average_mileage,
            cost_per_km=cost_per_km,
            best_mileage_vehicle=best_mileage_vehicle,
            worst_mileage_vehicle=worst_mileage_vehicle,
            cost_trend=cost_trend
        )
    
    def get_vehicle_fuel_logs(self, vehicle_id: str, company_id: str) -> List[FuelLog]:
        """Get all fuel logs for a specific vehicle."""
        return self.db.query(FuelLog).filter(
            FuelLog.vehicle_id == vehicle_id,
            FuelLog.company_id == company_id
        ).order_by(
            desc(FuelLog.date)
        ).all()
    
    def get_vehicle_analytics(self, vehicle_id: str, company_id: str) -> VehicleFuelAnalyticsResponse:
        """Get fuel analytics for a specific vehicle."""
        vehicle = self.db.query(Vehicle).filter(
            Vehicle.id == vehicle_id,
            Vehicle.company_id == company_id
        ).first()
        
        if not vehicle:
            raise ValueError("Vehicle not found or access denied")
        
        # Get fuel logs
        fuel_logs = self.get_vehicle_fuel_logs(vehicle_id, company_id)
        
        # Calculate totals
        total_cost = sum(log.total_cost for log in fuel_logs)
        total_quantity = sum(log.quantity for log in fuel_logs)
        
        # Calculate average mileage (simplified)
        average_mileage = 4.5  # Placeholder
        
        # Calculate cost per KM
        cost_per_km = total_cost / 5000 if total_cost > 0 else 0.0  # Placeholder
        
        # Mileage trend (last 7 entries)
        mileage_trend = [4.2, 4.3, 4.5, 4.4, 4.6, 4.5, 4.7]  # Placeholder
        
        # Cost trend (last 7 entries)
        cost_trend = [log.total_cost for log in fuel_logs[:7]]  # Simplified
        
        return VehicleFuelAnalyticsResponse(
            vehicle_id=str(vehicle.id),
            vehicle_number=vehicle.registration_number,
            total_fuel_cost=total_cost,
            total_quantity=total_quantity,
            average_mileage=average_mileage,
            cost_per_km=cost_per_km,
            fuel_logs=[],
            mileage_trend=mileage_trend,
            cost_trend=cost_trend
        )
    
    def get_cost_per_km_analysis(self, company_id: str) -> List[dict]:
        """Get cost per KM analysis for all vehicles."""
        # Simplified implementation
        # In production, this would calculate actual costs from trips, fuel, and maintenance
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.company_id == company_id
        ).all()
        
        results = []
        for vehicle in vehicles:
            total_fuel_cost = self.db.query(func.sum(FuelLog.total_cost)).filter(
                FuelLog.vehicle_id == vehicle.id,
                FuelLog.company_id == company_id
            ).scalar() or 0.0
            
            results.append({
                'vehicle_id': str(vehicle.id),
                'vehicle_number': vehicle.registration_number,
                'cost_per_km': total_fuel_cost / 5000 if total_fuel_cost > 0 else 0.0,
                'fuel_cost_per_km': total_fuel_cost / 5000 if total_fuel_cost > 0 else 0.0,
                'maintenance_cost_per_km': 0.0,  # Placeholder
                'total_cost_per_km': total_fuel_cost / 5000 if total_fuel_cost > 0 else 0.0
            })
        
        return results
