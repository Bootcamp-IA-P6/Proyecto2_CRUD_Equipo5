from rest_framework import serializers
from django.core.exceptions import ValidationError 
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
            raise serializers.ValidationError(e.message_dict)
        return attrs
