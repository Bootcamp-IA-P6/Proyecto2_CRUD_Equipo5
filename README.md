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

## 🛠 Database Setup & Initialization
Follow these steps to set up the database schema and load initial sample data.

### 1. Create Database (Manual Step)
Before running migrations, you must manually create the database in your MySQL server:
```sql
CREATE DATABASE renting_db;
```


### 2. Environment Configuration
Create a `.env` file in the root directory and configure your credentials:
```env
DB_NAME=renting_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

SECRET_KEY=your-django-secret-key
DEBUG=True
```


### 3. Database Migrations
Generate and apply the table schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

If needed:
```bash
python manage.py createsuperuser
```


### 4. Seeding Sample Data
Run the custom management command to populate the database with 15 Users, 15 Cars, and 25 Reservations.
```bash
python manage.py seed_data
```

Note:
- This command ensures all users are created with properly hashed passwords, allowing immediate login via JWT.
- Reservations are created with automatically calculated prices and coverage levels (Young Driver, Standard, Senior/Premium) based on the users' birth dates.


### 5. Default Credentials
After seeding, you can log in with any of the 15 generated accounts.
- **Username**: user1@example.com ~ user15@example.com
- **Password (for all)**: pass1234

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
