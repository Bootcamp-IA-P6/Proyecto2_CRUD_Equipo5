# 🚗 Car Rental System - Backend API

A comprehensive car rental management system built with **Django REST Framework** and **JWT authentication**. This project implements secure user management, vehicle inventory, and reservation handling with role-based access control.

---

## 📑 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Testing](#-testing)
- [Business Logic](#-business-logic)
- [Database Diagram (ERD)](#-database-diagram-erd)
- [Project Retrospective](#-project-retrospective)
- [Contributors](#-contributors)


---

## ✨ Features

### User Management
- 🔐 JWT-based authentication (login, signup, token refresh)
- 👤 User profile management with password confirmation
- 🔒 Secure password change endpoint
- 🗑️ Account self-deletion with password verification

### Vehicle Management
- 🚙 Complete vehicle catalog (cars, models, brands, specifications)
- 📊 Admin-only vehicle creation and management
- 🔍 Advanced filtering and search capabilities
- ✅ Data validation at model level (negative values prevention, range checks)

### Reservation System
- 📅 Create and manage reservations
- 🔐 Password-protected reservation deletion
- 🚫 Past reservation protection (read-only)
- 📈 Automatic price calculation based on:
  - Rental duration
  - User age (Young Driver / Standard / Senior pricing)
  - Daily vehicle rate
- 🔍 Filter reservations by status (upcoming/past)

### Security & Permissions
- 🛡️ Role-based access control (Staff vs Regular users)
- 🔒 User data isolation (users only see their own data)
- ✅ Password confirmation for sensitive operations
- 🚫 Comprehensive validation (API + Admin)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Django 6.0.1 |
| **API** | Django REST Framework 3.15+ |
| **Authentication** | Simple JWT (djangorestframework-simplejwt) |
| **Database** | MySQL 8.0+ |
| **Validation** | Django Validators + Custom clean() methods |
| **Filtering** | django-filter |
| **Testing** | Django TestCase + APITestCase |
| **Admin** | Django Admin (enhanced with custom configurations) |

---

## 📁 Project Structure
```
proyecto/
├── renting_project/          # Main Django project
│   ├── settings.py           # Project settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI config
│
├── renting/                  # Main application
│   ├── models.py            # Data models (User, Car, Reservation, etc.)
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # ViewSets and business logic
│   ├── profile_views.py     # User profile endpoints
│   ├── permissions.py       # Custom permission classes
│   ├── admin.py             # Django Admin configuration
│   ├── exceptions.py        # DRF exceptions logic
│   ├── filters.py           # Filters logic for business
│   ├── pagination.py        # Dynamic page size
│   ├── apps.py              # Django apps
│   ├── urls.py              # App-level routing
│   │
│   ├── tests/               # Test suite
│   │   ├── test_auth.py           # Authentication tests
│   │   ├── test_profile.py        # Profile management tests
│   │   ├── test_reservations.py   # Reservation tests
│   │   ├── test_vehicles.py       # Vehicle tests
│   │   └── test_permissions.py    # Permission tests
│   │
│   └── docs/
│       └── erd/             # Database diagrams
│
├── docs/
│   └── API_GUIDE.md         # Complete API documentation
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip
- virtualenv (recommended)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_ORG/proyecto.git
cd proyecto
```

2. **Create and activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🗄️ Database Setup

### MySQL Database Creation
```sql
CREATE DATABASE renting_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```env
DB_NAME=renting_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

SECRET_KEY=your-secret-key-here
DEBUG=True
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Initial Data (Optional)

Run the custom management command to populate the database with 110 Users, 50 Cars, and 230 Reservations.
```bash
python manage.py seed_data
```

---

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`


---

## 📚 API Documentation

Complete API documentation is available in **[docs/API_GUIDE.md](docs/API_GUIDE.md)**.

### Quick Start

#### 1. **Register a new user**
```bash
POST /api/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "birth_date": "1990-01-01",
  "license_number": "ABC123456"
}
```

#### 2. **Login and get JWT tokens**
```bash
POST /api/token/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePass123!"
}

# Response:
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 3. **Access protected endpoints**
```bash
GET /api/profile/me/
Authorization: Bearer <access_token>
```

See **[API_GUIDE.md](docs/API_GUIDE.md)** for complete endpoint documentation.

---

## 🔐 Authentication

This project uses **JWT (JSON Web Tokens)** for authentication.

### Token Flow

1. **Obtain tokens**: `POST /api/token/` with email/password
2. **Use access token**: Include in `Authorization: Bearer <token>` header
3. **Refresh token**: `POST /api/token/refresh/` when access token expires

### Token Lifetimes

- **Access Token**: 30 minutes
- **Refresh Token**: 1 day

---

## 🧪 Testing

The project includes comprehensive test coverage (45+ tests).

### Run all tests
```bash
python manage.py test renting.tests
```

### Run specific test file
```bash
python manage.py test renting.tests.test_auth
python manage.py test renting.tests.test_reservations
```


### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Authentication | 10 tests | Signup, login, token refresh, 401/403 |
| Profile Management | 10 tests | GET/PUT/PATCH/DELETE, password validation |
| Reservations | 11 tests | CRUD, filtering, deletion rules |
| Vehicles | 9 tests | Cars, models, validation |
| Permissions | 5 tests | Staff-only, authorization |
| **Total** | **44 tests** | **Complete API coverage** |

---

## 💼 Business Logic

### Automatic Price Calculation

Reservations automatically calculate pricing based on:
```python
# User age determines rate multiplier
< 25 years   → Young Driver (rate: 1.5x)
25-65 years  → Standard (rate: 1.0x)
> 65 years   → Senior/Premium (rate: 1.2x)

# Total price formula
total_price = (end_date - start_date + 1) × daily_price × rate
```

### Data Validation

**Model-level validation** prevents:
- ❌ Negative values (seats, mileage, prices)
- ❌ Invalid ranges (seats: 1-50, year: 1900-2100)
- ❌ Overlapping reservations for same vehicle
- ❌ End date before start date
- ❌ Zero or negative prices

**Permission-based validation**:
- 🔒 All profile modifications require password confirmation
- 🔒 Reservation deletion requires password
- 🔒 Past reservations are read-only (cannot be deleted)
- 🔒 Users can only access their own data (except staff)

---

## 📐 Database Diagram (ERD)

The Entity-Relationship Diagram is located in `renting/docs/erd/`.

### Core Models
```
AppUser ──┬── Reservation ──── Car ──── CarModel ──┬── Brand
          │                                        ├── VehicleType
          │                                        ├── FuelType
          └──────────────────────────────────────── Transmission
                                                    
                                         Color ──── Car
```

### Key Relationships

- **AppUser → Reservation**: One-to-many (a user can have multiple reservations)
- **Car → Reservation**: One-to-many (a car can be reserved multiple times)
- **CarModel → Car**: One-to-many (a model can have multiple car instances)
- **Brand/VehicleType/etc. → CarModel**: Many-to-one (lookup tables)

**View full ERD**: See `renting/docs/erd/erd.png`

---

## 👥 Contributors

This project was developed as part of an educational program. Special thanks to:

- **Mirae** – Project Lead, Backend & Frontend Development  
  GitHub: [https://github.com/KangMirae](https://github.com/KangMirae)

- **Raúl** – Database Design & Backend Development  
  GitHub: [https://github.com/RaulCtm](https://github.com/RaulCtm)

- **Isabel** – QA, Documentation & Backend Development  
  GitHub: [https://github.com/isrodam](https://github.com/isrodam)

---

## 📘 Project Retrospective

This project includes a detailed Project Retrospective Document, which summarizes the overall development process — covering achievements, challenges, lessons learned, and personal insights from each team member.

It provides a transparent view of the project’s evolution, focusing on:

- Key successes and obstacles faced during development

- Lessons learned from sprint‑based collaboration

- Improvement areas and reflections from individual contributors

For an in‑depth overview, please visit the full retrospective document:
👉 **renting/docs/PROJECT_RETROSPECTIVE.md**

---

## 🙏 Acknowledgments

- Django Software Foundation for the excellent framework
- Django REST Framework team for the powerful API toolkit
- All contributors and reviewers who helped improve this project

---

**Project Status**: ✅ Active Development  
**Last Updated**: January 2026