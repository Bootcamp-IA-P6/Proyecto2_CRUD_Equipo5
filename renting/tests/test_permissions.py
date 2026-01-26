"""
Issue #53: Permission & Authorization Tests
Tests: Staff-only operations, user isolation, edge cases
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from renting.models import AppUser


class PermissionTestCase(APITestCase):
    """Test authorization and permission edge cases"""
    
    def setUp(self):
        """Create test users"""
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
        
        # Check if login was successful
        if 'access' in response_normal.data:
            self.token_normal = response_normal.data['access']
        else:
            self.fail(f"Login failed for normal user: {response_normal.data}")
        
        response_staff = self.client.post(login_url, {
            'username': 'staff@example.com',  # ← CAMBIADO: 'email' → 'username'
            'password': 'Pass123!'
        }, format='json')
        
        if 'access' in response_staff.data:
            self.token_staff = response_staff.data['access']
        else:
            self.fail(f"Login failed for staff user: {response_staff.data}")
    
    def test_01_normal_user_cannot_list_users(self):
        """Test normal user cannot list all users"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_normal}')
        users_url = reverse('appuser-list')
        
        response = self.client.get(users_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_02_staff_can_list_users(self):
        """Test staff can list all users"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_staff}')
        users_url = reverse('appuser-list')
        
        response = self.client.get(users_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_03_normal_user_cannot_view_other_user_detail(self):
        """Test normal user cannot view other user's details"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_normal}')
        user_detail_url = reverse('appuser-detail', kwargs={'pk': self.staff_user.id})
        
        response = self.client.get(user_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_04_expired_token_returns_401(self):
        """Test expired/invalid token returns 401"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        profile_url = reverse('profile-me')
        
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_05_malformed_auth_header_returns_401(self):
        """Test malformed auth header returns 401"""
        self.client.credentials(HTTP_AUTHORIZATION='InvalidFormat token')
        profile_url = reverse('profile-me')
        
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)