import random
import string
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from renting.models import (
    AppUser, Brand, CarModel, Car,
    VehicleType, FuelType, Color,
    Transmission, Reservation
)

SEATS_BY_TYPE = {
    "Sedan": [4, 5],
    "SUV": [5, 7],
    "Compact": [4],
    "Van": [7, 9],
    "Coupe": [2, 4],
    "Truck": [2],
}

class Command(BaseCommand):
    help = "Seeds data: 7 brands, 30 models, 50 cars, 100+ users, 50+ reservations"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🧹 Seeding database (final realistic version)..."))

        # ---------- LOOKUP TABLES ----------
        brands = [
            "Boreal Motors", "VoltEra", "Iberia Drive",
            "NovaVelo", "Solano Cars", "Zenith Auto", "Auron Mobility"
        ]
        brand_objs = [Brand.objects.get_or_create(name=b)[0] for b in brands]

        vehicle_types = ["Sedan", "SUV", "Compact", "Van", "Coupe", "Truck"]
        vtype_objs = {v: VehicleType.objects.get_or_create(name=v)[0] for v in vehicle_types}

        fuels = ["Gasoline", "Diesel", "Electric", "Hybrid"]
        fuel_objs = [FuelType.objects.get_or_create(name=f)[0] for f in fuels]

        colors = ["White", "Black", "Silver", "Grey", "Blue", "Red"]
        color_objs = {c: Color.objects.get_or_create(name=c)[0] for c in colors}

        transmissions = ["Automatic", "Manual"]
        trans_objs = {t: Transmission.objects.get_or_create(name=t)[0] for t in transmissions}

        # ---------- CAR MODELS (30 UNIQUE) ----------
        model_names = [
            "Civis", "Astra", "Lumo", "Vento", "Ridge", "Orion",
            "Pulse", "Atlas", "Nexo", "Kairo", "Solace", "Drift",
            "Terra", "Flux", "Nova", "Elios", "Summit", "Trail",
            "Haven", "Axion", "Vertex", "Comet", "Strato", "Glide",
            "Monza", "Vector", "Echo", "Zenon", "Pyxis", "Argo"
        ]

        model_objs = []
        for name in model_names:
            brand = random.choice(brand_objs)
            vtype = random.choice(vehicle_types)
            seats = random.choice(SEATS_BY_TYPE[vtype])

            model, _ = CarModel.objects.get_or_create(
                model_name=name,
                brand=brand,
                defaults={
                    "vehicle_type": vtype_objs[vtype],
                    "fuel_type": random.choice(fuel_objs),
                    "transmission": random.choice(list(trans_objs.values())),
                    "seats": seats,
                    "daily_price": Decimal(random.randint(40, 160)),
                }
            )
            model_objs.append(model)

        # ---------- CARS (50, ALL MODELS INCLUDED) ----------
        car_objs = []
        consonants = "BCDFGHJKLMNPQRSTVWXYZ"

        # ensure every model appears at least once
        base_models = model_objs.copy()
        random.shuffle(base_models)

        while len(car_objs) < 50:
            model = base_models.pop() if base_models else random.choice(model_objs)

            plate = f"{random.randint(1000,9999)} {''.join(random.choices(consonants,k=3))}"
            color = random.choice(list(color_objs.values()))

            car, _ = Car.objects.get_or_create(
                license_plate=plate,
                defaults={
                    "car_model": model,
                    "color": color,
                    "mileage": random.randint(100, 120000)
                }
            )
            car_objs.append(car)

        # ---------- USERS (100+) ----------
        first_names = [
            "Juan Carlos", "María José", "Luis Miguel", "Ana Belén",
            "José Manuel", "Lucía Elena", "Pedro", "Carmen",
            "Miguel Ángel", "Sofía", "Diego", "Raúl",
            "Isabel", "Javier", "Paula", "Alberto"
        ]
        last_names = [
            "López González", "García Martínez", "Rodríguez Pérez",
            "Sánchez Romero", "Fernández Ruiz", "Jiménez Díaz",
            "Álvarez Moreno", "Muñoz Vega", "Romero Martín",
            "Alonso Serrano"
        ]

        user_objs = []
        for i in range(110):
            email = f"user{i+1}@example.com"
            birth_year = random.randint(1950, 2005)
            dni = f"{random.randint(10000000,99999999)}{random.choice(string.ascii_uppercase)}"

            user, created = AppUser.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": random.choice(first_names),
                    "last_name": random.choice(last_names),
                    "birth_date": date(birth_year, random.randint(1,12), random.randint(1,28)),
                    "license_number": dni
                }
            )
            if created:
                user.set_password("Pass1234!")
                user.save()
            user_objs.append(user)

        # ---------- RESERVATIONS (PAST + FUTURE, NO OVERLAPS) ----------
        today = date.today()
        used_slots = {car.id: [] for car in car_objs}
        res_count = 0

        for user in user_objs:
            for is_future in [False, True]:
                for _ in range(10):  # try until success
                    car = random.choice(car_objs)

                    if is_future:
                        start = today + timedelta(days=random.randint(5, 120))
                    else:
                        start = today - timedelta(days=random.randint(30, 400))

                    end = start + timedelta(days=random.randint(1, 10))

                    # overlap check
                    if any(s < end and start < e for s, e in used_slots[car.id]):
                        continue

                    try:
                        res = Reservation(user=user, car=car, start_date=start, end_date=end)
                        res.save()  # business logic applies here
                        used_slots[car.id].append((start, end))
                        res_count += 1
                        break
                    except Exception:
                        continue

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Seed complete: {len(brand_objs)} brands, "
                f"{len(model_objs)} models, {len(car_objs)} cars, "
                f"{len(user_objs)} users, {res_count} reservations"
            )
        )