# FleetMaster - API Specification

## Overview

- **Base URL**: `https://api.fleetmaster.com/v1`
- **Authentication**: JWT Bearer Token in Authorization header
- **Content-Type**: `application/json`
- **Response Format**: JSON with consistent structure

## General Response Format

### Success Response (2xx)
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

### Error Response (4xx, 5xx)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "total": 1000,
    "page": 1,
    "page_size": 20,
    "total_pages": 50
  }
}
```

## Authentication Endpoints

### POST /auth/register
**Description**: Register a new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "User registered successfully. Please verify your email."
}
```

**Validation Rules**:
- Email must be unique and valid format
- Username 3-50 chars, alphanumeric + underscore
- Password: minimum 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
- Phone: valid international format

---

### POST /auth/login
**Description**: Authenticate user and get JWT tokens

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "remember_me": false
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_here",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John"
    }
  }
}
```

**Error Responses**:
- 401: Invalid credentials
- 429: Too many login attempts (rate limited)
- 403: Account suspended/locked

---

### POST /auth/refresh-token
**Description**: Refresh access token using refresh token

**Headers**:
```
Authorization: Bearer {refresh_token}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token",
    "expires_in": 900
  }
}
```

---

### POST /auth/logout
**Description**: Logout user and invalidate tokens

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### POST /auth/verify-email
**Description**: Verify email address with verification code

**Request Body**:
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Email verified successfully"
}
```

---

### POST /auth/request-password-reset
**Description**: Request password reset via email

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Password reset link sent to email"
}
```

---

### POST /auth/reset-password
**Description**: Reset password with reset token

**Request Body**:
```json
{
  "reset_token": "token_from_email",
  "new_password": "NewSecurePassword123!"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

---

### POST /auth/setup-2fa
**Description**: Setup two-factor authentication

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "secret": "JBSWY3DPEBLW64TMMQ======",
    "qr_code_url": "https://...",
    "backup_codes": [
      "ABC123-DEFG45",
      "HIJ678-KLMN90"
    ]
  },
  "message": "Scan QR code with authenticator app"
}
```

---

### POST /auth/verify-2fa
**Description**: Verify 2FA setup or login

**Request Body**:
```json
{
  "otp_code": "123456"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "two_factor_enabled": true
  }
}
```

---

### GET /auth/me
**Description**: Get current authenticated user info

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+919876543210",
    "two_factor_enabled": true,
    "fleets": [
      {
        "id": "fleet_uuid",
        "name": "Fleet Name",
        "role": "admin"
      }
    ]
  }
}
```

## Fleet Management Endpoints

### GET /fleets
**Description**: List user's fleets

**Query Parameters**:
```
- page: number (default: 1)
- page_size: number (default: 20, max: 100)
- status: string (active, inactive, all)
- search: string (search by fleet name)
```

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "fleet_uuid",
      "name": "Premium Fleet",
      "owner_id": "user_uuid",
      "total_vehicles": 45,
      "total_drivers": 52,
      "status": "active",
      "tier": "growth",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

---

### POST /fleets
**Description**: Create a new fleet

**Headers**:
```
Authorization: Bearer {access_token}
```

**Request Body**:
```json
{
  "name": "Premium Fleet",
  "description": "Fleet for premium deliveries",
  "industry": "logistics",
  "phone_number": "+919876543210",
  "email": "fleet@example.com",
  "address": "123 Business Street",
  "city": "Bangalore",
  "state": "KA",
  "country_code": "IN"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "fleet_uuid",
    "name": "Premium Fleet",
    "owner_id": "user_uuid",
    "status": "active",
    "tier": "startup",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### GET /fleets/{fleet_id}
**Description**: Get fleet details

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "fleet_uuid",
    "name": "Premium Fleet",
    "description": "...",
    "owner_id": "user_uuid",
    "total_vehicles": 45,
    "total_drivers": 52,
    "country_code": "IN",
    "state_code": "KA",
    "city": "Bangalore",
    "address": "123 Business Street",
    "phone_number": "+919876543210",
    "email": "fleet@example.com",
    "status": "active",
    "tier": "growth",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### PUT /fleets/{fleet_id}
**Description**: Update fleet information

**Request Body** (partial update):
```json
{
  "name": "Updated Fleet Name",
  "description": "Updated description",
  "city": "Mumbai"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "fleet_uuid",
    "name": "Updated Fleet Name",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

### DELETE /fleets/{fleet_id}
**Description**: Delete/soft-delete fleet

**Response** (200):
```json
{
  "success": true,
  "message": "Fleet deleted successfully"
}
```

---

### GET /fleets/{fleet_id}/members
**Description**: List fleet members

**Query Parameters**:
```
- role: string (filter by role)
- status: string (active, inactive)
```

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "member_uuid",
      "user_id": "user_uuid",
      "fleet_id": "fleet_uuid",
      "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "role": "admin",
      "joined_at": "2024-01-01T00:00:00Z",
      "is_active": true
    }
  ]
}
```

---

### POST /fleets/{fleet_id}/members
**Description**: Add member to fleet

**Request Body**:
```json
{
  "email": "newmember@example.com",
  "role_id": "role_uuid",
  "send_invitation": true
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "member_uuid",
    "user_id": "user_uuid",
    "role": "manager",
    "invited_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### PUT /fleets/{fleet_id}/members/{user_id}
**Description**: Update member role

**Request Body**:
```json
{
  "role_id": "new_role_uuid"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "member_uuid",
    "role": "admin"
  }
}
```

---

### DELETE /fleets/{fleet_id}/members/{user_id}
**Description**: Remove member from fleet

**Response** (200):
```json
{
  "success": true,
  "message": "Member removed from fleet"
}
```

## Vehicle Management Endpoints

### GET /fleets/{fleet_id}/vehicles
**Description**: List vehicles in fleet

**Query Parameters**:
```
- page: number
- page_size: number
- status: string (operational, maintenance, retired)
- search: string (by registration number, VIN)
```

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "vehicle_uuid",
      "registration_number": "DL01AB1234",
      "vin": "VIN123456789",
      "make": "Toyota",
      "model": "Innova",
      "year": 2022,
      "fuel_type": "diesel",
      "category": "truck",
      "color": "white",
      "mileage": 15000,
      "status": "operational",
      "insurance_expiry_date": "2025-01-15",
      "registration_expiry_date": "2025-03-20"
    }
  ],
  "pagination": {
    "total": 45,
    "page": 1,
    "page_size": 20,
    "total_pages": 3
  }
}
```

---

### POST /fleets/{fleet_id}/vehicles
**Description**: Add vehicle to fleet

**Request Body**:
```json
{
  "registration_number": "DL01AB1234",
  "vin": "VIN123456789",
  "make": "Toyota",
  "model": "Innova",
  "year": 2022,
  "fuel_type": "diesel",
  "category": "truck",
  "color": "white",
  "purchased_date": "2022-01-15",
  "purchase_price": 1500000,
  "insurance_provider": "ICICI",
  "insurance_policy_number": "ICICI123456",
  "insurance_expiry_date": "2025-01-15",
  "registration_expiry_date": "2025-03-20"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "vehicle_uuid",
    "registration_number": "DL01AB1234",
    "status": "operational",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### GET /fleets/{fleet_id}/vehicles/{vehicle_id}
**Description**: Get vehicle details

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "vehicle_uuid",
    "registration_number": "DL01AB1234",
    "make": "Toyota",
    "model": "Innova",
    "status": "operational",
    "mileage": 15000,
    "assigned_driver": {
      "id": "driver_uuid",
      "first_name": "Raj",
      "last_name": "Kumar"
    },
    "fuel_tank_capacity": 60,
    "current_fuel_level": 45,
    "last_maintenance": "2024-01-10T00:00:00Z",
    "next_maintenance_due": "2024-02-10T00:00:00Z"
  }
}
```

---

### PUT /fleets/{fleet_id}/vehicles/{vehicle_id}
**Description**: Update vehicle

**Request Body** (partial update):
```json
{
  "color": "black",
  "insurance_expiry_date": "2025-06-15"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "vehicle_uuid",
    "registration_number": "DL01AB1234",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

### DELETE /fleets/{fleet_id}/vehicles/{vehicle_id}
**Description**: Remove vehicle from fleet

**Response** (200):
```json
{
  "success": true,
  "message": "Vehicle removed from fleet"
}
```

---

### GET /fleets/{fleet_id}/vehicles/{vehicle_id}/status
**Description**: Get real-time vehicle status

**Response** (200):
```json
{
  "success": true,
  "data": {
    "vehicle_id": "vehicle_uuid",
    "current_latitude": 28.6139,
    "current_longitude": 77.2090,
    "speed_kmh": 45,
    "heading": 180,
    "status": "operational",
    "last_update": "2024-01-15T10:30:00Z",
    "is_online": true,
    "battery_percent": 95,
    "current_trip": {
      "id": "trip_uuid",
      "destination": "Mumbai Port"
    }
  }
}
```

---

### GET /fleets/{fleet_id}/vehicles/{vehicle_id}/history
**Description**: Get vehicle history (trips, maintenance, etc)

**Query Parameters**:
```
- from_date: ISO date
- to_date: ISO date
- type: string (trips, maintenance, fuel, all)
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "vehicle_id": "vehicle_uuid",
    "trips_count": 124,
    "maintenance_count": 3,
    "fuel_records_count": 45,
    "total_distance": 12500,
    "trips": [
      {
        "id": "trip_uuid",
        "date": "2024-01-15",
        "distance": 150,
        "cost": 500
      }
    ]
  }
}
```


## Driver Management Endpoints

### GET /fleets/{fleet_id}/drivers
**Description**: List drivers in fleet

**Query Parameters**:
```
- page: number
- page_size: number
- status: string (active, inactive, suspended)
```

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "driver_uuid",
      "first_name": "Raj",
      "last_name": "Kumar",
      "email": "raj@example.com",
      "phone_number": "+919876543210",
      "license_number": "DL0620220012345",
      "license_expiry_date": "2026-01-15",
      "status": "active",
      "violation_count": 2,
      "accident_count": 0,
      "average_rating": 4.5
    }
  ],
  "pagination": {
    "total": 52,
    "page": 1,
    "page_size": 20,
    "total_pages": 3
  }
}
```

---

### POST /fleets/{fleet_id}/drivers
**Description**: Add driver to fleet

**Request Body**:
```json
{
  "first_name": "Raj",
  "last_name": "Kumar",
  "email": "raj@example.com",
  "phone_number": "+919876543210",
  "license_number": "DL0620220012345",
  "license_expiry_date": "2026-01-15",
  "aadhaar_number": "ENCRYPTED_AADHAAR",
  "pan_number": "ENCRYPTED_PAN",
  "date_of_birth": "1990-05-15",
  "gender": "male",
  "address": "123 Main Street",
  "driving_experience_years": 5
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "driver_uuid",
    "first_name": "Raj",
    "last_name": "Kumar",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### GET /fleets/{fleet_id}/drivers/{driver_id}
**Description**: Get driver details

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "driver_uuid",
    "first_name": "Raj",
    "last_name": "Kumar",
    "email": "raj@example.com",
    "phone_number": "+919876543210",
    "license_number": "DL0620220012345",
    "license_expiry_date": "2026-01-15",
    "status": "active",
    "driving_experience_years": 5,
    "violation_count": 2,
    "accident_count": 0,
    "average_rating": 4.5,
    "assigned_vehicles": [
      {
        "vehicle_id": "vehicle_uuid",
        "registration_number": "DL01AB1234",
        "is_primary": true
      }
    ]
  }
}
```

---

### PUT /fleets/{fleet_id}/drivers/{driver_id}
**Description**: Update driver

**Request Body** (partial update):
```json
{
  "phone_number": "+919876543211",
  "status": "inactive"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "driver_uuid",
    "first_name": "Raj",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

### DELETE /fleets/{fleet_id}/drivers/{driver_id}
**Description**: Remove driver from fleet

**Response** (200):
```json
{
  "success": true,
  "message": "Driver removed from fleet"
}
```

---

### GET /fleets/{fleet_id}/drivers/{driver_id}/trips
**Description**: Get driver's trips

**Query Parameters**:
```
- from_date: ISO date
- to_date: ISO date
- status: string
```

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "trip_uuid",
      "trip_number": "TRIP-20240115-001",
      "date": "2024-01-15",
      "vehicle": "DL01AB1234",
      "origin": "Bangalore",
      "destination": "Mumbai",
      "distance": 1350,
      "duration_hours": 18,
      "cost": 5000,
      "status": "completed"
    }
  ]
}
```

---

### GET /fleets/{fleet_id}/drivers/{driver_id}/performance
**Description**: Get driver performance metrics

**Response** (200):
```json
{
  "success": true,
  "data": {
    "driver_id": "driver_uuid",
    "average_rating": 4.5,
    "total_trips": 245,
    "completed_trips": 243,
    "cancelled_trips": 2,
    "violation_count": 2,
    "accident_count": 0,
    "average_fuel_efficiency": 8.5,
    "on_time_delivery_rate": 98.5,
    "safety_score": 95,
    "performance_trend": "improving"
  }
}
```

## Trip Management Endpoints

### GET /fleets/{fleet_id}/trips
**Description**: List trips

**Query Parameters**:
```
- page: number
- page_size: number
- status: string (created, started, completed, cancelled)
- from_date: ISO date
- to_date: ISO date
```

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "trip_uuid",
      "trip_number": "TRIP-20240115-001",
      "vehicle_id": "vehicle_uuid",
      "driver_id": "driver_uuid",
      "status": "completed",
      "started_at": "2024-01-15T06:00:00Z",
      "completed_at": "2024-01-15T14:00:00Z",
      "origin": "Bangalore",
      "destination": "Mumbai",
      "distance_km": 1350,
      "fuel_used": 150,
      "cost": 5000
    }
  ],
  "pagination": {
    "total": 500,
    "page": 1,
    "page_size": 20,
    "total_pages": 25
  }
}
```

---

### POST /fleets/{fleet_id}/trips
**Description**: Create trip

**Request Body**:
```json
{
  "vehicle_id": "vehicle_uuid",
  "driver_id": "driver_uuid",
  "trip_number": "TRIP-20240115-001",
  "origin_name": "Bangalore",
  "origin_latitude": 28.6139,
  "origin_longitude": 77.2090,
  "destination_name": "Mumbai",
  "destination_latitude": 19.0760,
  "destination_longitude": 72.8777,
  "planned_distance_km": 1350,
  "scheduled_start_time": "2024-01-15T06:00:00Z",
  "scheduled_end_time": "2024-01-16T00:00:00Z"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "trip_uuid",
    "trip_number": "TRIP-20240115-001",
    "status": "created",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### GET /fleets/{fleet_id}/trips/{trip_id}
**Description**: Get trip details

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "trip_uuid",
    "trip_number": "TRIP-20240115-001",
    "vehicle": {
      "id": "vehicle_uuid",
      "registration_number": "DL01AB1234"
    },
    "driver": {
      "id": "driver_uuid",
      "first_name": "Raj",
      "last_name": "Kumar"
    },
    "status": "completed",
    "started_at": "2024-01-15T06:00:00Z",
    "completed_at": "2024-01-15T14:00:00Z",
    "origin": "Bangalore",
    "destination": "Mumbai",
    "planned_distance_km": 1350,
    "actual_distance_km": 1355,
    "fuel_used": 150,
    "cost": 5000,
    "route_efficiency": 97.5
  }
}
```

---

### PUT /fleets/{fleet_id}/trips/{trip_id}
**Description**: Update trip

**Request Body** (partial update):
```json
{
  "status": "started",
  "notes": "Trip started from warehouse"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "trip_uuid",
    "status": "started",
    "started_at": "2024-01-15T06:15:00Z"
  }
}
```

---

### POST /fleets/{fleet_id}/trips/{trip_id}/complete
**Description**: Complete trip

**Request Body**:
```json
{
  "actual_distance_km": 1355,
  "fuel_used": 150,
  "notes": "Delivered successfully"
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "trip_uuid",
    "status": "completed",
    "completed_at": "2024-01-15T14:00:00Z",
    "duration_hours": 8
  }
}
```

---

### GET /fleets/{fleet_id}/trips/{trip_id}/route
**Description**: Get trip route with waypoints

**Response** (200):
```json
{
  "success": true,
  "data": {
    "trip_id": "trip_uuid",
    "waypoints": [
      {
        "name": "Start Point",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "order": 1
      }
    ],
    "route_polyline": "encoded_polyline_string",
    "total_distance_km": 1350,
    "estimated_duration_minutes": 480
  }
}
```

## Tracking Endpoints

### GET /fleets/{fleet_id}/tracking/live
**Description**: Get all vehicles' real-time positions

**Query Parameters**:
```
- include_offline: boolean (default: false)
```

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "vehicle_id": "vehicle_uuid",
      "registration_number": "DL01AB1234",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "speed_kmh": 45,
      "heading": 180,
      "accuracy_meters": 10,
      "is_online": true,
      "last_update": "2024-01-15T10:30:00Z",
      "driver": {
        "id": "driver_uuid",
        "name": "Raj Kumar"
      },
      "current_trip": "trip_uuid"
    }
  ]
}
```

---

### GET /fleets/{fleet_id}/tracking/vehicles/{vehicle_id}
**Description**: Get vehicle tracking history

**Query Parameters**:
```
- from_time: ISO datetime
- to_time: ISO datetime
- interval: string (1m, 5m, 15m, 1h)
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "vehicle_id": "vehicle_uuid",
    "polyline": "encoded_polyline_string",
    "points": [
      {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "speed_kmh": 45,
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "total_distance": 50,
    "duration_minutes": 30
  }
}
```

---

### POST /fleets/{fleet_id}/tracking/geofence
**Description**: Create geofence

**Request Body**:
```json
{
  "name": "Warehouse Zone",
  "description": "Main warehouse area",
  "geom_type": "circle",
  "center_latitude": 28.6139,
  "center_longitude": 77.2090,
  "radius_meters": 500,
  "entry_alert": true,
  "exit_alert": true
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "geofence_uuid",
    "name": "Warehouse Zone",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### GET /fleets/{fleet_id}/tracking/geofences
**Description**: List geofences

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "geofence_uuid",
      "name": "Warehouse Zone",
      "geom_type": "circle",
      "center_latitude": 28.6139,
      "center_longitude": 77.2090,
      "radius_meters": 500,
      "active": true
    }
  ]
}
```

---

### PUT /fleets/{fleet_id}/tracking/geofences/{geofence_id}
**Description**: Update geofence

**Request Body** (partial update):
```json
{
  "name": "Updated Warehouse Zone",
  "radius_meters": 600
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": "geofence_uuid",
    "name": "Updated Warehouse Zone",
    "radius_meters": 600
  }
}
```

---

### DELETE /fleets/{fleet_id}/tracking/geofences/{geofence_id}
**Description**: Delete geofence

**Response** (200):
```json
{
  "success": true,
  "message": "Geofence deleted"
}
```

## Analytics Endpoints

### GET /fleets/{fleet_id}/analytics/dashboard
**Description**: Get fleet dashboard metrics

**Response** (200):
```json
{
  "success": true,
  "data": {
    "total_vehicles": 45,
    "active_vehicles": 38,
    "total_drivers": 52,
    "active_drivers": 45,
    "today_trips": 124,
    "today_distance": 3500,
    "today_fuel_cost": 12500,
    "active_alerts": 5,
    "vehicle_utilization": 84.4,
    "average_fuel_efficiency": 8.5,
    "on_time_delivery_rate": 98.5
  }
}
```

---

### GET /fleets/{fleet_id}/analytics/vehicles
**Description**: Get vehicle analytics

**Query Parameters**:
```
- from_date: ISO date
- to_date: ISO date
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "total_distance": 125000,
    "total_trips": 500,
    "average_trip_distance": 250,
    "total_fuel_consumed": 14706,
    "average_fuel_efficiency": 8.5,
    "total_fuel_cost": 500000,
    "idle_hours": 120,
    "vehicles_by_status": {
      "operational": 40,
      "maintenance": 4,
      "retired": 1
    }
  }
}
```

---

### GET /fleets/{fleet_id}/analytics/drivers
**Description**: Get driver analytics

**Response** (200):
```json
{
  "success": true,
  "data": {
    "total_drivers": 52,
    "active_drivers": 45,
    "average_rating": 4.4,
    "total_violations": 8,
    "total_accidents": 2,
    "average_on_time_rate": 98.5,
    "top_performers": [
      {
        "driver_id": "driver_uuid",
        "name": "Raj Kumar",
        "rating": 4.8,
        "trips": 25
      }
    ]
  }
}
```

---

### GET /fleets/{fleet_id}/analytics/reports/{report_type}
**Description**: Generate custom report

**Parameters**:
```
report_type: vehicles, drivers, fuel, maintenance, trips, all
```

**Query Parameters**:
```
- from_date: ISO date
- to_date: ISO date
- format: json, pdf, csv
```

**Response** (200 for JSON, 200 with attachment for PDF/CSV):
```json
{
  "success": true,
  "data": {
    "report_type": "vehicles",
    "period": "2024-01-01 to 2024-01-31",
    "generated_at": "2024-01-31T23:59:00Z",
    "summary": {
      "total_vehicles": 45,
      "total_distance": 125000,
      "total_fuel": 14706
    },
    "details": []
  },
  "download_url": "https://api.fleetmaster.com/reports/report_uuid.pdf"
}
```

## Error Handling

### Error Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Invalid input parameters |
| 401 | Unauthorized | Missing/invalid auth token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |

### Error Response Example

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      },
      {
        "field": "password",
        "message": "Password too short"
      }
    ]
  }
}
```

## Rate Limiting

All endpoints are rate limited:
- **Standard**: 1000 requests/minute per user
- **Authentication**: 10 failed attempts before 15 min lockout
- **Export**: 100 report exports/day

Rate limit info in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
```

## Webhook Specifications (Phase 2+)

### Webhook Events

```
- vehicle.status_changed
- trip.completed
- geofence.entry
- geofence.exit
- maintenance.due
- alert.triggered
- driver.violation
```

### Webhook Payload

```json
{
  "event": "trip.completed",
  "timestamp": "2024-01-15T14:00:00Z",
  "fleet_id": "fleet_uuid",
  "data": {
    "trip_id": "trip_uuid",
    "vehicle_id": "vehicle_uuid",
    "duration_hours": 8,
    "distance": 1350
  }
}
```

---

This API specification covers all Phase 1 and Phase 2 endpoints with examples and validation rules.
