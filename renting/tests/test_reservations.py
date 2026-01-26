"""
Issue #53 & #62: Reservation Management Tests
Tests: CRUD operations, filtering, password-protected deletion
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from renting.models import AppUser, Car, CarModel, Brand, Color, VehicleType, FuelType, Transmission, Reservation
from datetime import date, timedelta
from decimal import Decimal


class ReservationManagementTestCase(APITestCase):
    """Test reservation endpoints"""
    
    def setUp(self):
        """Create test data"""
        # Create users - CAMBIO: usar date() en lugar de strings para evitar el error de calculate_details
        self.user1 = AppUser.objects.create_user(
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='Pass123!',
            birth_date=date(1990, 1, 1)  # ← FIJADO: usar date object
        )
        
        self.user2 = AppUser.objects.create_user(
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='Pass123!',
            birth_date=date(1995, 5, 15)  # ← FIJADO: usar date object
        )
        
        self.staff_user = AppUser.objects.create_user(
            email='staff@example.com',
            first_name='Staff',
            last_name='Member',
            password='Pass123!',
            birth_date=date(1985, 1, 1),  # ← FIJADO: usar date object
            is_staff=True
        )
        
        # Create lookup data
        brand = Brand.objects.create(name='Toyota')
        color = Color.objects.create(name='Red')
        vtype = VehicleType.objects.create(name='Sedan')
        ftype = FuelType.objects.create(name='Gasoline')
        trans = Transmission.objects.create(name='Automatic')
        
        # Create car model and car
        car_model = CarModel.objects.create(
            brand=brand,
            model_name='Camry',
            vehicle_type=vtype,
            fuel_type=ftype,
            transmission=trans,
            seats=5,
            daily_price=Decimal('50.00')
        )
        
        self.car = Car.objects.create(
            car_model=car_model,
            license_plate='ABC-123',
            color=color,
            mileage=10000
        )
        
        # Get JWT tokens
        login_url = reverse('token_obtain_pair')
        
        response1 = self.client.post(login_url, {
            'username': 'user1@example.com',
            'password': 'Pass123!'
        }, format='json')
        self.token_user1 = response1.data['access']
        
        response2 = self.client.post(login_url, {
            'username': 'user2@example.com',
            'password': 'Pass123!'
        }, format='json')
        self.token_user2 = response2.data['access']
        
        response_staff = self.client.post(login_url, {
            'username': 'staff@example.com',
            'password': 'Pass123!'
        }, format='json')
        self.token_staff = response_staff.data['access']
        
        self.reservations_url = reverse('reservation-list')
 
    def test_01_create_reservation_success(self):
        """Test creating a reservation"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        
        reservation_data = {
            'car': self.car.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=3))
        }
        
        response = self.client.post(self.reservations_url, reservation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('total_price', response.data)
        # ← FIJADO: convertir string a Decimal antes de comparar
        total_price = Decimal(response.data['total_price'])
        self.assertTrue(total_price > 0)
 
    def test_02_create_reservation_without_auth_fails(self):
        """Test creating reservation without auth returns 401"""
        reservation_data = {
            'car': self.car.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=3))
        }
        
        response = self.client.post(self.reservations_url, reservation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
 
    def test_03_create_reservation_invalid_dates(self):
        """Test creating reservation with end_date before start_date fails"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        
        reservation_data = {
            'car': self.car.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() - timedelta(days=1))  # Invalid
        }
        
        response = self.client.post(self.reservations_url, reservation_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
 
    def test_04_user_sees_only_own_reservations(self):
        """Test user can only see their own reservations (Issue #62)"""
        # Create reservation for user1
        Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2)
        )
        
        # Create reservation for user2
        Reservation.objects.create(
            user=self.user2,
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        # User1 should only see their own
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        response = self.client.get(self.reservations_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user1.id)
 
    def test_05_staff_sees_all_reservations(self):
        """Test staff can see all reservations"""
        # Create reservations for different users
        Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2)
        )
        
        Reservation.objects.create(
            user=self.user2,
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        # Staff should see all
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_staff}')
        response = self.client.get(self.reservations_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
 
    def test_06_filter_my_reservations_upcoming(self):
        """Test filtering my upcoming reservations (Issue #62)"""
        # Create past reservation
        Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() - timedelta(days=8)
        )
        
        # Create future reservation
        Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        # Filter upcoming
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        my_url = reverse('reservation-my-reservations')
        response = self.client.get(f'{my_url}?status=upcoming')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
 
    def test_07_filter_my_reservations_past(self):
        """Test filtering my past reservations (Issue #62)"""
        # Create past reservation
        Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() - timedelta(days=8)
        )
        
        # Create future reservation
        Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        # Filter past
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        my_url = reverse('reservation-my-reservations')
        response = self.client.get(f'{my_url}?status=past')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
 
    def test_08_delete_future_reservation_with_password(self):
        """Test deleting future reservation with password (Issue #62)"""
        reservation = Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        delete_url = reverse('reservation-delete-with-password', kwargs={'pk': reservation.id})
        
        response = self.client.delete(delete_url, {'password': 'Pass123!'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(id=reservation.id).exists())
 
    def test_09_delete_past_reservation_blocked(self):
        """Test deleting past reservation is blocked (Issue #62)"""
        reservation = Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() - timedelta(days=8)
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        delete_url = reverse('reservation-delete-with-password', kwargs={'pk': reservation.id})
        
        response = self.client.delete(delete_url, {'password': 'Pass123!'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Reservation.objects.filter(id=reservation.id).exists())
 
    def test_10_delete_reservation_wrong_password(self):
        """Test deleting reservation with wrong password fails"""
        reservation = Reservation.objects.create(
            user=self.user1,
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        delete_url = reverse('reservation-delete-with-password', kwargs={'pk': reservation.id})
        
        response = self.client.delete(delete_url, {'password': 'WrongPass!'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Reservation.objects.filter(id=reservation.id).exists())
 
    def test_11_user_cannot_delete_other_users_reservation(self):
        """Test user cannot delete another user's reservation"""
        reservation = Reservation.objects.create(
            user=self.user2,  # Belongs to user2
            car=self.car,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        # User1 tries to delete
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        delete_url = reverse('reservation-delete-with-password', kwargs={'pk': reservation.id})
        
        response = self.client.delete(delete_url, {'password': 'Pass123!'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
