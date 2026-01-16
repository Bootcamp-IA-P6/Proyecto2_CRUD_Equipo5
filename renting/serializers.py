from rest_framework import serializers
from django.core.exceptions import ValidationError 
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'first_name', 'last_name', 'email', 'birth_date', 'license_number']
        # ✅ password EXCLUIDO, manejado en create/update
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = AppUser.objects.create_user(
            **validated_data, 
            password=password  # ✅ Hash automático
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        super().update(instance, validated_data)
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


class CarSerializer(serializers.ModelSerializer):
    car_model_name = serializers.CharField(source='car_model.model_name', read_only=True)
    brand_name = serializers.CharField(source='car_model.brand.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)

    class Meta:
        model = Car
        fields = '__all__'


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
        # ✅ fuel_policy EXCLUIDO explícitamente

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        instance = instance or Reservation(**attrs)
        
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs