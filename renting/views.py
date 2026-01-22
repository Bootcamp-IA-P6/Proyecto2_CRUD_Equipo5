import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import CarFilter, ReservationFilter
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsReservationOwnerOrStaff 
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
    # permission_classes = [IsAuthenticated]  

    def get_permissions(self):
        """
        Action별로 권한을 다르게 설정합니다.
        - create (회원가입): 누구나 가능 (AllowAny)
        - 나머지: 로그인 필요 (IsAuthenticated)
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # 회원가입 성공 시 로그를 남기는 기존 로직 유지
        user = serializer.save()
        logger.info(f"User created: {user.email}")

    def perform_destroy(self, instance):
        # 삭제 시 로그를 남기는 기존 로직 유지
        logger.info(f"User deleted: {instance.email}")
        instance.delete()

    @action(detail=False, methods=['get'])
    def me(self, request):
        # 현재 로그인한 유저 정보를 반환하는 기존 로직 유지
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return AppUserSignupSerializer  # Strict validation
        return AppUserSerializer  # Normal para list/retrieve


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
    permission_classes = [IsAuthenticated]

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