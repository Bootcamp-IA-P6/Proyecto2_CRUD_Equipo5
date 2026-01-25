import csv
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    AppUser, VehicleType, Brand, FuelType, Color, Transmission,
    CarModel, Car, Reservation
)


# ============================================
# Reusable CSV Export Action
# ============================================

@admin.action(description="Export selected items to CSV")
def export_as_csv(modeladmin, request, queryset):
    """
    Generic action to export selected model instances to a UTF-8 encoded CSV file.
    Includes BOM for Excel compatibility and dynamic headers based on model fields.
    """
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
    
    # Write UTF-8 BOM for Excel compatibility
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


# ============================================
# Issue #86: Lookup Models Admin
# ============================================

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    """Admin for Vehicle Types (Issue #86)"""
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    actions = [export_as_csv]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin for Brands (Issue #86)"""
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    actions = [export_as_csv]


@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
    """Admin for Fuel Types (Issue #86)"""
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    actions = [export_as_csv]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    """Admin for Colors (Issue #86)"""
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    actions = [export_as_csv]


@admin.register(Transmission)
class TransmissionAdmin(admin.ModelAdmin):
    """Admin for Transmissions (Issue #86)"""
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    actions = [export_as_csv]


# ============================================
# Issue #86: Main Models Admin with Validation
# ============================================

@admin.register(AppUser)
class AppUserAdmin(BaseUserAdmin):
    """
    Admin for Users with enhanced display (Issue #86)
    Inherits from BaseUserAdmin for proper password handling
    """
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'last_login']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    actions = [export_as_csv]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'first_name', 'last_name', 'birth_date', 'license_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login',)
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    """
    Admin for Car Models with validation (Issue #86)
    Enhanced UX with fieldsets and filters
    """
    list_display = ['model_name', 'brand', 'vehicle_type', 'fuel_type', 'transmission', 'seats', 'daily_price']
    list_filter = ['brand', 'vehicle_type', 'fuel_type', 'transmission']
    search_fields = ['model_name', 'brand__name']
    ordering = ['brand__name', 'model_name']
    actions = [export_as_csv]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'model_name', 'image')
        }),
        ('Specifications', {
            'fields': ('vehicle_type', 'fuel_type', 'transmission', 'seats')
        }),
        ('Pricing', {
            'fields': ('daily_price',),
            'description': 'Daily rental price (must be positive)'
        }),
    )


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    """
    Admin for Cars with validation (Issue #86)
    Enhanced UX with filters and search
    """
    list_display = ['license_plate', 'car_model', 'color', 'mileage']
    list_filter = ['color', 'car_model__brand']
    search_fields = ['license_plate', 'car_model__model_name', 'car_model__brand__name']
    ordering = ['license_plate']
    actions = [export_as_csv]
    
    fieldsets = (
        ('Car Identity', {
            'fields': ('car_model', 'license_plate', 'color')
        }),
        ('Details', {
            'fields': ('mileage',),
            'description': 'Mileage cannot be negative'
        }),
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Admin for Reservations with auto-calculation and validation (Issue #86)
    Enhanced UX with date hierarchy and filters
    """
    list_display = ['id', 'user', 'car', 'start_date', 'end_date', 'coverage', 'rate', 'total_price']
    list_filter = ['start_date', 'coverage']
    search_fields = ['user__email', 'car__license_plate']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    actions = [export_as_csv]
    
    fieldsets = (
        ('Reservation Details', {
            'fields': ('user', 'car')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date'),
            'description': 'End date must be equal to or later than start date'
        }),
        ('Auto-Calculated Fields', {
            'fields': ('coverage', 'rate', 'total_price'),
            'description': 'These fields are calculated automatically based on user age and duration'
        }),
    )
    
    readonly_fields = ['coverage', 'rate', 'total_price']  # Auto-calculated, read-only