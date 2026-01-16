from rest_framework.test import APITransactionTestCase
from rest_framework import status
from django.urls import reverse

from renting.models import (
    Brand, VehicleType, FuelType, Transmission, Color,
    CarModel, Car
)


class VehicleAPITestCase(APITransactionTestCase):

    def setUp(self):
        # --- Lookup tables ---
        self.brand = Brand.objects.create(name="Toyota")
        self.vehicle_type = VehicleType.objects.create(name="Sedan")
        self.fuel_type = FuelType.objects.create(name="Gasoline")
        self.transmission = Transmission.objects.create(name="Automatic")
        self.color = Color.objects.create(name="White")

        # --- Car model ---
        self.car_model = CarModel.objects.create(
            model_name="Corolla",
            brand=self.brand,
            vehicle_type=self.vehicle_type,
            fuel_type=self.fuel_type,
            transmission=self.transmission,
            seats=5,
            daily_price=50.00
        )

        # --- Car ---
        self.car = Car.objects.create(
            car_model=self.car_model,
            license_plate="TEST-123",
            color=self.color,
            mileage=20000
        )

        self.car_list_url = reverse("car-list")
        self.car_detail_url = reverse("car-detail", args=[self.car.id])

    # -------------------------
    # CREATE
    # -------------------------
    def test_create_car(self):
        payload = {
            "car_model": self.car_model.id,
            "license_plate": "NEW-456",
            "color": self.color.id,
            "mileage": 1000
        }

        response = self.client.post(self.car_list_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Car.objects.count(), 2)

    # -------------------------
    # READ (LIST)
    # -------------------------
    def test_list_cars(self):
        response = self.client.get(self.car_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # -------------------------
    # READ (DETAIL)
    # -------------------------
    def test_retrieve_car(self):
        response = self.client.get(self.car_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["license_plate"], "TEST-123")

    # -------------------------
    # UPDATE
    # -------------------------
    def test_update_car(self):
        payload = {
            "car_model": self.car_model.id,
            "license_plate": "UPDATED-999",
            "color": self.color.id,
            "mileage": 30000
        }

        response = self.client.put(self.car_detail_url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertEqual(self.car.license_plate, "UPDATED-999")

    # -------------------------
    # DELETE
    # -------------------------
    def test_delete_car(self):
        response = self.client.delete(self.car_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Car.objects.count(), 0)