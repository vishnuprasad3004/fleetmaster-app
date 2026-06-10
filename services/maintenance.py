"""Maintenance service for business logic."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.models.maintenance import MaintenanceRecord, SparePart, MaintenanceType
from app.models.vehicle import Vehicle
from app.schemas.maintenance import (
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecordResponse,
    MaintenanceDashboardResponse, VehicleCostModel, MaintenanceAlert
)


class MaintenanceService:
    """Service for maintenance operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_maintenance_record(
        self,
        record_data: MaintenanceRecordCreate,
        user_id: str,
        company_id: str
    ) -> MaintenanceRecord:
        """Create a new maintenance record."""
        # Verify vehicle belongs to company
        vehicle = self.db.query(Vehicle).filter(
            Vehicle.id == record_data.vehicle_id,
            Vehicle.company_id == company_id
        ).first()
        
        if not vehicle:
            raise ValueError("Vehicle not found or access denied")
        
        # Create maintenance record
        record = MaintenanceRecord(
            vehicle_id=record_data.vehicle_id,
            company_id=company_id,
            created_by=user_id,
            type=record_data.type,
            date=record_data.date,
            cost=record_data.cost,
            workshop_name=record_data.workshop_name,
            workshop_contact=record_data.workshop_contact,
            workshop_address=record_data.workshop_address,
            odometer_reading=record_data.odometer_reading,
            description=record_data.description,
            notes=record_data.notes,
            next_service_date=record_data.next_service_date,
            next_service_odometer=record_data.next_service_odometer,
            spare_parts=[],
        )
        
        self.db.add(record)
        self.db.flush()
        
        # Create spare parts
        for part_data in record_data.spare_parts:
            spare_part = SparePart(
                maintenance_record_id=record.id,
                name=part_data.name,
                part_number=part_data.part_number,
                quantity=part_data.quantity,
                cost_per_unit=part_data.cost_per_unit,
                total_cost=part_data.quantity * part_data.cost_per_unit,
                supplier_name=part_data.supplier_name,
                supplier_contact=part_data.supplier_contact,
            )
            self.db.add(spare_part)
        
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_maintenance_records(
        self,
        company_id: str,
        vehicle_id: Optional[str] = None,
        record_type: Optional[MaintenanceType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MaintenanceRecord]:
        """Get maintenance records with filters."""
        query = self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.company_id == company_id
        )
        
        if vehicle_id:
            query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
        
        if record_type:
            query = query.filter(MaintenanceRecord.type == record_type)
        
        query = query.order_by(desc(MaintenanceRecord.date))
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_maintenance_record(self, record_id: str, company_id: str) -> Optional[MaintenanceRecord]:
        """Get a specific maintenance record."""
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.id == record_id,
            MaintenanceRecord.company_id == company_id
        ).first()
    
    def update_maintenance_record(
        self,
        record_id: str,
        record_data: MaintenanceRecordUpdate,
        company_id: str
    ) -> Optional[MaintenanceRecord]:
        """Update a maintenance record."""
        record = self.get_maintenance_record(record_id, company_id)
        if not record:
            return None
        
        # Update fields
        update_data = record_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != 'spare_parts' and hasattr(record, field):
                setattr(record, field, value)
        
        # Handle spare parts update
        if 'spare_parts' in update_data and update_data['spare_parts'] is not None:
            # Delete existing spare parts
            self.db.query(SparePart).filter(
                SparePart.maintenance_record_id == record_id
            ).delete()
            
            # Add new spare parts
            for part_data in update_data['spare_parts']:
                spare_part = SparePart(
                    maintenance_record_id=record.id,
                    name=part_data.name,
                    part_number=part_data.part_number,
                    quantity=part_data.quantity,
                    cost_per_unit=part_data.cost_per_unit,
                    total_cost=part_data.quantity * part_data.cost_per_unit,
                    supplier_name=part_data.supplier_name,
                    supplier_contact=part_data.supplier_contact,
                )
                self.db.add(spare_part)
        
        record.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def delete_maintenance_record(self, record_id: str, company_id: str) -> bool:
        """Delete a maintenance record."""
        record = self.get_maintenance_record(record_id, company_id)
        if not record:
            return False
        
        self.db.delete(record)
        self.db.commit()
        return True
    
    def get_dashboard(self, company_id: str) -> MaintenanceDashboardResponse:
        """Get maintenance dashboard data."""
        now = datetime.utcnow()
        today = now.date()
        week_end = (now + timedelta(days=7)).date()
        
        # Service due today
        service_due_today = self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.company_id == company_id,
            MaintenanceRecord.next_service_date == today
        ).count()
        
        # Service due this week
        service_due_this_week = self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.company_id == company_id,
            MaintenanceRecord.next_service_date >= today,
            MaintenanceRecord.next_service_date <= week_end
        ).count()
        
        # Total maintenance cost (last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        total_cost = self.db.query(func.sum(MaintenanceRecord.cost)).filter(
            MaintenanceRecord.company_id == company_id,
            MaintenanceRecord.date >= thirty_days_ago
        ).scalar() or 0.0
        
        # Vehicles in service (with maintenance in last 7 days)
        seven_days_ago = now - timedelta(days=7)
        vehicles_in_service = self.db.query(func.count(func.distinct(MaintenanceRecord.vehicle_id))).filter(
            MaintenanceRecord.company_id == company_id,
            MaintenanceRecord.date >= seven_days_ago
        ).scalar() or 0
        
        # Cost trend (last 7 days)
        cost_trend = []
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_cost = self.db.query(func.sum(MaintenanceRecord.cost)).filter(
                MaintenanceRecord.company_id == company_id,
                MaintenanceRecord.date >= day_start,
                MaintenanceRecord.date < day_end
            ).scalar() or 0.0
            cost_trend.append(float(day_cost))
        
        # Top cost vehicle (last 30 days)
        top_cost_result = self.db.query(
            Vehicle.registration_number,
            func.sum(MaintenanceRecord.cost).label('total_cost')
        ).join(
            MaintenanceRecord,
            Vehicle.id == MaintenanceRecord.vehicle_id
        ).filter(
            Vehicle.company_id == company_id,
            MaintenanceRecord.date >= thirty_days_ago
        ).group_by(
            Vehicle.id,
            Vehicle.registration_number
        ).order_by(
            desc('total_cost')
        ).first()
        
        top_cost_vehicle = {}
        if top_cost_result:
            top_cost_vehicle = {
                'vehicle_number': top_cost_result[0],
                'cost': float(top_cost_result[1]),
                'cost_change': 15.0  # Placeholder - would calculate from previous period
            }
        
        return MaintenanceDashboardResponse(
            service_due_today=service_due_today,
            service_due_this_week=service_due_this_week,
            total_maintenance_cost=total_cost,
            vehicles_in_service=vehicles_in_service,
            cost_trend=cost_trend,
            top_cost_vehicle=top_cost_vehicle
        )
    
    def get_upcoming_services(self, company_id: str, limit: int = 50) -> List[MaintenanceRecord]:
        """Get upcoming service records."""
        now = datetime.utcnow()
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.company_id == company_id,
            MaintenanceRecord.next_service_date >= now
        ).order_by(
            MaintenanceRecord.next_service_date.asc()
        ).limit(limit).all()
    
    def get_service_records(self, company_id: str, limit: int = 100) -> List[MaintenanceRecord]:
        """Get service records only."""
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.company_id == company_id,
            MaintenanceRecord.type == MaintenanceType.SERVICE
        ).order_by(
            desc(MaintenanceRecord.date)
        ).limit(limit).all()
    
    def get_repair_records(self, company_id: str, limit: int = 100) -> List[MaintenanceRecord]:
        """Get repair records only."""
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.company_id == company_id,
            MaintenanceRecord.type == MaintenanceType.REPAIR
        ).order_by(
            desc(MaintenanceRecord.date)
        ).limit(limit).all()
    
    def get_vehicle_maintenance_records(self, vehicle_id: str, company_id: str) -> List[MaintenanceRecord]:
        """Get all maintenance records for a specific vehicle."""
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.vehicle_id == vehicle_id,
            MaintenanceRecord.company_id == company_id
        ).order_by(
            desc(MaintenanceRecord.date)
        ).all()
    
    def get_alerts(self, company_id: str) -> List[MaintenanceAlert]:
        """Get maintenance alerts."""
        now = datetime.utcnow()
        alerts = []
        
        # Get vehicles with upcoming services
        upcoming = self.db.query(MaintenanceRecord, Vehicle).join(
            Vehicle,
            MaintenanceRecord.vehicle_id == Vehicle.id
        ).filter(
            Vehicle.company_id == company_id,
            MaintenanceRecord.next_service_date >= now
        ).order_by(
            MaintenanceRecord.next_service_date.asc()
        ).limit(20).all()
        
        for record, vehicle in upcoming:
            days_until = (record.next_service_date - now).days if record.next_service_date else None
            
            if days_until is not None:
                if days_until <= 0:
                    urgency = "urgent"
                    message = f"Service overdue for {vehicle.registration_number}"
                elif days_until <= 3:
                    urgency = "urgent"
                    message = f"Service due in {days_until} day{'s' if days_until != 1 else ''} for {vehicle.registration_number}"
                elif days_until <= 7:
                    urgency = "warning"
                    message = f"Service due in {days_until} days for {vehicle.registration_number}"
                else:
                    urgency = "info"
                    message = f"Service scheduled for {vehicle.registration_number}"
                
                alerts.append(MaintenanceAlert(
                    vehicle_id=vehicle.id,
                    vehicle_number=vehicle.registration_number,
                    alert_type="service_due",
                    message=message,
                    urgency=urgency,
                    days_until=days_until
                ))
        
        return alerts
