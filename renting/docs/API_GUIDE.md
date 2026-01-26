# 📖 API Documentation - Car Rental System

Complete API reference for the Car Rental System backend.

**Base URL**: `http://localhost:8000`  
**Authentication**: JWT (JSON Web Tokens)

---

## 📑 Table of Contents

- [Authentication](#authentication)
- [User Management](#user-management)
- [Profile Management](#profile-management)
- [Vehicle Management](#vehicle-management)
- [Reservation Management](#reservation-management)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

### Overview

All endpoints (except registration and login) require JWT authentication.

**Include the access token in request headers:**
```
Authorization: Bearer <access_token>
```

---

### 1. Register New User

**Endpoint**: `POST /api/users/`  
**Authentication**: None (public)

**Request Body**:
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "birth_date": "1990-01-01",
  "license_number": "ABC123456"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "birth_date": "1990-01-01",
  "license_number": "ABC123456",
  "is_active": true,
  "is_staff": false
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Client Error",
  "status_code": 400,
  "details": {
    "email": ["user with this email already exists."]
  }
}
```

---

### 2. Login (Obtain JWT Tokens)

**Endpoint**: `POST /api/token/`  
**Authentication**: None

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA2...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6..."
}
```

**Error Response** (401 Unauthorized):
```json
{
  "error": "Client Error",
  "status_code": 401,
  "details": {
    "detail": "No active account found with the given credentials"
  }
}
```

**Token Lifetimes**:
- Access token: 30 minutes
- Refresh token: 1 day

---

### 3. Refresh Access Token

**Endpoint**: `POST /api/token/refresh/`  
**Authentication**: None

**Request Body**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIi..."
}
```

---

## 👤 Profile Management

All profile endpoints require authentication and operate on the current user.

### 1. Get Own Profile

**Endpoint**: `GET /api/profile/me/`  
**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "birth_date": "1990-01-01",
  "license_number": "ABC123456",
  "is_active": true,
  "is_staff": false
}
```

---

### 2. Update Profile (Full)

**Endpoint**: `PUT /api/profile/me/`  
**Authentication**: Required

**⚠️ IMPORTANT**: Requires `current_password` for security.

**Request Body**:
```json
{
  "current_password": "SecurePass123!",
  "first_name": "John Updated",
  "last_name": "Doe Updated",
  "birth_date": "1990-01-01",
  "license_number": "XYZ789"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John Updated",
  "last_name": "Doe Updated",
  "birth_date": "1990-01-01",
  "license_number": "XYZ789",
  "is_active": true,
  "is_staff": false
}
```

**Error Response** (400 Bad Request - Missing Password):
```json
{
  "error": "current_password is required to update profile"
}
```

**Error Response** (400 Bad Request - Wrong Password):
```json
{
  "error": "Invalid current password"
}
```

---

### 3. Update Profile (Partial)

**Endpoint**: `PATCH /api/profile/me/`  
**Authentication**: Required

**Request Body**:
```json
{
  "current_password": "SecurePass123!",
  "first_name": "New Name"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "New Name",
  "last_name": "Doe",
  ...
}
```

---

### 4. Change Password

**Endpoint**: `POST /api/profile/me/change-password/`  
**Authentication**: Required

**Request Body**:
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!"
}
```

**Validation Rules**:
- New password must be at least 8 characters

**Success Response** (200 OK):
```json
{
  "detail": "Password successfully updated"
}
```

**Error Responses**:

Wrong old password (400):
```json
{
  "error": "Invalid current password"
}
```

Password too short (400):
```json
{
  "error": "New password must be at least 8 characters long"
}
```

---

### 5. Delete Account

**Endpoint**: `DELETE /api/profile/me/`  
**Authentication**: Required

**Request Body**:
```json
{
  "password": "SecurePass123!"
}
```

**Success Response** (204 No Content):
```json
{
  "detail": "Account successfully deleted"
}
```

**Error Response** (400 - Wrong Password):
```json
{
  "error": "Invalid password"
}
```

---

## 🚙 Vehicle Management

### Lookup Tables

These endpoints provide reference data for vehicle specifications.

#### Get Vehicle Types

**Endpoint**: `GET /api/vehicle-types/`  
**Authentication**: Required  
**Permission**: Any authenticated user

**Success Response** (200 OK):
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {"id": 1, "name": "Sedan"},
    {"id": 2, "name": "SUV"},
    {"id": 3, "name": "Truck"}
  ]
}
```

#### Get Brands

**Endpoint**: `GET /api/brands/`  
**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {"id": 1, "name": "Toyota"},
    {"id": 2, "name": "Honda"}
  ]
}
```

**Other lookup endpoints** (same pattern):
- `GET /api/fuel-types/` - Fuel types (Gasoline, Electric, Hybrid)
- `GET /api/colors/` - Available colors
- `GET /api/transmissions/` - Transmission types (Manual, Automatic)

---

### Car Models

#### List Car Models

**Endpoint**: `GET /api/car-models/`  
**Authentication**: Required  
**Permission**: Any authenticated user

**Query Parameters**:
- `brand` - Filter by brand ID
- `vehicle_type` - Filter by vehicle type ID
- `search` - Search in model name

**Success Response** (200 OK):
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "brand": 1,
      "model_name": "Camry",
      "vehicle_type": 1,
      "seats": 5,
      "fuel_type": 1,
      "transmission": 1,
      "daily_price": "50.00",
      "image": null
    }
  ]
}
```

#### Create Car Model

**Endpoint**: `POST /api/car-models/`  
**Authentication**: Required  
**Permission**: Staff only

**Request Body**:
```json
{
  "brand": 1,
  "model_name": "Corolla",
  "vehicle_type": 1,
  "seats": 5,
  "fuel_type": 1,
  "transmission": 1,
  "daily_price": "45.00"
}
```

**Validation Rules**:
- `seats`: Must be between 1 and 50
- `daily_price`: Must be greater than 0

**Success Response** (201 Created):
```json
{
  "id": 2,
  "brand": 1,
  "model_name": "Corolla",
  ...
}
```

**Error Response** (400 - Invalid seats):
```json
{
  "error": "Client Error",
  "status_code": 400,
  "details": {
    "seats": ["Ensure this value is greater than or equal to 1."]
  }
}
```

---

### Cars

#### List Cars

**Endpoint**: `GET /api/cars/`  
**Authentication**: Required  
**Permission**: Any authenticated user (Read-only for non-staff)

**Query Parameters**:
- `car_model` - Filter by car model ID
- `color` - Filter by color ID
- `search` - Search by license plate or model name
- `ordering` - Order by field (e.g., `license_plate`, `-mileage`)

**Success Response** (200 OK):
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "car_model": 1,
      "license_plate": "ABC-123",
      "color": 1,
      "mileage": 10000
    }
  ]
}
```

#### Create Car

**Endpoint**: `POST /api/cars/`  
**Authentication**: Required  
**Permission**: Staff only

**Request Body**:
```json
{
  "car_model": 1,
  "license_plate": "XYZ-789",
  "color": 2,
  "mileage": 0
}
```

**Validation Rules**:
- `mileage`: Cannot be negative
- `license_plate`: Must be unique

**Success Response** (201 Created):
```json
{
  "id": 2,
  "car_model": 1,
  "license_plate": "XYZ-789",
  "color": 2,
  "mileage": 0
}
```

---

## 📅 Reservation Management

### 1. Create Reservation

**Endpoint**: `POST /api/reservations/`  
**Authentication**: Required

**Request Body**:
```json
{
  "car": 1,
  "start_date": "2026-02-01",
  "end_date": "2026-02-05"
}
```

**Auto-calculated fields**:
- `coverage` - Based on user age (Young Driver / Standard / Senior/Premium)
- `rate` - Multiplier based on age (<25: 1.5x, 25-65: 1.0x, >65: 1.2x)
- `total_price` - Calculated as `duration × daily_price × rate`

**Success Response** (201 Created):
```json
{
  "id": 1,
  "user": 1,
  "car": 1,
  "start_date": "2026-02-01",
  "end_date": "2026-02-05",
  "coverage": "Standard",
  "rate": "1.00",
  "total_price": "200.00"
}
```

**Error Response** (400 - Invalid dates):
```json
{
  "error": "Client Error",
  "status_code": 400,
  "details": {
    "end_date": ["End date must be equal to or later than start date"]
  }
}
```

**Error Response** (400 - Overlapping reservation):
```json
{
  "error": "Client Error",
  "status_code": 400,
  "details": {
    "non_field_errors": ["Selected dates overlap with another reservation for this vehicle"]
  }
}
```

---

### 2. List My Reservations

**Endpoint**: `GET /api/reservations/my/`  
**Authentication**: Required

**Query Parameters**:
- `status=upcoming` - Only future reservations
- `status=past` - Only past reservations

**Success Response** (200 OK):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "car": 1,
      "start_date": "2026-02-01",
      "end_date": "2026-02-05",
      "coverage": "Standard",
      "rate": "1.00",
      "total_price": "200.00"
    },
    ...
  ]
}
```

**Filter Examples**:
```bash
# Get upcoming reservations
GET /api/reservations/my/?status=upcoming

# Get past reservations
GET /api/reservations/my/?status=past

# Get all my reservations
GET /api/reservations/my/
```

---

### 3. Delete Reservation (with Password)

**Endpoint**: `DELETE /api/reservations/{id}/delete-with-password/`  
**Authentication**: Required  
**Permission**: Owner or Staff

**Request Body**:
```json
{
  "password": "SecurePass123!"
}
```

**Rules**:
- ✅ Can delete future reservations
- ❌ Cannot delete past reservations (read-only)
- 🔒 Requires password confirmation

**Success Response** (204 No Content):
```json
{
  "message": "Reservation deleted successfully"
}
```

**Error Response** (400 - Past reservation):
```json
{
  "detail": "Past reservations cannot be deleted"
}
```

**Error Response** (400 - Wrong password):
```json
{
  "detail": "Invalid password"
}
```

**Error Response** (403 - Not owner):
```json
{
  "error": "Client Error",
  "status_code": 403,
  "details": {
    "detail": "You do not have permission to perform this action."
  }
}
```

---

### 4. List All Reservations (Staff Only)

**Endpoint**: `GET /api/reservations/`  
**Authentication**: Required  
**Permission**: Staff only

Regular users automatically only see their own reservations.  
Staff can see all reservations.

**Query Parameters**:
- `user` - Filter by user ID
- `car` - Filter by car ID
- `start_date__gte` - Reservations starting on or after date
- `end_date__lte` - Reservations ending on or before date
- `search` - Search by user email or car license plate

---

## ⚠️ Error Handling

### Standard Error Response Format

All errors follow this structure:
```json
{
  "error": "Error Type",
  "status_code": 400,
  "details": {
    "field_name": ["Error message"]
  }
}
```

### Common HTTP Status Codes

| Code | Meaning | When it occurs |
|------|---------|----------------|
| 200 | OK | Successful GET/PUT/PATCH request |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side error |

### Example Error Responses

**401 Unauthorized** (No token provided):
```json
{
  "error": "Client Error",
  "status_code": 401,
  "details": {
    "detail": "Authentication credentials were not provided."
  }
}
```

**401 Unauthorized** (Invalid/expired token):
```json
{
  "error": "Client Error",
  "status_code": 401,
  "details": {
    "detail": "Given token not valid for any token type"
  }
}
```

**403 Forbidden** (Insufficient permissions):
```json
{
  "error": "Client Error",
  "status_code": 403,
  "details": {
    "detail": "You do not have permission to perform this action."
  }
}
```

**400 Bad Request** (Validation error):
```json
{
  "error": "Client Error",
  "status_code": 400,
  "details": {
    "username": ["user with this email already exists."],
    "password": ["This field is required."]
  }
}
```

---

## 🔒 Permission Matrix

| Endpoint                                            | Anonymous | Authenticated User | Staff |
| --------------------------------------------------- | --------- | ------------------ | ----- |
| POST /api/users/ (signup)                           | ✅         | ✅                  | ✅     |
| POST /api/token/ (login)                            | ✅         | ✅                  | ✅     |
| POST /api/token/refresh/                            | ✅         | ✅                  | ✅     |
| GET /api/profile/me/                                | ❌         | ✅                  | ✅     |
| PUT /api/profile/me/                                | ❌         | ✅                  | ✅     |
| PATCH /api/profile/me/                              | ❌         | ✅                  | ✅     |
| POST /api/profile/me/change-password/               | ❌         | ✅                  | ✅     |
| DELETE /api/profile/me/                             | ❌         | ✅                  | ✅     |
| GET /api/brands/                                    | ✅         | ✅                  | ✅     |
| GET /api/vehicle-types/                             | ✅         | ✅                  | ✅     |
| GET /api/fuel-types/                                | ✅         | ✅                  | ✅     |
| GET /api/colors/                                    | ✅         | ✅                  | ✅     |
| GET /api/transmissions/                             | ✅         | ✅                  | ✅     |
| GET /api/car-models/                                | ✅         | ✅                  | ✅     |
| POST /api/car-models/                               | ❌         | ❌                  | ✅     |
| GET /api/cars/                                      | ✅         | ✅                  | ✅     |
| POST /api/cars/                                     | ❌         | ❌                  | ✅     |
| POST /api/reservations/                             | ❌         | ✅                  | ✅     |
| GET /api/reservations/my/                           | ❌         | ✅                  | ✅     |
| DELETE /api/reservations/{id}/delete-with-password/ | ❌         | ✅                  | ✅     |
| GET /api/reservations/ (all)                        | ❌         | ❌                  | ✅     |
| GET /api/users/                                     | ❌         | ❌                  | ✅     |
| GET /api/users/{id}/                                | ❌         | ❌                  | ✅     |

---

## ⚙️ Rate Limiting

# Overview
To prevent abuse and ensure fair API usage, all endpoints are subject to rate limits depending on the user's authentication status.

| User Type     | Limit | Window   | Description                         |
| ------------- | ----- | -------- | ----------------------------------- |
| Anonymous     | 100   | per hour | Unauthenticated requests            |
| Authenticated | 1000  | per hour | Logged-in users (JWT-authenticated) |
| Staff         | 5000  | per hour | Admin users or automation scripts   |

---

## 🧩 Versioning & Metadata
# API Version: v1.0

Framework: Django REST Framework
Token Algorithm: HS256
Response Format: JSON
Pagination: LimitOffset (default limit = 10)