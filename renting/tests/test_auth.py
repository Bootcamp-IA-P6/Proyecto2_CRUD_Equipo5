"""
Issue #53: Authentication & JWT Flow Tests
Tests: Signup → Login → Token Refresh → Logout
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from renting.models import AppUser


class AuthenticationFlowTestCase(APITestCase):
    """Test complete authentication flow with JWT"""
    
    def setUp(self):
        """Setup test data"""
        self.signup_url = reverse('appuser-list')
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        
        self.valid_user_data = {
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'SecurePass123!',
            'birth_date': '1990-01-01',
            'license_number': 'TEST123456'
        }
    
    def test_01_signup_success(self):
        """Test successful user registration"""
        response = self.client.post(self.signup_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], self.valid_user_data['email'])
        self.assertNotIn('password', response.data)
        
        # Verify user exists in database
        self.assertTrue(AppUser.objects.filter(email=self.valid_user_data['email']).exists())
    
    def test_02_signup_duplicate_email(self):
        """Test signup with duplicate email fails"""
        self.client.post(self.signup_url, self.valid_user_data, format='json')
        
        response = self.client.post(self.signup_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_03_signup_missing_required_fields(self):
        """Test signup with missing required fields"""
        invalid_data = {
            'email': 'incomplete@example.com'
        }
        
        response = self.client.post(self.signup_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_04_login_success(self):
        """Test successful login returns JWT tokens"""
        self.client.post(self.signup_url, self.valid_user_data, format='json')
        
        login_data = {
            'username': self.valid_user_data['email'],  # ← CAMBIADO: 'email' → 'username'
            'password': self.valid_user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        self.assertTrue(len(response.data['access']) > 0)
        self.assertTrue(len(response.data['refresh']) > 0)
    
    def test_05_login_invalid_credentials(self):
        """Test login with wrong password fails"""
        self.client.post(self.signup_url, self.valid_user_data, format='json')
        
        login_data = {
            'username': self.valid_user_data['email'],  # ← CAMBIADO: 'email' → 'username'
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_06_login_nonexistent_user(self):
        """Test login with non-existent user fails"""
        login_data = {
            'username': 'nonexistent@example.com',  # ← CAMBIADO: 'email' → 'username'
            'password': 'SomePassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_07_token_refresh_success(self):
        """Test token refresh with valid refresh token"""
        self.client.post(self.signup_url, self.valid_user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': self.valid_user_data['email'],  # ← CAMBIADO: 'email' → 'username'
            'password': self.valid_user_data['password']
        }, format='json')
        
        refresh_token = login_response.data['refresh']
        
        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_08_token_refresh_invalid_token(self):
        """Test token refresh with invalid refresh token"""
        response = self.client.post(self.refresh_url, {'refresh': 'invalid_token'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_09_authenticated_request_without_token(self):
        """Test accessing protected endpoint without token returns 401"""
        profile_url = reverse('profile-me')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_10_authenticated_request_with_token(self):
        """Test accessing protected endpoint with valid token succeeds"""
        self.client.post(self.signup_url, self.valid_user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'username': self.valid_user_data['email'],  # ← CAMBIADO: 'email' → 'username'
            'password': self.valid_user_data['password']
        }, format='json')
        
        access_token = login_response.data['access']
        
        profile_url = reverse('profile-me')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.valid_user_data['email'])