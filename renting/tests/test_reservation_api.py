from rest_framework import status
from rest_framework.test import APITransactionTestCase
from django.urls import reverse
from datetime import date

from renting.models import (
    AppUser, Brand, VehicleType, FuelType, Transmission,
    CarModel, Color, Car, Reservation
)


class ReservationAPITestCase(APITransactionTestCase):

    def setUp(self):
        # ---------- User ----------
        self.user = AppUser.objects.create(
            first_name="Carlos",
            last_name="García",
            email="carlos@test.com",
            birth_date="1990-05-10",
            license_number="LIC-001",
        )
        self.user.set_password("test1234")
        self.user.save()

        # ---------- Lookup tables ----------
        self.brand = Brand.objects.create(name="Toyota")
        self.vehicle_type = VehicleType.objects.create(name="Sedan")
        self.fuel_type = FuelType.objects.create(name="Gasoline")
        self.transmission = Transmission.objects.create(name="Automatic")
        self.color = Color.objects.create(name="White")

        # ---------- Car model ----------
        self.car_model = CarModel.objects.create(
            model_name="Corolla",
            brand=self.brand,
            vehicle_type=self.vehicle_type,
            fuel_type=self.fuel_type,
            transmission=self.transmission,
            seats=5,
            daily_price=50.00
        )

        # ---------- Car ----------
        self.car = Car.objects.create(
            car_model=self.car_model,
            license_plate="TEST-123",
            color=self.color,
            mileage=20000
        )

        # ---------- Reservation ----------
        self.reservation = Reservation.objects.create(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 5),
            coverage="Standard",
            rate=1.0,
            total_price=200.00,
            user=self.user,
            car=self.car
        )

        self.list_url = "/api/reservations/"
        self.detail_url = f"/api/reservations/{self.reservation.id}/"

    # ------------------------------------------------------------------
    # TESTS
    # ------------------------------------------------------------------

    def test_create_reservation_valid(self):
        payload = {
            "start_date": "2026-03-01",
            "end_date": "2026-03-03",
            "coverage": "Standard",
            "rate": 1.0,
            "total_price": 150.00,
            "user": self.user.id,
            "car": self.car.id,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 2)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["car"], self.car.id)

    def test_create_reservation_invalid_relationship(self):
        payload = {
            "start_date": "2026-04-01",
            "end_date": "2026-04-03",
            "coverage": "Standard",
            "rate": 1.0,
            "total_price": 150.00,
            "user": 9999,   # ❌ user inexistente
            "car": self.car.id,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reservations(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_reservation(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.reservation.id)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["car"], self.car.id)

    def test_update_reservation(self):
        payload = {
            "start_date": "2026-02-02",
            "end_date": "2026-02-06",
            "coverage": "Premium",
            "rate": 1.2,
            "total_price": 240.00,
            "user": self.user.id,
            "car": self.car.id,
        }

        response = self.client.put(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.coverage, "Premium")

    def test_delete_reservation(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reservation.objects.count(), 0)