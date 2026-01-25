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
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    AppUserSerializer, VehicleTypeSerializer, BrandSerializer,
    FuelTypeSerializer, ColorSerializer, TransmissionSerializer,
    CarModelSerializer, CarSerializer, ReservationSerializer, AppUserSignupSerializer
)

class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer

    def get_permissions(self):
        """
        #61 Staff + #62 My Page - Permissions por acción
        """
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['me', 'update_me', 'change_password', 'delete_me']:
            return [IsAuthenticated()]
        return [IsStaffPermission()]

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"User created: {user.email}")

    def perform_destroy(self, instance):
        logger.info(f"User deleted: {instance.email}")
        instance.delete()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """#62 GET /api/users/me/ → Perfil actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return AppUserSignupSerializer
        return AppUserSerializer

    @action(detail=False, methods=['put'], url_path='me')
    def update_me(self, request):
        """#62 PUT /api/users/me/ → Update perfil + password"""
        password = request.data.pop('current_password', None)
        if not request.user.check_password(password):
            return Response({"detail": "Invalid current password"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        """#62 POST /api/users/me/change-password/"""
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not request.user.check_password(current_password):
            return Response({"detail": "Invalid current password"}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({"detail": "New password too short (min 8 chars)"}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "Password changed successfully"})

    @action(detail=False, methods=['delete'], url_path='me')
    def delete_me(self, request):
        """#62 DELETE /api/users/me/ → Delete account + password"""
        password = request.data.get('password')
        if not request.user.check_password(password):
            return Response({"detail": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = [IsAuthenticated, IsReservationOwnerOrStaff]  # ← CAMBIAR

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
        
        status = request.query_params.get('status')
        now = timezone.now().date()
        if status == 'upcoming':
            queryset = queryset.filter(start_date__gte=now)
        elif status == 'past':
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
            return Response({"detail": "Past reservations cannot be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Password confirmation
        password = request.data.get('password')
        if not request.user.check_password(password):
            return Response({"detail": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(reservation)
        return Response({"message": "Reservation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

def login_view(request):
    return render(request, 'renting/login.html')

def logout_view(request):
    # 세션 기반 로그아웃 대신 프론트엔드에서 처리하도록 유도 (나중에 삭제 가능)
    return redirect('login')

def register_view(request):
    return render(request, 'renting/register.html')

def reservation_create(request):
    return render(request, 'renting/reservations/create.html')

# temp change to trigger git