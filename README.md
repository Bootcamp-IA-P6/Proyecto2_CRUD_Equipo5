# 🚗 Vehicle Rental System

A **vehicle rental management system** developed as a **web application** based on a **REST API**.
This project provides a **complete CRUD API** for managing users, vehicles, and reservations.

---

## ✨ Features

* 🔐 User management
* 🚘 Vehicle management
* 📅 Reservation system
* 🛠️ Full CRUD operations
* 🌐 RESTful API architecture
* 🧑‍💼 Admin panel support

---

## 🚀 Quick Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Bootcamp-IA-P6/Proyecto2_CRUD_Equipo5.git
cd Proyecto2_CRUD_Equipo5


# Create virtual environment
python -m venv venv


# Activate virtual environment
# Windows
venv\Scripts\activate


# Linux / macOS
source venv/bin/activate


# Install dependencies
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

Create a `.env` file in the root directory of the project:

```env
DB_NAME=vehicle_rental_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

SECRET_KEY=your-secret-key-here
DEBUG=True
```

Run migrations and create the admin user:

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser
```

---

## ▶️ Run Project

Start the development server:

```bash
python manage.py runserver
```

🌐 Open in your browser:
**[http://localhost:8000](http://localhost:8000)**

---

## 📋 API Endpoints

```text
GET     /api/users/
POST    /api/users/
PUT     /api/users/{id}/
DELETE  /api/users/{id}/

GET     /api/vehicles/
POST    /api/vehicles/
PUT     /api/vehicles/{id}/
DELETE  /api/vehicles/{id}/

GET     /api/reservations/
POST    /api/reservations/
PUT     /api/reservations/{id}/
DELETE  /api/reservations/{id}/
```

---

## 🏗️ Project Structure

```text
renting/
├── models/         # User, Vehicle, Reservation
├── serializers/    # API serialization
├── views/          # CRUD logic
├── urls/           # API routes
├── templates/      # HTML pages
└── admin/          # Admin panel
```

---

## 🧰 Tech Stack

* 🐍 Python
* 🌐 Django
* 🔗 Django REST Framework
* 🐬 MySQL
* ⚙️ dotenv

---

## 📄 License

This project is for **educational purposes**.

---

💙 Built with passion by **Equipo 5**
