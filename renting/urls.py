from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    AppUserViewSet, VehicleTypeViewSet, BrandViewSet, FuelTypeViewSet,
    ColorViewSet, TransmissionViewSet, CarModelViewSet, CarViewSet,
    ReservationViewSet
)

router = DefaultRouter()
router.register(r'users', AppUserViewSet)
router.register(r'vehicle-types', VehicleTypeViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'fuel-types', FuelTypeViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'transmissions', TransmissionViewSet)
router.register(r'car-models', CarModelViewSet)
router.register(r'cars', CarViewSet)
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.user_list, name='user_list'),
    path('cars/', views.car_list, name='car_list'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('api/', include(router.urls)),
]
