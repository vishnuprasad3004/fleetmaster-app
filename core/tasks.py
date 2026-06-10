"""Background task processing with Celery."""

from celery import Celery
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.config.database import SessionLocal
from app.services.vehicle import VehicleService
from app.services.driver import DriverService
from app.services.trip import TripService
from app.api.websocket import send_alert_to_owner

# Initialize Celery
celery_app = Celery(
    "fleetmaster",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.core.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_routes={
        "app.core.tasks.check_document_expiry": {"queue": "alerts"},
        "app.core.tasks.check_service_due": {"queue": "alerts"},
        "app.core.tasks.check_license_expiry": {"queue": "alerts"},
        "app.core.tasks.generate_reports": {"queue": "reports"},
        "app.core.tasks.cleanup_old_data": {"queue": "maintenance"},
    },
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "check-document-expiry": {
        "task": "app.core.tasks.check_document_expiry",
        "schedule": 3600.0,  # Every hour
    },
    "check-service-due": {
        "task": "app.core.tasks.check_service_due", 
        "schedule": 7200.0,  # Every 2 hours
    },
    "check-license-expiry": {
        "task": "app.core.tasks.check_license_expiry",
        "schedule": 3600.0,  # Every hour
    },
    "generate-daily-reports": {
        "task": "app.core.tasks.generate_daily_reports",
        "schedule": 86400.0,  # Daily at midnight
    },
    "cleanup-old-gps-logs": {
        "task": "app.core.tasks.cleanup_old_gps_logs",
        "schedule": 604800.0,  # Weekly
    },
    "calculate-driver-performance": {
        "task": "app.core.tasks.calculate_driver_performance",
        "schedule": 86400.0,  # Daily
    },
}


def get_db_session():
    """Get database session for tasks."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@celery_app.task(bind=True)
def check_document_expiry(self):
    """Check for expiring vehicle documents."""
    try:
        db = get_db_session()
        vehicle_service = VehicleService(db)
        
        # Get all users (owners)
        from app.repositories.user import UserRepository
        user_repo = UserRepository(db)
        users = user_repo.get_all()
        
        for user in users:
            # Check documents expiring in 30 days
            expiring_docs = vehicle_service.get_expiring_documents(user.id, days=30)
            
            for doc in expiring_docs:
                # Send real-time alert
                asyncio.create_task(send_alert_to_owner(
                    user.id,
                    {
                        "type": "document_expiring",
                        "title": f"Document Expiring Soon",
                        "message": f"Vehicle {doc.vehicle.registration_number} - {doc.document_type} expires in {doc.days_to_expiry} days",
                        "priority": "high" if doc.days_to_expiry <= 7 else "medium"
                    }
                ))
                
                # TODO: Send WhatsApp notification
                send_whatsapp_alert.delay(
                    user.phone_number,
                    f"🚨 Document Alert: Vehicle {doc.vehicle.registration_number} - {doc.document_type} expires in {doc.days_to_expiry} days. Please renew immediately."
                )
        
        db.close()
        return f"Checked document expiry for {len(users)} users"
        
    except Exception as e:
        print(f"Error checking document expiry: {e}")
        self.retry(countdown=60, max_retries=3)


@celery_app.task(bind=True)
def check_service_due(self):
    """Check for vehicles due for service."""
    try:
        db = get_db_session()
        vehicle_service = VehicleService(db)
        
        from app.repositories.user import UserRepository
        user_repo = UserRepository(db)
        users = user_repo.get_all()
        
        for user in users:
            service_due_vehicles = vehicle_service.get_vehicles_due_for_service(user.id)
            
            for vehicle in service_due_vehicles:
                # Send real-time alert
                asyncio.create_task(send_alert_to_owner(
                    user.id,
                    {
                        "type": "service_due",
                        "title": f"Service Due",
                        "message": f"Vehicle {vehicle.registration_number} is due for service (Current: {vehicle.current_odo} km)",
                        "priority": "medium"
                    }
                ))
        
        db.close()
        return f"Checked service due for {len(users)} users"
        
    except Exception as e:
        print(f"Error checking service due: {e}")
        self.retry(countdown=60, max_retries=3)


@celery_app.task(bind=True)
def check_license_expiry(self):
    """Check for expiring driver licenses."""
    try:
        db = get_db_session()
        driver_service = DriverService(db)
        
        from app.repositories.user import UserRepository
        user_repo = UserRepository(db)
        users = user_repo.get_all()
        
        for user in users:
            # Check licenses expiring in 30 days
            expiring_licenses = driver_service.get_drivers_license_expiring_soon(user.id, days=30)
            
            for driver in expiring_licenses:
                # Send real-time alert
                asyncio.create_task(send_alert_to_owner(
                    user.id,
                    {
                        "type": "license_expiring",
                        "title": f"License Expiring Soon",
                        "message": f"Driver {driver.full_name} license expires in {driver.license_days_to_expiry} days",
                        "priority": "high" if driver.license_days_to_expiry <= 7 else "medium"
                    }
                ))
        
        db.close()
        return f"Checked license expiry for {len(users)} users"
        
    except Exception as e:
        print(f"Error checking license expiry: {e}")
        self.retry(countdown=60, max_retries=3)


@celery_app.task
def generate_daily_reports():
    """Generate daily business reports."""
    try:
        db = get_db_session()
        
        from app.repositories.user import UserRepository
        user_repo = UserRepository(db)
        users = user_repo.get_all()
        
        for user in users:
            # Generate daily summary
            trip_service = TripService(db)
            vehicle_service = VehicleService(db)
            driver_service = DriverService(db)
            
            # Get today's stats
            trip_stats = trip_service.get_trip_stats(user.id, days=1)
            
            # Send daily WhatsApp summary
            summary = f"""
📊 *FleetMaster Daily Summary*
Date: {datetime.now().strftime('%d/%m/%Y')}

💰 *Financial*
Revenue: ₹{trip_stats['total_revenue']:,.2f}
Costs: ₹{trip_stats['total_costs']:,.2f}
Profit: ₹{trip_stats['total_profit']:,.2f}

🚛 *Operations*
Trips Completed: {trip_stats['completed_trips']}
Total Distance: {trip_stats['total_distance']:.0f} km
Active Vehicles: {vehicle_service.get_vehicle_stats(user.id)['active_vehicles']}

⚠️ *Alerts*
Check FleetMaster app for any pending alerts.
            """
            
            send_whatsapp_summary.delay(user.phone_number, summary)
        
        db.close()
        return f"Generated daily reports for {len(users)} users"
        
    except Exception as e:
        print(f"Error generating daily reports: {e}")
        return f"Error: {e}"


@celery_app.task
def cleanup_old_gps_logs():
    """Clean up GPS logs older than 90 days."""
    try:
        db = get_db_session()
        
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Delete old GPS logs
        from app.models.trip import TripGPSLog
        deleted_count = db.query(TripGPSLog).filter(
            TripGPSLog.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        db.close()
        
        return f"Cleaned up {deleted_count} old GPS logs"
        
    except Exception as e:
        print(f"Error cleaning up GPS logs: {e}")
        return f"Error: {e}"


@celery_app.task
def calculate_driver_performance():
    """Calculate daily driver performance metrics."""
    try:
        db = get_db_session()
        
        # Update driver performance scores
        from app.repositories.driver import DriverRepository
        from app.repositories.trip import TripRepository
        
        driver_repo = DriverRepository(db)
        trip_repo = TripRepository(db)
        
        drivers = driver_repo.get_all()
        
        for driver in drivers:
            # Calculate performance metrics
            recent_trips = trip_repo.get_by_driver(driver.id, skip=0, limit=50)
            
            if recent_trips:
                # Calculate average efficiency score
                avg_efficiency = sum(trip.efficiency_score for trip in recent_trips) / len(recent_trips)
                
                # Update driver rating
                driver_repo.update(driver, {"avg_rating": avg_efficiency})
        
        db.commit()
        db.close()
        
        return f"Updated performance for {len(drivers)} drivers"
        
    except Exception as e:
        print(f"Error calculating driver performance: {e}")
        return f"Error: {e}"


@celery_app.task
def send_whatsapp_alert(phone_number: str, message: str):
    """Send WhatsApp alert to user."""
    try:
        # TODO: Implement WhatsApp API integration
        # Using Twilio WhatsApp API or similar service
        print(f"WhatsApp alert to {phone_number}: {message}")
        return f"WhatsApp sent to {phone_number}"
    except Exception as e:
        print(f"Error sending WhatsApp: {e}")
        return f"Error: {e}"


@celery_app.task
def send_whatsapp_summary(phone_number: str, summary: str):
    """Send daily WhatsApp summary."""
    try:
        # TODO: Implement WhatsApp API integration
        print(f"WhatsApp summary to {phone_number}: {summary}")
        return f"Summary sent to {phone_number}"
    except Exception as e:
        print(f"Error sending WhatsApp summary: {e}")
        return f"Error: {e}"


@celery_app.task
def process_gps_tracking_data(trip_id: str, gps_data: Dict[str, Any]):
    """Process incoming GPS tracking data."""
    try:
        db = get_db_session()
        
        # Save GPS log
        from app.models.trip import TripGPSLog
        gps_log = TripGPSLog(
            trip_id=trip_id,
            timestamp=datetime.utcnow(),
            latitude=gps_data["latitude"],
            longitude=gps_data["longitude"],
            speed=gps_data.get("speed"),
            heading=gps_data.get("heading"),
            accuracy=gps_data.get("accuracy"),
            fuel_level=gps_data.get("fuel_level"),
            odometer=gps_data.get("odometer")
        )
        
        db.add(gps_log)
        db.commit()
        db.close()
        
        # Check for geofence violations, speed violations, etc.
        check_geofence_violations.delay(trip_id, gps_data)
        
        return f"Processed GPS data for trip {trip_id}"
        
    except Exception as e:
        print(f"Error processing GPS data: {e}")
        return f"Error: {e}"


@celery_app.task
def check_geofence_violations(trip_id: str, gps_data: Dict[str, Any]):
    """Check for geofence violations."""
    try:
        # TODO: Implement geofencing logic
        print(f"Checking geofence for trip {trip_id}")
        return f"Geofence check completed for trip {trip_id}"
    except Exception as e:
        print(f"Error checking geofence: {e}")
        return f"Error: {e}"