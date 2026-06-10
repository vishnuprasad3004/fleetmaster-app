"""Repositories."""

from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.fleet import FleetRepository
from app.repositories.vehicle import VehicleRepository, VehicleDocumentRepository
from app.repositories.driver import DriverRepository, DriverAttendanceRepository
from app.repositories.trip import TripRepository, MaintenanceRepository, FuelRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "FleetRepository",
]
