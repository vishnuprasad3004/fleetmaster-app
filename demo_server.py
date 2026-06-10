"""
FleetMaster Demo Backend Server
Simple FastAPI server for demonstrating the frontend integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime, timedelta
import uuid

app = FastAPI(
    title="FleetMaster Demo API",
    description="Demo backend for FleetMaster mobile app",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    business_name: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    business_name: Optional[str]

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: User

class DashboardStats(BaseModel):
    financial: dict
    operations: dict
    overview: dict
    alerts: dict

class Vehicle(BaseModel):
    id: str
    registration_number: str
    brand: str
    model: str
    status: str
    current_odo: float
    fuel_type: Optional[str]
    mileage: Optional[float]

# Demo data
DEMO_USER = {
    "id": "user_123",
    "email": "vishnu@fleetmaster.com",
    "first_name": "Vishnu",
    "last_name": "Prasad",
    "business_name": "FleetMaster Demo"
}

DEMO_VEHICLES = [
    {
        "id": "veh_001",
        "registration_number": "TN-38-BC-1001",
        "brand": "Tata",
        "model": "Ace Gold",
        "status": "active",
        "current_odo": 45230.5,
        "fuel_type": "Diesel",
        "mileage": 12.5
    },
    {
        "id": "veh_002", 
        "registration_number": "KA-01-HG-9922",
        "brand": "Mahindra",
        "model": "Bolero Pickup",
        "status": "active",
        "current_odo": 67890.2,
        "fuel_type": "Diesel", 
        "mileage": 14.2
    },
    {
        "id": "veh_003",
        "registration_number": "MH-12-QG-4455",
        "brand": "Ashok Leyland",
        "model": "Partner",
        "status": "inactive",
        "current_odo": 89450.8,
        "fuel_type": "Diesel",
        "mileage": 11.8
    },
    {
        "id": "veh_004",
        "registration_number": "DL-07-XY-7788", 
        "brand": "Force",
        "model": "Traveller",
        "status": "maintenance",
        "current_odo": 34560.3,
        "fuel_type": "Diesel",
        "mileage": 9.5
    }
]

DEMO_DASHBOARD = {
    "financial": {
        "total_revenue": 42500.0,
        "total_costs": 28300.0,
        "total_profit": 14200.0,
        "fuel_cost": 12500.0,
        "maintenance_cost": 4800.0,
        "revenue_growth": 8.5,
        "profit_growth": 15.2
    },
    "operations": {
        "total_distance": 1247.5,
        "total_fuel_consumed": 285.4,
        "avg_efficiency_score": 87.3,
        "total_refuels": 12,
        "total_services": 3,
        "active_vehicles": 2,
        "vehicles_in_service": 1,
        "active_trips": 3,
        "average_speed": 45.8
    },
    "overview": {
        "total_vehicles": 4,
        "active_vehicles": 2,
        "total_drivers": 4,
        "active_drivers": 2,
        "trips_in_progress": 3,
        "completed_trips_today": 8
    },
    "alerts": {
        "vehicles_with_expired_docs": 1,
        "vehicles_due_for_service": 2,
        "drivers_with_expired_license": 0,
        "drivers_license_expiring_soon": 1
    }
}

DEMO_ALERTS = [
    {
        "id": "alert_001",
        "title": "Engine Temperature High",
        "description": "Vehicle TN-38-BC-1001 showing high engine temperature",
        "priority": "critical",
        "category": "vehicle",
        "created_at": (datetime.now() - timedelta(minutes=15)).isoformat()
    },
    {
        "id": "alert_002",
        "title": "Service Due",
        "description": "KA-01-HG-9922 due for regular maintenance",
        "priority": "warning",
        "category": "maintenance", 
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
    },
    {
        "id": "alert_003",
        "title": "Insurance Expiry",
        "description": "MH-12-QG-4455 insurance expires in 5 days",
        "priority": "high",
        "category": "document",
        "created_at": (datetime.now() - timedelta(hours=6)).isoformat()
    }
]

DEMO_VEHICLE_LOCATIONS = [
    {
        "registration_number": "TN-38-BC-1001",
        "driver_name": "Rajesh Kumar",
        "current_location": "Chennai → Bangalore", 
        "speed": 62,
        "status": "active",
        "eta": "2h 30m",
        "last_update": "2 min ago"
    },
    {
        "registration_number": "KA-01-HG-9922",
        "driver_name": "Suresh Singh",
        "current_location": "Bangalore → Chennai",
        "speed": 0,
        "status": "idle", 
        "eta": "4h 15m",
        "last_update": "5 min ago"
    }
]

# API Endpoints
@app.get("/")
async def root():
    return {"message": "FleetMaster Demo API is running!", "version": "1.0.0"}

@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    # Demo authentication - accept any email/password
    if "@" in request.email and len(request.password) >= 4:
        return AuthResponse(
            access_token=f"demo_access_token_{uuid.uuid4().hex[:16]}",
            refresh_token=f"demo_refresh_token_{uuid.uuid4().hex[:16]}",
            user=User(**DEMO_USER)
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    # Demo registration - always succeeds
    return AuthResponse(
        access_token=f"demo_access_token_{uuid.uuid4().hex[:16]}",
        refresh_token=f"demo_refresh_token_{uuid.uuid4().hex[:16]}",
        user=User(
            id=f"user_{uuid.uuid4().hex[:8]}",
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            business_name=request.business_name
        )
    )

@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    return DashboardStats(**DEMO_DASHBOARD)

@app.get("/dashboard/alerts")
async def get_alerts():
    return {"alerts": DEMO_ALERTS}

@app.get("/dashboard/activity")
async def get_recent_activity():
    return {
        "items": [
            {
                "id": "act_001",
                "title": "Trip Completed",
                "description": "TN-38-BC-1001 completed Chennai to Bangalore route",
                "type": "trip",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()
            },
            {
                "id": "act_002", 
                "title": "Fuel Added",
                "description": "KA-01-HG-9922 refueled 45L at Bangalore",
                "type": "fuel",
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                "id": "act_003",
                "title": "Maintenance Scheduled", 
                "description": "MH-12-QG-4455 service booked for tomorrow",
                "type": "maintenance",
                "timestamp": (datetime.now() - timedelta(hours=3)).isoformat()
            }
        ]
    }

@app.get("/vehicles/", response_model=List[Vehicle])
async def get_vehicles(status: Optional[str] = None):
    vehicles = DEMO_VEHICLES.copy()
    if status:
        vehicles = [v for v in vehicles if v["status"] == status]
    return [Vehicle(**v) for v in vehicles]

@app.get("/vehicles/locations")
async def get_vehicle_locations():
    return {"vehicles": DEMO_VEHICLE_LOCATIONS}

@app.get("/maintenance/dashboard")
async def get_maintenance_dashboard():
    return {
        "upcoming_services": 3,
        "overdue_services": 1,
        "total_cost_this_month": 24500.0,
        "avg_service_cost": 8150.0
    }

@app.get("/fuel/dashboard")
async def get_fuel_dashboard():
    return {
        "total_fuel_consumed": 1250.5,
        "avg_fuel_efficiency": 12.8,
        "total_fuel_cost": 87650.0,
        "cost_per_km": 7.25
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)