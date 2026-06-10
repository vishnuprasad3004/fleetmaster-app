# FleetMaster API Documentation

## Overview

The FleetMaster API provides endpoints for fleet management operations including vehicle tracking, driver management, and trip monitoring.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API requests require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Authentication

#### Login
```
POST /auth/login

Request:
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Vehicles

#### Get All Vehicles
```
GET /vehicles
Query Parameters:
  - status: (running|idle|alert|offline)
  - limit: number
  - offset: number

Response:
{
  "data": [
    {
      "id": "1001",
      "plate_number": "TN-38-BC-1001",
      "driver": "Rajesh Kumar",
      "status": "running",
      "speed": 62,
      "battery": 85,
      "location": {
        "latitude": 13.0827,
        "longitude": 80.2707
      },
      "route": "Chennai → Bangalore",
      "earnings": "₹2,450"
    }
  ],
  "total": 4,
  "page": 1
}
```

#### Get Vehicle Details
```
GET /vehicles/{vehicle_id}

Response:
{
  "id": "1001",
  "plate_number": "TN-38-BC-1001",
  "driver_id": "driver_001",
  "status": "running",
  "speed": 62,
  "battery": 85,
  "location": {...},
  "route": {...},
  "trip_history": [...],
  "maintenance_records": [...]
}
```

### Drivers

#### Get All Drivers
```
GET /drivers

Response:
{
  "data": [
    {
      "id": "driver_001",
      "name": "Rajesh Kumar",
      "phone": "+91-9876543210",
      "email": "rajesh@example.com",
      "vehicles": 1,
      "total_earnings": "₹45,000",
      "rating": 4.8
    }
  ],
  "total": 10
}
```

### Tracking

#### Get Live Vehicle Location
```
GET /tracking/live/{vehicle_id}

Response:
{
  "vehicle_id": "1001",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "altitude": 10,
  "speed": 62,
  "bearing": 45,
  "accuracy": 5,
  "timestamp": "2026-06-10T12:30:00Z"
}
```

#### Get Trip History
```
GET /tracking/trips/{vehicle_id}
Query Parameters:
  - start_date: ISO8601 date
  - end_date: ISO8601 date
  - limit: number

Response:
{
  "data": [
    {
      "trip_id": "trip_001",
      "vehicle_id": "1001",
      "driver_id": "driver_001",
      "start_location": {...},
      "end_location": {...},
      "duration": 7200,
      "distance": 250,
      "earnings": 2450,
      "start_time": "2026-06-10T10:00:00Z",
      "end_time": "2026-06-10T12:00:00Z"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "details": {}
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 500 Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

- Rate limit: 1000 requests per hour
- Rate limit reset: On the hour
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## WebSocket (Real-time Updates)

```
ws://localhost:8000/ws/tracking/{vehicle_id}?token=<jwt_token>
```

### Message Format
```json
{
  "type": "location_update",
  "data": {
    "vehicle_id": "1001",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "speed": 62,
    "timestamp": "2026-06-10T12:30:00Z"
  }
}
```

## Code Examples

### JavaScript/Dart
```dart
final response = await http.get(
  Uri.parse('http://localhost:8000/api/v1/vehicles'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
);
```

### Python
```python
import requests

headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/v1/vehicles', headers=headers)
data = response.json()
```

## Support

For API issues, please open a GitHub issue or contact support@fleetmaster.app