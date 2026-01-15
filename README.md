# vehicle-rental-system
A vehicle rental management system developed as a web application based on a REST API.
Vehicle Renting API
Complete CRUD API for vehicle rental management.

🚀 Quick Installation
bash
git clone https://github.com/Bootcamp-IA-P6/Proyecto2_CRUD_Equipo5.git
cd Proyecto2_CRUD_Equipo5
pip install -r requirements.txt
🗄️ Database Setup
Create .env file:

text
DATABASE_URL=mysql://user:password@localhost:3306/renting_db
SECRET_KEY=your-secret-key-here
DEBUG=True
bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser
▶️ Run Project
bash
python manage.py runserver
🌐 Open http://localhost:8000

📋 API Endpoints
text
GET/POST/PUT/DELETE /api/users/
GET/POST/PUT/DELETE /api/vehicles/  
GET/POST/PUT/DELETE /api/reservations/
🏗️ Project Structure
text
renting/
├── models/         # User, Vehicle, Reservation
├── serializers/    # API serialization
├── views/          # CRUD logic
├── urls/           # API routes
├── templates/      # HTML pages
└── admin/          # Admin panel