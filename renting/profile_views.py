from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import AppUserSerializer
import logging

logger = logging.getLogger(__name__)


class ProfileView(APIView):
    """
    Endpoint para gestionar el perfil del usuario actual
    GET/PUT/PATCH/DELETE /api/profile/me/
    
    IMPORTANTE: Todas las modificaciones (PUT/PATCH/DELETE) requieren 
    confirmación de contraseña según criterios de aceptación del Issue #62
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/profile/me/ 
        Ver perfil propio (no requiere contraseña)
        """
        serializer = AppUserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """
        PUT /api/profile/me/ 
        Actualizar perfil completo (REQUIERE current_password)
        """
        return self._update(request, partial=False)
    
    def patch(self, request):
        """
        PATCH /api/profile/me/ 
        Actualizar perfil parcial (REQUIERE current_password)
        """
        return self._update(request, partial=True)
    
    def _update(self, request, partial):
        """
        Lógica común de actualización
        Issue #62: Todas las modificaciones requieren current_password
        """
        current_password = request.data.get('current_password')
        
        # Validar que se proporcione la contraseña actual
        if not current_password:
            return Response(
                {"error": "Se requiere current_password para modificar el perfil"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que la contraseña sea correcta
        if not request.user.check_password(current_password):
            return Response(
                {"error": "Contraseña actual incorrecta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear una copia de los datos sin current_password
        data = request.data.copy()
        data.pop('current_password')
        
        # Validar y guardar
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
        """
        DELETE /api/profile/me/ 
        Eliminar cuenta propia (REQUIERE password)
        """
        password = request.data.get('password')
        
        if not password:
            return Response(
                {"error": "Se requiere password para eliminar la cuenta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(password):
            return Response(
                {"error": "Contraseña incorrecta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_email = request.user.email
        request.user.delete()
        logger.info(f"User self-deleted: {user_email}")
        return Response(
            {"detail": "Cuenta eliminada exitosamente"}, 
            status=status.HTTP_204_NO_CONTENT
        )


class ChangePasswordView(APIView):
    """
    POST /api/profile/me/change-password/
    Cambiar contraseña del usuario actual
    
    Validación: Mínimo 8 caracteres (según Issue #62)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {"error": "Se requieren old_password y new_password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {"error": "Contraseña actual incorrecta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación: mínimo 8 caracteres
        if len(new_password) < 8:
            return Response(
                {"error": "La nueva contraseña debe tener al menos 8 caracteres"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        logger.info(f"Password changed for user: {request.user.email}")
        
        return Response({"detail": "Contraseña actualizada exitosamente"})