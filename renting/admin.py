from django.contrib import admin
from .models import AppUser, CarModel, Car, Reservation

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    search_fields = ['email', 'first_name']

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'daily_price']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'car_model']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'start_date', 'total_price']
    list_filter = ['start_date', 'coverage']
