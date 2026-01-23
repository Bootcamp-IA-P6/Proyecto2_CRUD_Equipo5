from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError 
import re
from datetime import date
from django.contrib.auth.hashers import make_password
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        # 1. Agregamos 'password' a la lista de campos para que DRF lo reciba
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'birth_date', 'license_number']
        # ✅ write_only asegura que se pueda enviar pero nunca se vea en la respuesta
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 2. Usamos .pop con un valor por defecto para evitar el KeyError
        password = validated_data.pop('password', None)
        # Creamos el usuario (usamos create porque tu modelo no es el User de Django, es el tuyo)
        user = AppUser.objects.create(**validated_data) 
        
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

def capitalize_name(name):
    """Capitaliza cada palabra: 'maria de la cruz' → 'Maria De La Cruz'"""
    return ' '.join(word.capitalize() for word in name.split())

class AppUserSignupSerializer(serializers.ModelSerializer):
    """
    Issue #55 - Strict Signup Validation (solo para CREATE)
    """
    
    class Meta:
        model = AppUser
        fields = ['first_name', 'last_name', 'email', 'password', 'birth_date', 'license_number']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_first_name(self, value):
        """No numbers, no special chars, Capitalized"""
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        
        if not re.match(r'^[a-zA-Z\sáéíóúñÁÉÍÓÚÑ]+$', value):
            raise serializers.ValidationError("First name can only contain letters and spaces.")
        
        return capitalize_name(value.strip())  # ✅ Función personalizada
    
    def validate_last_name(self, value):
        """Igual que first_name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        
        if not re.match(r'^[a-zA-Z\sáéíóúñÁÉÍÓÚÑ]+$', value):
            raise serializers.ValidationError("Last name can only contain letters and spaces.")
        
        return capitalize_name(value.strip())
    
    def validate_email(self, value):
        """Valid format + unique"""
        if AppUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Enter a valid email address.")
        
        return value.lower().strip()
    
    def validate_password(self, value):
        """8+ chars, upper, lower, number, special, no emojis"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain 1 uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain 1 lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain 1 number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain 1 special character.")
        
        return value
    
    def validate_birth_date(self, value):
        """>= 18 años, no futuro"""
        today = date.today()
        if value > today:
            raise serializers.ValidationError("Birth date cannot be in the future.")
        
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")
        
        return value
    
    def create(self, validated_data):
        """Hashear password"""
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        return super().create(validated_data)


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class FuelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelType
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


class TransmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transmission
        fields = '__all__'


class CarModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    vehicle_type_name = serializers.CharField(source='vehicle_type.name', read_only=True)
    fuel_type_name = serializers.CharField(source='fuel_type.name', read_only=True)
    transmission_name = serializers.CharField(source='transmission.name', read_only=True)

    class Meta:
        model = CarModel
        fields = '__all__'


    # VALIDACIÓN: El precio no puede ser negativo
    def validate_daily_price(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio diario no puede ser negativo.")
        return value


class CarSerializer(serializers.ModelSerializer):
    car_model_name = serializers.CharField(source='car_model.model_name', read_only=True)
    brand_name = serializers.CharField(source='car_model.brand.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)

    class Meta:
        model = Car
        fields = '__all__'
    
    # (Aquí ya no hace falta el validate_price porque el precio está en CarModel)


class ReservationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    car_license = serializers.CharField(source='car.license_plate', read_only=True)
    model_name = serializers.CharField(source='car.car_model.model_name', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'start_date', 'end_date', 'coverage', 'rate', 
            'total_price', 'user', 'car', 
            'user_name', 'car_license', 'model_name'
        ]
        read_only_fields = ['user', 'coverage', 'rate', 'total_price']

        # ← AÑADIR extra_kwargs (doble seguro)
        extra_kwargs = {
            'user': {'read_only': True},
        }

    def validate(self, attrs):
        # 1. 현재 요청을 보낸 유저 정보를 가져옵니다.
        request = self.context.get('request')
        user = request.user if request else None

        # 2. 검증용 임시 인스턴스를 만들 때 유저 정보를 포함시킵니다.
        # (이렇게 해야 full_clean()이 '유저가 없네?'라고 화내지 않습니다.)
        instance = getattr(self, 'instance', None)
        if instance:
            for attr, value in attrs.items():
                setattr(instance, attr, value)
        else:
            instance = Reservation(user=user, **attrs)

        try:
            instance.full_clean()
        except ValidationError as e:
            # 장고 모델 에러를 DRF 에러로 변환
            raise serializers.ValidationError(e.message_dict)
            
        return attrs

    # VALIDACIÓN: El total de la reserva debe ser positivo
    def validate_total_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("El precio total debe ser mayor que cero.")
        return value 

class MyTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.EmailField(required=True)  # ← required=True
    password = serializers.CharField(write_only=True, required=True)  # ← required=True

    def validate(self, attrs):
        email = attrs.get("username")
        password = attrs.get("password")

        # 1. Validación campos requeridos
        errors = {}
        if not email:
            errors["username"] = ["Email is required."]
        if not password:
            errors["password"] = ["Password is required."]
        
        if errors:
            raise serializers.ValidationError(errors)

        # 2. Normalizar email
        email = email.strip().lower()

        # 3. Credenciales SIN filtrar info sensible
        try:
            user = AppUser.objects.get(email=email)
        except AppUser.DoesNotExist:
            # SIEMPRE misma respuesta (no dice si existe o no)
            raise serializers.ValidationError({
                "detail": "Invalid credentials."
            })

        if not user.check_password(password):
            # Misma respuesta que arriba
            raise serializers.ValidationError({
                "detail": "Invalid credentials."
            })

        # 4. Éxito → tokens
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# temp change to trigger git