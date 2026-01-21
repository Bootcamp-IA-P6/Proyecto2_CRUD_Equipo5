# renting/management/commands/seed_data.py
import random
from django.core.management.base import BaseCommand
from renting.models import (
    AppUser, Brand, CarModel, Car, VehicleType, 
    FuelType, Color, Transmission, Reservation
)
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Robust seed with variety for Color, Type, and Fuel (MySQL Compatible)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🧹 Starting robust database seed (No global transaction)..."))
        
        # 1. 기초 테이블 생성 (Lookup Tables)
        # atomic 블록 없이 각각 독립적으로 생성합니다.
        brands = ["Toyota", "BMW", "Tesla", "Hyundai", "Ford", "Mercedes", "Audi"]
        brand_objs = [Brand.objects.get_or_create(name=name)[0] for name in brands]

        colors = ["Silver", "Black", "White", "Deep Blue", "Red"]
        color_objs = [Color.objects.get_or_create(name=name)[0] for name in colors]

        v_types = ["SUV", "Sedan", "Hatchback", "Coupe"]
        v_type_objs = [VehicleType.objects.get_or_create(name=name)[0] for name in v_types]

        fuels = ["Gasoline", "Diesel", "Electric", "Hybrid"]
        fuel_objs = [FuelType.objects.get_or_create(name=name)[0] for name in fuels]

        transmissions = ["Automatic", "Manual"]
        trans_objs = [Transmission.objects.get_or_create(name=name)[0] for name in transmissions]

        self.stdout.write("✅ Lookup tables (Color, Type, Fuel) seeded.")

        # 2. CarModel 생성 (12가지 모델 조합)
        model_names = ["Corolla", "X5", "Model 3", "Tucson", "Explorer", "Civic", "A4", "Golf", "Mustang", "C-Class"]
        model_objs = []
        for i in range(12):
            model, _ = CarModel.objects.get_or_create(
                model_name=f"{random.choice(model_names)} v{i}",
                brand=random.choice(brand_objs),
                defaults={
                    'vehicle_type': random.choice(v_type_objs),
                    'fuel_type': random.choice(fuel_objs),
                    'transmission': random.choice(trans_objs),
                    'seats': random.choice([2, 4, 5, 7]),
                    'daily_price': Decimal(random.randint(45, 120))
                }
            )
            model_objs.append(model)
        self.stdout.write(f"✅ {len(model_objs)} Car Models created.")

        # 3. Physical Car 생성 (15대)
        car_objs = []
        for i in range(15):
            car, _ = Car.objects.get_or_create(
                license_plate=f"{random.randint(1000, 9999)}-{random.choice(['ABC', 'XYZ', 'JWT'])}",
                defaults={
                    'car_model': random.choice(model_objs),
                    'color': random.choice(color_objs), # 🎨 다양한 컬러 적용
                    'mileage': random.randint(1000, 60000)
                }
            )
            car_objs.append(car)
        self.stdout.write("✅ 15 Physical Cars seeded.")

        # 4. AppUser 생성 (15명)
        f_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph"]
        l_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
        
        user_objs = []
        for i in range(15):
            email = f"user{i+1}@example.com"
            birth_year = random.choice([1955, 1970, 1985, 1995, 2004, 2006])
            
            user, created = AppUser.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f_names[i],
                    'last_name': l_names[i],
                    'birth_date': date(birth_year, random.randint(1,12), random.randint(1,28)),
                    'license_number': f"LIC-{random.randint(10000, 99999)}"
                }
            )
            if created:
                user.set_password("pass1234")
                user.save()
            user_objs.append(user)
        self.stdout.write("✅ 15 Users with hashed passwords seeded.")

        # 5. Reservation 생성 (25개)
        created_res_count = 0
        for i in range(25):
            user = random.choice(user_objs)
            car = random.choice(car_objs)
            start = date(2026, 2, 1) + timedelta(days=random.randint(1, 45))
            end = start + timedelta(days=random.randint(1, 5))
            
            # Reservation은 중복 검사가 복잡하므로 간단하게 create로 생성
            try:
                res = Reservation(
                    user=user,
                    car=car,
                    start_date=start,
                    end_date=end
                )
                res.save() # 여기서 비즈니스 로직(나이별 자동 가격) 실행됨
                created_res_count += 1
            except Exception as e:
                # 겹치는 예약 등 에러 발생 시 건너뛰고 계속 진행
                continue

        self.stdout.write(self.style.SUCCESS(f"🚀 Successfully seeded all 9 tables! (Reservations: {created_res_count})"))