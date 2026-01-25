import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from django.utils import timezone
from .filters import CarFilter, ReservationFilter
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsReservationOwnerOrStaff, IsStaffPermission, IsStaffOrReadOnlyPermission 
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)

logger = logging.getLogger(__name__)

def user_list(request):
    logger.info("User list page accessed")
    users = AppUser.objects.all()
    return render(request, 'renting/users/list.html', {'users': users})

def home(request):
    return render(request, 'renting/home.html')

def car_list(request):
    return render(request, 'renting/cars/list.html')

def reservation_list(request):
    return render(request, 'renting/reservations/list.html')


# API Views con JWT
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    AppUserSerializer, VehicleTypeSerializer, BrandSerializer,
    FuelTypeSerializer, ColorSerializer, TransmissionSerializer,
    CarModelSerializer, CarSerializer, ReservationSerializer, AppUserSignupSerializer
)


# Permiso personalizado para el ViewSet de usuarios
class IsOwnerOrStaffOrCreateOnly(BasePermission):
    """
    - Cualquiera puede registrarse (create)
    - Usuarios autenticados pueden acceder a /me/
    - Solo staff puede list/retrieve/update/delete otros usuarios
    """
    
    def has_permission(self, request, view):
        # Permitir registro sin autenticación
        if view.action == 'create':
            return True
        
        # Todas las acciones personalizadas (me, update_me, etc.) requieren autenticación
        if view.action in ['me', 'update_me', 'delete_me', 'change_password']:
            # CRÍTICO: Verificar que el usuario está autenticado Y activo
            return (
                request.user 
                and request.user.is_authenticated 
                and getattr(request.user, 'is_active', True)
            )
        
        # list, retrieve, update, destroy requieren staff
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.is_staff 
            and getattr(request.user, 'is_active', True)
        )
    
    def has_object_permission(self, request, view, obj):
        # Staff puede todo
        if request.user.is_staff:
            return True
        
        # Usuarios solo pueden modificar su propia cuenta
        return obj == request.user


class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    permission_classes = [IsOwnerOrStaffOrCreateOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return AppUserSignupSerializer
        return AppUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"User created: {user.email}")

    def perform_destroy(self, instance):
        logger.info(f"User deleted: {instance.email}")
        instance.delete()

    # ==========================================
    # ENDPOINTS /me/
    # ==========================================
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        GET /api/users/me/
        Obtiene información del usuario actual
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], url_path='me')
    def update_me(self, request):
        """
        PUT/PATCH /api/users/me/
        Actualiza información del usuario actual
        
        IMPORTANTE: Se requiere current_password para cambios de seguridad
        """
        # Validar current_password si está presente
        current_password = request.data.get('current_password')
        
        # Si intenta cambiar email o campos sensibles, requerir contraseña
        sensitive_fields = {'email', 'password'}
        is_sensitive_update = any(field in request.data for field in sensitive_fields)
        
        if is_sensitive_update and not current_password:
            return Response(
                {"error": "Se requiere current_password para cambios sensibles"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if current_password:
            if not request.user.check_password(current_password):
                return Response(
                    {"error": "Contraseña actual incorrecta"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Crear una copia de los datos sin current_password
        data = request.data.copy()
        if 'current_password' in data:
            data.pop('current_password')
        
        serializer = self.get_serializer(
            request.user, 
            data=data, 
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"User updated: {request.user.email}")
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='me')
    def delete_me(self, request):
        """
        DELETE /api/users/me/
        Elimina la cuenta del usuario actual
        
        Body: { "password": "..." }
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
        
        user = request.user
        logger.info(f"User self-deleted: {user.email}")
        user.delete()
        return Response(
            {"detail": "Cuenta eliminada exitosamente"}, 
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        """
        POST /api/users/me/change-password/
        Cambia la contraseña del usuario actual
        
        Body: {
            "old_password": "...",
            "new_password": "..."
        }
        """
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
        
        # Validación básica de nueva contraseña
        if len(new_password) < 8:
            return Response(
                {"error": "La nueva contraseña debe tener al menos 8 caracteres"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        logger.info(f"Password changed for user: {request.user.email}")
        
        return Response({"detail": "Contraseña actualizada exitosamente"})


class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated]

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]

class FuelTypeViewSet(viewsets.ModelViewSet):
    queryset = FuelType.objects.all()
    serializer_class = FuelTypeSerializer
    permission_classes = [IsAuthenticated] 

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]

class TransmissionViewSet(viewsets.ModelViewSet):
    queryset = Transmission.objects.all()
    serializer_class = TransmissionSerializer
    permission_classes = [IsAuthenticated]

class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.select_related(
        'brand', 'vehicle_type', 'fuel_type', 'transmission'
    ).all()
    serializer_class = CarModelSerializer
    permission_classes = [IsAuthenticated]

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.select_related('car_model', 'car_model__brand', 'color').all()
    serializer_class = CarSerializer
    permission_classes = [IsStaffOrReadOnlyPermission] 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CarFilter
    search_fields = ['license_plate', 'car_model__model_name']
    ordering_fields = ['license_plate']

    def perform_create(self, serializer):
        car = serializer.save()
        logger.info(f"Car created: {car.license_plate}")

    def perform_destroy(self, instance):
        logger.info(f"Car deleted: {instance.license_plate}")
        instance.delete()

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related(
        'user', 'car', 'car__car_model', 'car__car_model__brand'
    ).all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsReservationOwnerOrStaff]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReservationFilter
    search_fields = ['user__email', 'car__license_plate']
    ordering_fields = ['start_date', 'end_date']

    def get_queryset(self):
        """
        Issue #24: Non-staff solo ve sus reservas
        """
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        reservation = serializer.save(user=self.request.user)
        logger.info(
            f"Reservation created: user={reservation.user.email}, car={reservation.car.license_plate}"
        )

    def perform_destroy(self, instance):
        logger.info(
            f"Reservation deleted: id={instance.id}, user={instance.user.email}"
        )
        instance.delete()

    def get_permissions(self):
        """
        #61 Explicit: OwnerOrStaff para list/retrieve
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsReservationOwnerOrStaff()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='my')
    def my_reservations(self, request):
        """#62 GET /api/reservations/my/?status=upcoming|past"""
        queryset = self.filter_queryset(self.get_queryset())
        
        status_param = request.query_params.get('status')
        now = timezone.now().date()
        if status_param == 'upcoming':
            queryset = queryset.filter(start_date__gte=now)
        elif status_param == 'past':
            queryset = queryset.filter(end_date__lt=now)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='delete-with-password')
    def delete_with_password(self, request, pk=None):
        """#62 DELETE /api/reservations/{id}/delete-with-password/"""
        reservation = self.get_object()
        
        # Past reservations read-only
        if reservation.end_date < timezone.now().date():
            return Response(
                {"detail": "Past reservations cannot be deleted"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Password confirmation
        password = request.data.get('password')
        if not request.user.check_password(password):
            return Response(
                {"detail": "Invalid password"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(reservation)
        return Response(
            {"message": "Reservation deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )


def login_view(request):
    return render(request, 'renting/login.html')

def logout_view(request):
    return redirect('login')

def register_view(request):
    return render(request, 'renting/register.html')

def reservation_create(request):
    return render(request, 'renting/reservations/create.html')