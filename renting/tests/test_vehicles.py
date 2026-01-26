"""
Issue #53: Vehicle Management Tests
Tests: CarModels, Cars, and lookup tables access
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from renting.models import AppUser, Brand, VehicleType, FuelType, Color, Transmission, CarModel, Car
from decimal import Decimal


class VehicleManagementTestCase(APITestCase):
    """Test vehicle-related endpoints"""
    
    def setUp(self):
        """Create test data"""
        # Create users
        self.normal_user = AppUser.objects.create_user(
            email='normal@example.com',
            first_name='Normal',
            last_name='User',
            password='Pass123!'
        )
        
        self.staff_user = AppUser.objects.create_user(
            email='staff@example.com',
            first_name='Staff',
            last_name='User',
            password='Pass123!',
            is_staff=True
        )
        
        # Get tokens
        login_url = reverse('token_obtain_pair')
        
        response_normal = self.client.post(login_url, {
            'username': 'normal@example.com',  # ← CAMBIADO: 'email' → 'username'
            'password': 'Pass123!'
        }, format='json')
        self.token_normal = response_normal.data['access']
        
        response_staff = self.client.post(login_url, {
            'username': 'staff@example.com',  # ← CAMBIADO: 'email' → 'username'
            'password': 'Pass123!'
        }, format='json')
        self.token_staff = response_staff.data['access']
        
        # Create lookup data
        self.brand = Brand.objects.create(name='Toyota')
        self.vtype = VehicleType.objects.create(name='SUV')
        self.ftype = FuelType.objects.create(name='Hybrid')
        self.color = Color.objects.create(name='Blue')
        self.trans = Transmission.objects.create(name='Automatic')
        
        # Create car model
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            model_name='RAV4',
            vehicle_type=self.vtype,
            fuel_type=self.ftype,
            transmission=self.trans,
            seats=5,
            daily_price=Decimal('75.00')
        )
        
        # Create car
        self.car = Car.objects.create(
            car_model=self.car_model,
            license_plate='XYZ-789',
            color=self.color,
            mileage=5000
        )
    
    def test_01_list_cars_authenticated(self):
        """Test authenticated user can list cars"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_normal}')
        cars_url = reverse('car-list')
        
        response = self.client.get(cars_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
    
    def test_02_normal_user_cannot_create_car(self):
        """Test normal user cannot create car (Issue #86)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_normal}')
        cars_url = reverse('car-list')
        
        car_data = {
            'car_model': self.car_model.id,
            'license_plate': 'NEW-123',
            'color': self.color.id,
            'mileage': 0
        }
        
        response = self.client.post(cars_url, car_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_03_staff_can_create_car(self):
        """Test staff can create car"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_staff}')
        cars_url = reverse('car-list')
        
        car_data = {
            'car_model': self.car_model.id,
            'license_plate': 'STAFF-001',
            'color': self.color.id,
            'mileage': 0
        }
        
        response = self.client.post(cars_url, car_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_04_create_car_negative_mileage_fails(self):
        """Test creating car with negative mileage fails (Issue #86)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_staff}')
        cars_url = reverse('car-list')
        
        car_data = {
            'car_model': self.car_model.id,
            'license_plate': 'NEG-001',
            'color': self.color.id,
            'mileage': -100  # Invalid
        }
        
        response = self.client.post(cars_url, car_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_05_list_brands_authenticated(self):
        """Test authenticated user can list brands"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_normal}')
        brands_url = reverse('brand-list')
        
        response = self.client.get(brands_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
    
    def test_06_list_vehicle_types_authenticated(self):
        """Test authenticated user can list vehicle types"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_normal}')
        vtype_url = reverse('vehicletype-list')
        
        response = self.client.get(vtype_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_07_create_carmodel_negative_seats_fails(self):
        """Test creating car model with negative seats fails (Issue #86)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_staff}')
        carmodel_url = reverse('carmodel-list')
        
        carmodel_data = {
            'brand': self.brand.id,
            'model_name': 'Invalid Model',
            'seats': -5,  # Invalid
            'daily_price': '50.00'
        }
        
        response = self.client.post(carmodel_url, carmodel_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_08_create_carmodel_zero_price_fails(self):
        """Test creating car model with zero price fails (Issue #86)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_staff}')
        carmodel_url = reverse('carmodel-list')
        
        carmodel_data = {
            'brand': self.brand.id,
            'model_name': 'Zero Price Model',
            'seats': 5,
            'daily_price': '0.00'  # Invalid
        }
        
        response = self.client.post(carmodel_url, carmodel_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)