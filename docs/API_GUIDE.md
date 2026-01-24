# 📖 API Usage Guide (JWT & Auth Flow)

This guide documents the authentication process and the main API endpoints for the Vehicle Rental Management System.

---

## 🔐 1. Authentication Flow (JWT)

We use JSON Web Tokens (JWT) to secure our API. Follow these steps to interact with protected data.

### Step 1: Login to Obtain Tokens
Send your credentials to the token endpoint.
- **URL:** `/api/token/`
- **Method:** `POST`
- **Body:**
{
    "username": "user1@example.com",
    "password": "pass1234"
}
*Note: The key remains `username` even though we use the email address.*

### Step 2: Use the Access Token
Include the `access` token in the header of every subsequent request.
- **Header:** `Authorization: Bearer <your_access_token>`

---

## 🚦 2. API Endpoints Registry

| Category | Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | POST | `/api/token/` | Obtain Access & Refresh tokens | No |
| | POST | `/api/token/refresh/` | Refresh expired Access token | No |
| **Users** | POST | `/api/users/` | User Registration | No |
| | GET | `/api/users/me/` | Get current logged-in user data | **Yes** |
| **Cars** | GET | `/api/cars/` | List all physical vehicles | **Yes** |
| | GET | `/api/car-models/` | List car models and prices | **Yes** |
| **Reservations**| GET | `/api/reservations/`| List your own reservations | **Yes** |
| | POST | `/api/reservations/`| Create a new booking | **Yes** |

---

## 📝 3. Request Examples

### Creating a Reservation
The system automatically calculates the `total_price` and `coverage` based on the user's age and the car's daily rate.
- **Endpoint:** `POST /api/reservations/`
- **Payload:**
{
    "car": 1,
    "start_date": "2026-02-10",
    "end_date": "2026-02-12"
}

---

## 📑 4. Pagination

All "List" endpoints return paginated data to optimize performance.
- **Query Parameter:** `?page=1`
- **Response Format:**
{
    "count": 15,
    "next": "http://127.0.0.1:8000/api/cars/?page=2",
    "previous": null,
    "results": [ ... ]
}
*Your frontend logic should always look for the `results` key to display the data.*

---

## 🛠 5. Error Handling

- **401 Unauthorized:** Token is missing, expired, or invalid. Redirect the user to `/login/`.
- **400 Bad Request:** Validation failed (e.g., duplicate email, end_date before start_date).
- **404 Not Found:** The requested resource or URL does not exist.