# renting/management/commands/seed_data.py
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from renting.models import (
    AppUser, Brand, CarModel, Car, VehicleType, 
    FuelType, Color, Transmission, Reservation
)

class Command(BaseCommand):
    help = 'Seeds fixed Car/Model data and dynamic Spanish Users/Reservations (Issue #77 Update)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🧹 Starting consistent database seed..."))

        # 1. 고정 데이터 정의 (Constants)
        SEATS_BY_TYPE = {
            "Sedan": 5, "SUV": 7, "Compact": 4, "Van": 9, "Coupe": 4, "Truck": 2,
        }
        VEHICLE_TYPES = ["Sedan", "SUV", "Compact", "Van", "Coupe", "Truck"]
        BRANDS = ["Boreal Motors", "VoltEra", "Iberia Drive", "NovaVelo", "BayerMotive", "Solano Cars", "Zenith Auto"]
        FUELS = ["Gasoline", "Diesel", "Electric", "Hybrid"]
        TRANSMISSIONS = ["Automatic", "Manual"]
        COLORS = ["White", "Black", "Silver", "Grey", "Blue", "Red"]

        # 2. 기초 테이블 생성 (Lookup Tables)
        brand_map = {name: Brand.objects.get_or_create(name=name)[0] for name in BRANDS}
        vtype_map = {name: VehicleType.objects.get_or_create(name=name)[0] for name in VEHICLE_TYPES}
        fuel_map = {name: FuelType.objects.get_or_create(name=name)[0] for name in FUELS}
        trans_map = {name: Transmission.objects.get_or_create(name=name)[0] for name in TRANSMISSIONS}
        color_map = {name: Color.objects.get_or_create(name=name)[0] for name in COLORS}

        # 3. 30개 고정 CarModel 데이터 (이미지 파일명 규칙 준수)
        # (브랜드, 베이스모델명, 컬러, 타입, 연료, 변속기, 가격)
        MODEL_DATA = [
            ("Boreal Motors", "Civis", "Red", "Sedan", "Gasoline", "Automatic", 55),
            ("Boreal Motors", "Civis", "White", "Sedan", "Gasoline", "Manual", 50),
            ("Boreal Motors", "Prime", "Black", "SUV", "Diesel", "Automatic", 85),
            ("VoltEra", "Neo", "Blue", "Compact", "Electric", "Automatic", 45),
            ("VoltEra", "Neo", "Grey", "Compact", "Electric", "Automatic", 45),
            ("VoltEra", "Surge", "Silver", "SUV", "Hybrid", "Automatic", 95),
            ("Iberia Drive", "Ruta", "White", "Van", "Diesel", "Manual", 75),
            ("Iberia Drive", "Costa", "Blue", "Coupe", "Gasoline", "Manual", 110),
            ("Iberia Drive", "Viento", "Red", "Coupe", "Gasoline", "Automatic", 120),
            ("NovaVelo", "Astro", "Black", "Sedan", "Hybrid", "Automatic", 65),
            ("NovaVelo", "Pulse", "Grey", "Compact", "Gasoline", "Manual", 40),
            ("BayerMotive", "Kinetix", "Silver", "Sedan", "Diesel", "Automatic", 70),
            ("BayerMotive", "Apex", "Black", "SUV", "Gasoline", "Automatic", 130),
            ("Solano Cars", "Luna", "White", "Compact", "Electric", "Automatic", 50),
            ("Solano Cars", "Sol", "Red", "Hatchback", "Hybrid", "Manual", 55), # Hatchback은 없으니 Compact으로 대체
            ("Zenith Auto", "Summit", "Grey", "Truck", "Diesel", "Manual", 90),
            ("Zenith Auto", "Peak", "Black", "Truck", "Diesel", "Manual", 95),
            ("Zenith Auto", "Atlas", "Silver", "SUV", "Gasoline", "Automatic", 140),
            ("Boreal Motors", "Civis", "Blue", "Sedan", "Gasoline", "Manual", 52),
            ("VoltEra", "Eon", "White", "Sedan", "Electric", "Automatic", 60),
            ("Iberia Drive", "Giro", "Black", "Compact", "Gasoline", "Manual", 35),
            ("NovaVelo", "Flow", "Blue", "Sedan", "Hybrid", "Automatic", 68),
            ("BayerMotive", "Stratos", "Silver", "SUV", "Diesel", "Automatic", 115),
            ("Solano Cars", "Horizon", "Grey", "SUV", "Hybrid", "Automatic", 88),
            ("Zenith Auto", "Apex", "Red", "SUV", "Gasoline", "Automatic", 125),
            ("Boreal Motors", "Nova", "White", "Compact", "Gasoline", "Manual", 38),
            ("VoltEra", "Spark", "Blue", "Compact", "Electric", "Automatic", 42),
            ("Iberia Drive", "Rio", "Silver", "Sedan", "Diesel", "Manual", 48),
            ("NovaVelo", "Orbit", "Black", "SUV", "Hybrid", "Automatic", 105),
            ("Solano Cars", "Mar", "Blue", "Coupe", "Gasoline", "Manual", 95),
        ]

        # CarModel 생성 및 매핑
        created_models = []
        for b_name, m_base, c_name, t_name, f_name, trans_name, price in MODEL_DATA:
            # 모델명 규칙: Civis_Red
            full_model_name = f"{m_base}_{c_name}"
            # 이미지 파일명 규칙: boreal motors_civis_red.jpg (소문자, 공백 유지 혹은 언더바)
            img_filename = f"{b_name}_{full_model_name}.jpg".lower().replace(" ", "_")
            
            # v_type 보정 (Hatchback 등 예외처리)
            v_type_key = t_name if t_name in SEATS_BY_TYPE else "Sedan"
            
            model, _ = CarModel.objects.get_or_create(
                model_name=full_model_name,
                brand=brand_map[b_name],
                defaults={
                    'vehicle_type': vtype_map[v_type_key],
                    'fuel_type': fuel_map[f_name],
                    'transmission': trans_map[trans_name],
                    'seats': SEATS_BY_TYPE[v_type_key],
                    'daily_price': Decimal(price),
                    'image': f"car_models/{img_filename}" # media/car_models/ 경로
                }
            )
            created_models.append((model, c_name))

        # 4. 50개 고정 Car 데이터 (번호판 규칙: 1234 BCD)
        consonants = "BCDFGHJKLMNPQRSTVWXYZ"
        for i in range(50):
            # 30개 모델을 최소 한 번씩 다 쓰고, 나머지 20개는 랜덤
            model_info = created_models[i] if i < 30 else random.choice(created_models)
            model_obj, color_name = model_info
            
            plate = f"{random.randint(1000, 9999)} {''.join(random.choices(consonants, k=3))}"
            Car.objects.get_or_create(
                license_plate=plate,
                defaults={
                    'car_model': model_obj,
                    'color': color_map[color_name], # 모델명 힌트와 일치시킴
                    'mileage': random.randint(500, 90000)
                }
            )
        self.stdout.write(f"✅ 30 Models and 50 Cars seeded with fixed rules.")

        # 5. 100+ 명의 스패니쉬 유저 생성
        first_names = ["Enrique Manuel", "María Josefa", "Juan Carlos", "Lucía Elena", "José Antonio", "Ana María", "Francisco Javier", "Dolores", "Ángel", "Pilar"]
        last_names_1 = ["López", "García", "Rodríguez", "Sánchez", "Fernández", "González", "Martínez", "Ruiz"]
        last_names_2 = ["Pérez", "Gómez", "Jiménez", "Díaz", "Álvarez", "Moreno", "Vega", "Serrano"]
        
        user_objs = []
        for i in range(110):
            email = f"user{i+1}@example.com"
            # 나이대 분포 (Young, Standard, Senior)
            birth_year = random.choice([random.randint(1950, 1960), random.randint(1975, 1995), random.randint(2000, 2007)])
            
            user, created = AppUser.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': random.choice(first_names),
                    'last_name': f"{random.choice(last_names_1)} {random.choice(last_names_2)}",
                    'birth_date': date(birth_year, random.randint(1,12), random.randint(1,28)),
                    'license_number': f"{random.randint(10000000, 99999999)}{random.choice('TRWAGMYFPDXBNJZSTQVHLCKE')}"
                }
            )
            if created:
                user.set_password("Pass1234!")
                user.save()
            user_objs.append(user)
        self.stdout.write(f"✅ 110 Spanish users seeded.")

        # 6. 200+ 개의 예약 (유저당 과거 1, 미래 1 보장)
        today = date.today()
        cars = list(Car.objects.all())
        res_count = 0
        
        for user in user_objs:
            # 과거 예약 1개
            past_start = today - timedelta(days=random.randint(30, 365))
            # 미래 예약 1개
            future_start = today + timedelta(days=random.randint(10, 100))
            
            for start_dt in [past_start, future_start]:
                car = random.choice(cars)
                end_dt = start_dt + timedelta(days=random.randint(1, 7))
                try:
                    res = Reservation(user=user, car=car, start_date=start_dt, end_date=end_dt)
                    res.save() # 비즈니스 로직 실행
                    res_count += 1
                except Exception:
                    continue # 날짜 중복 시 건너뜀

        self.stdout.write(self.style.SUCCESS(f"🚀 Final Total: 30 Models, 50 Cars, 110 Users, {res_count} Reservations."))