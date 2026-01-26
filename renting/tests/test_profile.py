"""
Issue #53 & #62: Profile Management Tests
Tests: GET/PUT/PATCH/DELETE /api/profile/me/
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from renting.models import AppUser


class ProfileManagementTestCase(APITestCase):
    """Test profile endpoints (Issue #62)"""
    
    def setUp(self):
        """Create a test user and get JWT token"""
        self.user = AppUser.objects.create_user(
            email='profile@example.com',
            first_name='Profile',
            last_name='User',
            password='TestPass123!',
            birth_date='1995-05-15',
            license_number='LIC123456'
        )
        
        # Get JWT token
        login_url = reverse('token_obtain_pair')
        login_response = self.client.post(login_url, {
            'username': 'profile@example.com',  # ← CAMBIADO: 'email' → 'username'
            'password': 'TestPass123!'
        }, format='json')
        
        self.access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.profile_url = reverse('profile-me')
        self.change_password_url = reverse('profile-change-password')
    
    def test_01_get_own_profile(self):
        """Test viewing own profile"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')
        self.assertNotIn('password', response.data)
    
    def test_02_update_profile_with_password(self):
        """Test updating profile with password confirmation (Issue #62)"""
        update_data = {
            'current_password': 'TestPass123!',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
    
    def test_03_update_profile_without_password_fails(self):
        """Test updating profile without password fails (Issue #62)"""
        update_data = {
            'first_name': 'Updated'
            # Missing current_password
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_04_update_profile_wrong_password(self):
        """Test updating profile with wrong password fails"""
        update_data = {
            'current_password': 'WrongPassword!',
            'first_name': 'Updated'
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_05_change_password_success(self):
        """Test changing password successfully"""
        change_data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewSecurePass123!'
        }
        
        response = self.client.post(self.change_password_url, change_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify can login with new password
        login_url = reverse('token_obtain_pair')
        login_response = self.client.post(login_url, {
            'username': 'profile@example.com',  # ← CAMBIADO: 'email' → 'username'
            'password': 'NewSecurePass123!'
        }, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
    def test_06_change_password_too_short(self):
        """Test changing password with too short password fails"""
        change_data = {
            'old_password': 'TestPass123!',
            'new_password': 'Short1'  # Less than 8 chars
        }
        
        response = self.client.post(self.change_password_url, change_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_07_change_password_wrong_old_password(self):
        """Test changing password with wrong old password fails"""
        change_data = {
            'old_password': 'WrongOldPass!',
            'new_password': 'NewSecurePass123!'
        }
        
        response = self.client.post(self.change_password_url, change_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_08_delete_account_with_password(self):
        """Test deleting account with password confirmation"""
        delete_data = {
            'password': 'TestPass123!'
        }
        
        response = self.client.delete(self.profile_url, delete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify user is deleted
        self.assertFalse(AppUser.objects.filter(email='profile@example.com').exists())
    
    def test_09_delete_account_without_password_fails(self):
        """Test deleting account without password fails"""
        response = self.client.delete(self.profile_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_10_profile_endpoints_without_auth_return_401(self):
        """Test all profile endpoints require authentication"""
        # Remove authentication
        self.client.credentials()
        
        # GET
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # PATCH
        response = self.client.patch(self.profile_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # DELETE
        response = self.client.delete(self.profile_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Change password
        response = self.client.post(self.change_password_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)