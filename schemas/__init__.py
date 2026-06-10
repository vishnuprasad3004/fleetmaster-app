"""API schemas."""

from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserProfileUpdate,
    PasswordReset,
    PasswordResetConfirm,
    PasswordChange,
)
from app.schemas.fleet import FleetCreate, FleetUpdate, FleetResponse
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleDocumentCreate, VehicleDocumentUpdate, VehicleDocumentResponse
from app.schemas.driver import DriverCreate, DriverUpdate, DriverResponse, DriverAttendanceCreate, DriverAttendanceUpdate, DriverAttendanceResponse
from app.schemas.trip import TripCreate, TripUpdate, TripResponse, TripExpenseResponse, TripGPSLogResponse, MaintenanceRecordResponse, FuelRecordResponse

__all__ = [
    # User
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "UserProfileUpdate",
    "PasswordReset",
    "PasswordResetConfirm",
    "PasswordChange",
    # Fleet
    "FleetCreate",
    "FleetUpdate",
    "FleetResponse",
    # Vehicle
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleResponse",
    "VehicleDocumentCreate",
    "VehicleDocumentUpdate", 
    "VehicleDocumentResponse",
    # Driver
    "DriverCreate",
    "DriverUpdate",
    "DriverResponse",
    "DriverAttendanceCreate",
    "DriverAttendanceUpdate",
    "DriverAttendanceResponse",
    # Trip
    "TripCreate",
    "TripUpdate", 
    "TripResponse",
    "TripExpenseResponse",
    "TripGPSLogResponse",
    "MaintenanceRecordResponse",
    "FuelRecordResponse",
]
