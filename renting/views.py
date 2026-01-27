import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .filters import CarFilter, ReservationFilter
from .filters import CarFilter, ReservationFilter
from .permissions import IsReservationOwnerOrStaff, IsStaffPermission, IsStaffOrReadOnlyPermission 
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)
from .serializers import (
    AppUserSerializer, VehicleTypeSerializer, BrandSerializer,
    FuelTypeSerializer, ColorSerializer, TransmissionSerializer,
    CarModelSerializer, CarSerializer, ReservationSerializer, AppUserSignupSerializer
)


logger = logging.getLogger(__name__)


# ==========================================
# HTML Template Views
# ==========================================
def user_list(request):
    """Display list of all users"""
    logger.info("User list page accessed")
    users = AppUser.objects.all()
    return render(request, 'renting/users/list.html', {'users': users})


def home(request):
    """Render home page"""
    return render(request, 'renting/home.html')


def car_list(request):
    """Render car list page"""
    return render(request, 'renting/cars/list.html')


@login_required
def reservation_list(request):
    """Render reservation list page"""
    return render(request, 'renting/reservations/list.html')


def car_detail(request, id):
    """Render car detail page"""
    return render(request, 'renting/cars/detail.html', {'car_id': id})


@login_required
def profile_view(request):
    """Render user profile page"""
    return render(request, 'renting/users/profile.html')


def login_view(request):
    """Render login page"""
    return render(request, 'renting/login.html')


def logout_view(request):
    """Redirect to login page"""
    return redirect('login')


def register_view(request):
    """Render registration page"""
    return render(request, 'renting/register.html')


@login_required
def reservation_create(request):
    """Render reservation creation page"""
    return render(request, 'renting/reservations/create.html')


# ==========================================
# API ViewSets
# ==========================================
class IsOwnerOrStaffOrCreateOnly(permissions.BasePermission):
    """
    Custom permission for user management:
    - Anyone can create (register)
    - Authenticated users can access /me/ endpoints  
    - Staff only for list/retrieve/update/delete others
    """
    
    def has_permission(self, request, view):
        # Allow registration without authentication
        if view.action == 'create':
            return True
        
        # Custom actions require authentication
        if view.action in ['me', 'update_me', 'delete_me', 'change_password']:
            return (
                request.user 
                and request.user.is_authenticated 
                and getattr(request.user, 'is_active', True)
            )
        
        # List/retrieve/update/destroy require staff
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.is_staff 
            and getattr(request.user, 'is_active', True)
        )
    
    def has_object_permission(self, request, view, obj):
        # Staff has full access
        if request.user.is_staff:
            return True
        # Users can only modify their own account
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
        """Log user creation"""
        user = serializer.save()
        logger.info(f"User created: {user.email}")

    def perform_destroy(self, instance):
        """Log user deletion"""
        logger.info(f"User deleted: {instance.email}")
        instance.delete()

    # ==========================================
    # Current User Endpoints (/me/)
    # ==========================================
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """GET /api/users/me/ - Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], url_path='me')
    def update_me(self, request):
        """PUT/PATCH /api/users/me/ - Update current user profile"""
        current_password = request.data.get('current_password')
        
        # Require password for sensitive fields
        sensitive_fields = {'email'}
        is_sensitive_update = any(field in request.data for field in sensitive_fields)
        
        if is_sensitive_update and not current_password:
            return Response(
                {"error": "current_password is required for sensitive changes"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if current_password and not request.user.check_password(current_password):
            return Response(
                {"error": "Invalid current password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove current_password from data
        data = request.data.copy()
        data.pop('current_password', None)
        
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
        """DELETE /api/users/me/ - Delete current user account"""
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
        
        user = request.user
        logger.info(f"User self-deleted: {user.email}")
        user.delete()
        return Response(
            {"detail": "Account deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        """POST /api/users/me/change-password/ - Change current user password"""
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
        
        if len(new_password) < 8:
            return Response(
                {"error": "New password must be at least 8 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        logger.info(f"Password changed for user: {request.user.email}")
        return Response({"detail": "Password updated successfully"})


class VehicleTypeViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for vehicle types"""
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsStaffOrReadOnlyPermission]


class BrandViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for brands"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsStaffOrReadOnlyPermission]


class FuelTypeViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for fuel types"""
    queryset = FuelType.objects.all()
    serializer_class = FuelTypeSerializer
    permission_classes = [IsStaffOrReadOnlyPermission] 


class ColorViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for colors"""
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsStaffOrReadOnlyPermission]


class TransmissionViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for transmissions"""
    queryset = Transmission.objects.all()
    serializer_class = TransmissionSerializer
    permission_classes = [IsStaffOrReadOnlyPermission]


class CarModelViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for car models with optimized queries"""
    queryset = CarModel.objects.select_related(
        'brand', 'vehicle_type', 'fuel_type', 'transmission'
    ).all()
    serializer_class = CarModelSerializer
    permission_classes = [IsStaffOrReadOnlyPermission]


class CarViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Car resources.

    Provides CRUD operations with:
    - Optimized queryset using select_related
    - Filtering, ordering, and unified keyword search
    - Availability filtering based on reservation dates
    - Logging for create and delete actions
    """

    # Base queryset optimized with select_related to reduce DB queries
    queryset = Car.objects.select_related(
        'car_model',
        'car_model__brand',
        'color'
    ).all()

    serializer_class = CarSerializer
    permission_classes = [IsStaffOrReadOnlyPermission]

    # Enable filtering and ordering backends
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CarFilter
    ordering_fields = ['license_plate', 'car_model__daily_price', 'mileage']

    def get_queryset(self):
        """
        Override base queryset to apply:
        - Unified keyword search (Brand OR Model)
        - Availability filtering by date range

        Returns a filtered queryset based on query parameters.
        """
        # Get the base queryset before filter backends are applied
        queryset = super().get_queryset()

        # Unified keyword search across brand name and model name
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(car_model__brand__name__icontains=search_query) |
                Q(car_model__model_name__icontains=search_query)
            )

        # Availability filtering: exclude cars with overlapping reservations
        date_from = self.request.query_params.get('available_from', None)
        date_to = self.request.query_params.get('available_to', None)

        if date_from and date_to:
            occupied_car_ids = Reservation.objects.filter(
                start_date__lte=date_to,
                end_date__gte=date_from
            ).values_list('car_id', flat=True)

            queryset = queryset.exclude(id__in=occupied_car_ids)

        return queryset

    def perform_create(self, serializer):
        """
        Save a new Car instance and log the creation event.
        """
        car = serializer.save()
        logger.info(f"Car created: {car.license_plate}")

    def perform_destroy(self, instance):
        """
        Delete a Car instance and log the deletion event.
        """
        logger.info(f"Car deleted: {instance.license_plate}")
        instance.delete()


class ReservationViewSet(viewsets.ModelViewSet):
    """Authenticated users manage reservations (own only, staff all)"""
    queryset = Reservation.objects.select_related(
        'user', 'car', 'car__car_model', 'car__car_model__brand'
    ).all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, IsReservationOwnerOrStaff]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReservationFilter
    search_fields = ['user__email', 'car__license_plate']
    ordering_fields = ['start_date', 'end_date']

    def get_queryset(self):
        """Non-staff users see only their reservations (Issue #24)"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        """Auto-assign current user and log creation"""
        reservation = serializer.save(user=self.request.user)
        logger.info(
            f"Reservation created: user={reservation.user.email}, car={reservation.car.license_plate}"
        )

    def perform_destroy(self, instance):
        """Log reservation deletion"""
        logger.info(
            f"Reservation deleted: id={instance.id}, user={instance.user.email}"
        )
        instance.delete()

    def get_permissions(self):
        """Explicit permissions for list/retrieve (Issue #61)"""
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated(), IsReservationOwnerOrStaff()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='my')
    def my_reservations(self, request):
        """GET /api/reservations/my/?status=upcoming|past - Filter user reservations (Issue #62)"""
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
        """DELETE /api/reservations/{id}/delete-with-password/ - Secure deletion (Issue #62)"""
        reservation = self.get_object()
        
        # Past reservations are read-only
        if reservation.end_date < timezone.now().date():
            return Response(
                {"detail": "Past reservations cannot be deleted"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Require password confirmation
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
