from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from renting.models import AppUser

class UserAPITests(APITestCase):
    def test_create_user_success(self):
        url = reverse('appuser-list')
        data = {
            "first_name": "Clara",
            "last_name": "Tester",
            "email": "clara@example.com",
            "password": "password123",
            "birth_date": "1990-01-01",
            "license_number": "DNI123"
        }
        response = self.client.post(url, data, format='json')
        
        # Si sigue fallando, esto ahora nos dará más pistas si comentaste lo de exceptions.py
        if response.status_code == 500:
            print(response.content) 
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)