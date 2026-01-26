from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    AppUserViewSet, VehicleTypeViewSet, BrandViewSet, FuelTypeViewSet,
    ColorViewSet, TransmissionViewSet, CarModelViewSet, CarViewSet,
    ReservationViewSet
)
from .profile_views import ProfileView, ChangePasswordView


# API Router for ViewSets
# Router con basenames explícitos
router = DefaultRouter()
router.register(r'users', AppUserViewSet, basename='appuser')
router.register(r'vehicle-types', VehicleTypeViewSet, basename='vehicletype')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'fuel-types', FuelTypeViewSet, basename='fueltype')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'transmissions', TransmissionViewSet, basename='transmission')
router.register(r'car-models', CarModelViewSet, basename='carmodel')
router.register(r'cars', CarViewSet, basename='car')
router.register(r'reservations', ReservationViewSet, basename='reservation')


urlpatterns = [
    # ==========================================
    # HTML Template Views
    # ==========================================
    path('', views.home, name='home'),
    path('users/', views.user_list, name='user_list'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:id>/', views.car_detail, name='car_detail'),
    path('profile/', views.profile_view, name='profile_view'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.reservation_create, name='reservation_create'),
    
    # ==========================================
    # Authentication HTML Views
    # ==========================================
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==========================================
    # API Endpoints
    # ==========================================
    path('api/', include(router.urls)),  # REST API ViewSets
    
    # Profile management endpoints (current user)
    path('api/profile/me/', ProfileView.as_view(), name='profile-me'),
    path('api/profile/me/change-password/', ChangePasswordView.as_view(), name='profile-change-password'),
]
