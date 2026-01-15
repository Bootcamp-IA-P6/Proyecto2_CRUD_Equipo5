from django.shortcuts import render
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)

def home(request):
    return render(request, 'renting/home.html', {
        'total_users': AppUser.objects.count(),
        'total_cars': Car.objects.count(),
        'total_reservations': Reservation.objects.count(),
    })

def user_list(request):
    users = AppUser.objects.all()
    return render(request, 'renting/users/list.html', {'users': users})

def car_list(request):
    cars = Car.objects.select_related('car_model', 'car_model__brand').all()
    return render(request, 'renting/cars/list.html', {'cars': cars})

def reservation_list(request):
    reservations = Reservation.objects.select_related('user', 'car', 'car__car_model').all()
    return render(request, 'renting/reservations/list.html', {'reservations': reservations})

#API Views

from rest_framework import viewsets
from .serializers import (
    AppUserSerializer, VehicleTypeSerializer, BrandSerializer,
    FuelTypeSerializer, ColorSerializer, TransmissionSerializer,
    CarModelSerializer, CarSerializer, ReservationSerializer
)

class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer

class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class FuelTypeViewSet(viewsets.ModelViewSet):
    queryset = FuelType.objects.all()
    serializer_class = FuelTypeSerializer

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class TransmissionViewSet(viewsets.ModelViewSet):
    queryset = Transmission.objects.all()
    serializer_class = TransmissionSerializer

class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.select_related(
        'brand', 'vehicle_type', 'fuel_type', 'transmission'
    ).all()
    serializer_class = CarModelSerializer

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.select_related('car_model', 'car_model__brand', 'color').all()
    serializer_class = CarSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related(
        'user', 'car', 'car__car_model', 'car__car_model__brand'
    ).all()
    serializer_class = ReservationSerializer
