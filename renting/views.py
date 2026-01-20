import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)
from .pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

def user_list(request):
    logger.info("User list page accessed")
    users = AppUser.objects.all()
    return render(request, 'renting/users/list.html', {'users': users})

# --- Protected Views ---
def car_list(request):
    # Security check: if not logged in, go to login page
    if 'user_id' not in request.session:
        return redirect('login')
    
    cars = Car.objects.select_related('car_model', 'car_model__brand').all()
    return render(request, 'renting/cars/list.html', {'cars': cars})

def reservation_list(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    reservations = Reservation.objects.select_related('user', 'car', 'car__car_model').all()
    return render(request, 'renting/reservations/list.html', {'reservations': reservations})

def home(request):
    # Standard stats for home page
    context = {
        'total_users': AppUser.objects.count(),
        'total_cars': Car.objects.count(),
        'total_reservations': Reservation.objects.count(),
        'user_name': request.session.get('user_name', 'Guest')
    }
    return render(request, 'renting/home.html', context)

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

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = AppUser.objects.get(email=email)
            if user.check_password(password):
                # 1. 세션 로그인 (현재 UI 유지용)
                request.session['user_id'] = user.id
                request.session['user_name'] = user.first_name
                
                # 2. JWT 토큰 생성 (이슈 요구사항 충족용)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                # 3. 템플릿으로 토큰을 전달해서 localStorage에 저장하게 함
                return render(request, 'renting/login.html', {
                    'access_token': access_token,
                    'success': True
                })
            else:
                messages.error(request, "Invalid password")
        except AppUser.DoesNotExist:
            messages.error(request, "User not found")
    return render(request, 'renting/login.html')

def logout_view(request):
    request.session.flush() # Clear all session data
    return redirect('login')

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        birth_date = request.POST.get('birth_date')

        # 간단한 중복 체크
        if AppUser.objects.filter(email=email).exists():
            messages.error(request, "Este email ya está registrado.")
            return render(request, 'renting/register.html')

        # 유저 생성 및 비밀번호 암호화
        new_user = AppUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            birth_date=birth_date
        )
        new_user.set_password(password) # 핵심: 여기서 암호화됨
        new_user.save()

        messages.success(request, "Cuenta creada con éxito. Por favor, inicia sesión.")
        return redirect('login')

    return render(request, 'renting/register.html')

def reservation_create(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == "POST":
        car_id = request.POST.get('car')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        user_id = request.session['user_id']

        try:
            # Create object - Model's save() will handle calculations
            res = Reservation(
                user_id=user_id,
                car_id=car_id,
                start_date=start_date,
                end_date=end_date
            )
            res.full_clean() # Run validation (overlap, dates, etc.)
            res.save()
            messages.success(request, f"Reserva creada con éxito. Total: {res.total_price}€")
            return redirect('reservation_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    cars = Car.objects.select_related('car_model').all()
    return render(request, 'renting/reservations/create.html', {'cars': cars})