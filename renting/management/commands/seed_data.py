# renting/management/commands/seed_data.py
import random
import string
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from renting.models import (
    AppUser, Brand, CarModel, Car, VehicleType, 
    FuelType, Color, Transmission, Reservation
)

class Command(BaseCommand):
    help = 'Seeds realistic data for 30 users, 20 models, 30 cars, and 100 reservations'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🧹 Starting realistic database seed (Spanish Context)..."))

        # --- 1. Basic Lookup Tables (Realistic Names) ---
        virtual_brands = ["Boreal Motors", "VoltEra", "Iberia Drive", "NovaVelo", "BayerMotive", "Solano Cars", "Zenith Auto"]
        brand_objs = [Brand.objects.get_or_create(name=b)[0] for b in virtual_brands]

        v_types = ["Sedan", "SUV", "Compact", "Van", "Coupe", "Truck"]
        v_type_objs = [VehicleType.objects.get_or_create(name=v)[0] for v in v_types]

        fuels = ["Gasoline", "Diesel", "Electric", "Hybrid"]
        fuel_objs = [FuelType.objects.get_or_create(name=f)[0] for f in fuels]

        colors = ["White", "Black", "Silver", "Grey", "Blue", "Red"]
        color_objs = [Color.objects.get_or_create(name=c)[0] for c in colors]

        trans = ["Automatic", "Manual"]
        trans_objs = [Transmission.objects.get_or_create(name=t)[0] for t in trans]

        # --- 2. 20 Unique Car Models (Virtual Names) ---
        virtual_models = [
            ("Civis", "Boreal Motors"), ("Prime", "Boreal Motors"), ("Neo", "VoltEra"), ("Surge", "VoltEra"),
            ("Ruta", "Iberia Drive"), ("Costa", "Iberia Drive"), ("Viento", "Iberia Drive"), ("Astro", "NovaVelo"),
            ("Pulse", "NovaVelo"), ("Kinetix", "BayerMotive"), ("Apex", "BayerMotive"), ("Luna", "Solano Cars"),
            ("Sol", "Solano Cars"), ("Horizon", "Solano Cars"), ("Summit", "Zenith Auto"), ("Peak", "Zenith Auto"),
            ("Atlas", "Zenith Auto"), ("Eon", "NovaVelo"), ("Flow", "VoltEra"), ("Giro", "Iberia Drive")
        ]
        
        model_objs = []
        for m_name, b_name in virtual_models:
            brand_ptr = next(b for b in brand_objs if b.name == b_name)
            model, _ = CarModel.objects.get_or_create(
                model_name=m_name,
                brand=brand_ptr,
                defaults={
                    'vehicle_type': random.choice(v_type_objs),
                    'fuel_type': random.choice(fuel_objs),
                    'transmission': random.choice(trans_objs),
                    'seats': random.choice([2, 4, 5, 7]),
                    'daily_price': Decimal(random.randint(40, 150))
                }
            )
            model_objs.append(model)

        # --- 3. 30 Physical Cars (Spanish Plate Format: 1234 ABC) ---
        car_objs = []
        consonants = "BCDFGHJKLMNPQRSTVWXYZ" # Spanish plates don't use vowels
        for i in range(30):
            plate_num = f"{random.randint(1000, 9999)}"
            plate_letters = "".join(random.choices(consonants, k=3))
            plate = f"{plate_num} {plate_letters}"
            
            car, _ = Car.objects.get_or_create(
                license_plate=plate,
                defaults={
                    'car_model': random.choice(model_objs),
                    'color': random.choice(color_objs),
                    'mileage': random.randint(100, 95000)
                }
            )
            car_objs.append(car)

        # --- 4. 30 Users (Spanish Names & DNI: 12345678X) ---
        first_names = ["Enrique Manuel", "María Josefa", "Juan Carlos", "Lucía Elena", "Jorge", "Carmen", "Sergio", "Paula", "Miguel Ángel", "Sofía", "Diego", "Isabel", "Javier", "Marta", "Raúl"]
        last_names = ["López González", "García Martínez", "Rodríguez Pérez", "Sánchez Romero", "Fernández Ruiz", "Jiménez Díaz", "Álvarez Moreno", "Muñoz Vega", "Romero Martín", "Alonso Serrano"]
        
        user_objs = []
        for i in range(30):
            email = f"user{i+1}@example.com"
            # Age range: 1950 to 2007 (Min 18+ as of 2026)
            birth_year = random.randint(1950, 2007)
            
            # Spanish DNI format: 8 digits + 1 uppercase letter
            dni = f"{random.randint(10000000, 99999999)}{random.choice(string.ascii_uppercase)}"
            
            user, created = AppUser.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': random.choice(first_names),
                    'last_name': random.choice(last_names),
                    'birth_date': date(birth_year, random.randint(1, 12), random.randint(1, 28)),
                    'license_number': dni
                }
            )
            if created:
                user.set_password("Pass1234!")
                user.save()
            user_objs.append(user)

        # --- 5. 100 Reservations (Past & Future) ---
        today = date.today()
        res_count = 0
        for user in user_objs:
            # Each user gets around 3-4 reservations to reach ~100 total
            for _ in range(random.randint(3, 4)):
                car = random.choice(car_objs)
                
                # Mixture of Past (2024-2025) and Future (2026)
                if random.random() > 0.4: 
                    start = today + timedelta(days=random.randint(5, 90)) # Future
                else: 
                    start = today - timedelta(days=random.randint(30, 365)) # Past
                
                end = start + timedelta(days=random.randint(1, 14))
                
                try:
                    res = Reservation(user=user, car=car, start_date=start, end_date=end)
                    res.save() # Automatic price/coverage calculation
                    res_count += 1
                except Exception:
                    continue # Skip if dates overlap

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully seeded: 30 Users (DNI), 20 Models, 30 Cars (Plates), and {res_count} Reservations!"))