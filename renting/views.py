import logging
from django.shortcuts import render
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)
from .pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

# Vistas HTML (sin cambios)
def home(request):
    logger.info("Home page accessed")
    return render(request, 'renting/home.html', {
        'total_users': AppUser.objects.count(),
        'total_cars': Car.objects.count(),
        'total_reservations': Reservation.objects.count(),
    })

def user_list(request):
    logger.info("User list page accessed")
    users = AppUser.objects.all()
    return render(request, 'renting/users/list.html', {'users': users})

def car_list(request):
    logger.info("Car list page accessed")
    cars = Car.objects.select_related('car_model', 'car_model__brand').all()
    return render(request, 'renting/cars/list.html', {'cars': cars})

def reservation_list(request):
    logger.info("Reservation list page accessed")
    reservations = Reservation.objects.select_related('user', 'car', 'car__car_model').all()
    return render(request, 'renting/reservations/list.html', {'reservations': reservations})

# API Views con JWT
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    AppUserSerializer, VehicleTypeSerializer, BrandSerializer,
    FuelTypeSerializer, ColorSerializer, TransmissionSerializer,
    CarModelSerializer, CarSerializer, ReservationSerializer
)

class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"User created: {user.email}")

    def perform_destroy(self, instance):
        logger.info(f"User deleted: {instance.email}")
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Endpoint para obtener datos del usuario logueado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

class FuelTypeViewSet(viewsets.ModelViewSet):
    queryset = FuelType.objects.all()
    serializer_class = FuelTypeSerializer
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

class TransmissionViewSet(viewsets.ModelViewSet):
    queryset = Transmission.objects.all()
    serializer_class = TransmissionSerializer
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.select_related(
        'brand', 'vehicle_type', 'fuel_type', 'transmission'
    ).all()
    serializer_class = CarModelSerializer
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.select_related('car_model', 'car_model__brand', 'color').all()
    serializer_class = CarSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

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
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]  # ✅ PROTEGIDO

    def perform_create(self, serializer):
        reservation = serializer.save()
        logger.info(
            f"Reservation created: user={reservation.user.email}, car={reservation.car.license_plate}"
        )

    def perform_destroy(self, instance):
        logger.info(
            f"Reservation deleted: id={instance.id}, user={instance.user.email}"
        )
        instance.delete()
