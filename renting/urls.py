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
