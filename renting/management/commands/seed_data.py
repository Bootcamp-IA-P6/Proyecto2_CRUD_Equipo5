import random
import string
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from renting.models import (
    AppUser, Brand, CarModel, Car, VehicleType,
    FuelType, Color, Transmission, Reservation
)

SEATS_BY_TYPE = {
    "Sedan": 5,
    "SUV": 7,
    "Compact": 4,
    "Van": 9,
    "Coupe": 4,
    "Truck": 2,
}

class Command(BaseCommand):
    help = "Strict seed following fixed model rules (models, cars, users, reservations)"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🧹 Seeding database with strict consistency rules..."))

        # -----------------------------
        # 1. Lookup tables
        # -----------------------------
        brands = [
            "Boreal Motors", "VoltEra", "Iberia Drive",
            "NovaVelo", "BayerMotive", "Solano Cars", "Zenith Auto"
        ]
        brand_objs = {b: Brand.objects.get_or_create(name=b)[0] for b in brands}

        vehicle_types = ["Sedan", "SUV", "Compact", "Van", "Coupe", "Truck"]
        vt_objs = {v: VehicleType.objects.get_or_create(name=v)[0] for v in vehicle_types}

        fuels = ["Gasoline", "Diesel", "Electric", "Hybrid"]
        fuel_objs = {f: FuelType.objects.get_or_create(name=f)[0] for f in fuels}

        transmissions = ["Automatic", "Manual"]
        trans_objs = {t: Transmission.objects.get_or_create(name=t)[0] for t in transmissions}

        colors = ["White", "Black", "Silver", "Grey", "Blue", "Red"]
        color_objs = {c.lower(): Color.objects.get_or_create(name=c)[0] for c in colors}

        # -----------------------------
        # 2. CarModel definitions (30)
        # -----------------------------
        model_definitions = [
            # model_name, brand, type, fuel, trans
            ("civis_red", "Boreal Motors", "Sedan", "Gasoline", "Automatic"),
            ("civis_white", "Boreal Motors", "Sedan", "Gasoline", "Automatic"),
            ("pulse_black", "NovaVelo", "Coupe", "Hybrid", "Manual"),
            ("pulse_blue", "NovaVelo", "Coupe", "Hybrid", "Manual"),
            ("neo_grey", "VoltEra", "Compact", "Electric", "Automatic"),
            ("neo_white", "VoltEra", "Compact", "Electric", "Automatic"),
            ("ruta_red", "Iberia Drive", "SUV", "Diesel", "Manual"),
            ("ruta_black", "Iberia Drive", "SUV", "Diesel", "Manual"),
            ("atlas_silver", "Zenith Auto", "Truck", "Diesel", "Manual"),
            ("atlas_black", "Zenith Auto", "Truck", "Diesel", "Manual"),
            ("luna_white", "Solano Cars", "Van", "Hybrid", "Automatic"),
            ("luna_blue", "Solano Cars", "Van", "Hybrid", "Automatic"),
            ("apex_red", "BayerMotive", "Sedan", "Gasoline", "Automatic"),
            ("apex_black", "BayerMotive", "Sedan", "Gasoline", "Automatic"),
            ("flow_blue", "VoltEra", "SUV", "Electric", "Automatic"),
            ("flow_grey", "VoltEra", "SUV", "Electric", "Automatic"),
            ("giro_white", "Iberia Drive", "Compact", "Gasoline", "Manual"),
            ("giro_red", "Iberia Drive", "Compact", "Gasoline", "Manual"),
            ("summit_black", "Zenith Auto", "SUV", "Hybrid", "Automatic"),
            ("summit_white", "Zenith Auto", "SUV", "Hybrid", "Automatic"),
            ("sol_red", "Solano Cars", "Sedan", "Gasoline", "Manual"),
            ("sol_grey", "Solano Cars", "Sedan", "Gasoline", "Manual"),
            ("horizon_blue", "Solano Cars", "SUV", "Hybrid", "Automatic"),
            ("horizon_black", "Solano Cars", "SUV", "Hybrid", "Automatic"),
            ("eon_white", "NovaVelo", "Compact", "Electric", "Automatic"),
            ("eon_black", "NovaVelo", "Compact", "Electric", "Automatic"),
            ("peak_silver", "Zenith Auto", "Coupe", "Gasoline", "Manual"),
            ("peak_red", "Zenith Auto", "Coupe", "Gasoline", "Manual"),
            ("surge_blue", "VoltEra", "Sedan", "Hybrid", "Automatic"),
            ("surge_white", "VoltEra", "Sedan", "Hybrid", "Automatic"),
        ]

        model_objs = []
        for name, brand, vtype, fuel, trans in model_definitions:
            model, _ = CarModel.objects.get_or_create(
                model_name=name,
                brand=brand_objs[brand],
                defaults={
                    "vehicle_type": vt_objs[vtype],
                    "fuel_type": fuel_objs[fuel],
                    "transmission": trans_objs[trans],
                    "seats": SEATS_BY_TYPE[vtype],
                    "daily_price": Decimal(random.randint(50, 150)),
                    "image": f"{brand.lower().replace(' ', '_')}_{name}.jpg",
                },
            )
            model_objs.append(model)

        # -----------------------------
        # 3. Cars (50)
        # -----------------------------
        car_objs = []
        consonants = "BCDFGHJKLMNPQRSTVWXYZ"

        for i in range(50):
            model = model_objs[i % len(model_objs)]
            color_key = model.model_name.split("_")[-1]

            plate = f"{random.randint(1000,9999)} {''.join(random.choices(consonants, k=3))}"

            car = Car.objects.create(
                license_plate=plate,
                car_model=model,
                color=color_objs[color_key],
                mileage=random.randint(500, 120000),
            )
            car_objs.append(car)

        # -----------------------------
        # 4. Users (100)
        # -----------------------------
        first_names = [
            "Juan Carlos", "María José", "Enrique Manuel", "Lucía Elena",
            "Miguel Ángel", "Ana María", "José Luis", "Laura Isabel",
            "Pedro Antonio", "Sofía Cristina"
        ]
        last_names = [
            "López González", "García Martínez", "Rodríguez Pérez",
            "Sánchez Romero", "Fernández Ruiz", "Jiménez Díaz",
            "Álvarez Moreno", "Muñoz Vega"
        ]

        user_objs = []
        for i in range(100):
            user = AppUser.objects.create(
                email=f"user{i+1}@example.com",
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                birth_date=date(random.randint(1950, 2005), random.randint(1,12), random.randint(1,28)),
                license_number=f"{random.randint(10000000,99999999)}{random.choice(string.ascii_uppercase)}",
            )
            user.set_password("Pass1234!")
            user.save()
            user_objs.append(user)

        # -----------------------------
        # 5. Reservations
        # -----------------------------
        today = date.today()
        for user in user_objs:
            for is_future in [False, True]:
                while True:
                    car = random.choice(car_objs)
                    start = today + timedelta(days=random.randint(10, 90)) if is_future else today - timedelta(days=random.randint(30, 365))
                    end = start + timedelta(days=random.randint(1, 10))
                    try:
                        Reservation.objects.create(
                            user=user,
                            car=car,
                            start_date=start,
                            end_date=end
                        )
                        break
                    except Exception:
                        continue

        self.stdout.write(self.style.SUCCESS("✅ Seed completed with full consistency."))