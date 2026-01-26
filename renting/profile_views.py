from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import AppUserSerializer
import logging


logger = logging.getLogger(__name__)


class ProfileView(APIView):
    """
    Profile management endpoint for authenticated users.
    GET/PUT/PATCH/DELETE /api/profile/me/
    
    All modifications (PUT/PATCH/DELETE) require current password confirmation (Issue #62).
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retrieve current user's profile (no password required)"""
        serializer = AppUserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update full profile (requires current_password)"""
        return self._update(request, partial=False)
    
    def patch(self, request):
        """Update partial profile (requires current_password)"""
        return self._update(request, partial=True)
    
    def _update(self, request, partial):
        """Common update logic with password verification (Issue #62)"""
        current_password = request.data.get('current_password')
        
        # Validate current password is provided
        if not current_password:
            return Response(
                {"error": "current_password is required to update profile"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify current password is correct
        if not request.user.check_password(current_password):
            return Response(
                {"error": "Invalid current password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove current_password from data for serialization
        data = request.data.copy()
        data.pop('current_password')
        
        # Validate and save
        serializer = AppUserSerializer(
            request.user, 
            data=data, 
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Profile updated: {request.user.email} ({'partial' if partial else 'full'})")
        return Response(serializer.data)
    
    def delete(self, request):
        """Delete user account (requires password confirmation)"""
        password = request.data.get('password')
        
        if not password:
            return Response(
                {"error": "Password is required to delete account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(password):
            return Response(
                {"error": "Invalid password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_email = request.user.email
        request.user.delete()
        logger.info(f"User self-deleted: {user_email}")
        return Response(
            {"detail": "Account successfully deleted"}, 
            status=status.HTTP_204_NO_CONTENT
        )


class ChangePasswordView(APIView):
    """
    Change current user password.
    POST /api/profile/me/change-password/
    
    Requires minimum 8 characters (Issue #62).
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {"error": "old_password and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {"error": "Invalid current password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate minimum 8 characters
        if len(new_password) < 8:
            return Response(
                {"error": "New password must be at least 8 characters long"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        logger.info(f"Password changed for user: {request.user.email}")
        
        return Response({"detail": "Password updated successfully"})
