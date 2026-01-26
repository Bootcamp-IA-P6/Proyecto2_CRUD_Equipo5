from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal


# ============================================
# User Management
# ============================================

class AppUserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)
    
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)

    
class AppUser(AbstractBaseUser, PermissionsMixin): 
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    email           = models.EmailField(max_length=150, unique=True)
    password        = models.CharField(max_length=128)
    birth_date      = models.DateField(null=True, blank=True)
    license_number  = models.CharField(max_length=50, blank=True)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    last_login      = models.DateTimeField(null=True, blank=True)

    objects = AppUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'app_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


# ============================================
# Lookup Models (Issue #86: Admin-manageable)
# ============================================

class VehicleType(models.Model):
    """
    Lookup table for vehicle types (e.g., SUV, Sedan, Truck)
    Issue #86: Must be admin-manageable
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'vehicle_type'
        verbose_name = 'Vehicle Type'
        verbose_name_plural = 'Vehicle Types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    """
    Lookup table for car brands (e.g., Toyota, Ford)
    Issue #86: Must be admin-manageable
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'brand'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def __str__(self):
        return self.name


class FuelType(models.Model):
    """
    Lookup table for fuel types (e.g., Gasoline, Diesel, Electric)
    Issue #86: Must be admin-manageable
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'fuel_type'
        verbose_name = 'Fuel Type'
        verbose_name_plural = 'Fuel Types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Color(models.Model):
    """
    Lookup table for car colors
    Issue #86: Must be admin-manageable
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'color'
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'
        ordering = ['name']

    def __str__(self):
        return self.name


class Transmission(models.Model):
    """
    Lookup table for transmission types (e.g., Manual, Automatic)
    Issue #86: Must be admin-manageable
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'transmission'
        verbose_name = 'Transmission'
        verbose_name_plural = 'Transmissions'
        ordering = ['name']

    def __str__(self):
        return self.name


# ============================================
# Car Models (Issue #86: Add validation)
# ============================================

class CarModel(models.Model):
    """
    Car model with validated numeric fields
    Issue #86: Enforce positive values and valid ranges
    """
    model_name      = models.CharField(max_length=100)
    brand           = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='car_models')
    vehicle_type    = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Issue #86: Validated numeric fields
    seats           = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Number of seats (1-50)"
    )
    
    fuel_type       = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True)
    transmission    = models.ForeignKey(Transmission, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Issue #86: Daily price must be positive
    daily_price     = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Daily rental price (must be positive)"
    )
    
    image           = models.ImageField(upload_to='car_models/', null=True, blank=True)

    class Meta:
        db_table = 'car_model'
        verbose_name = 'Car Model'
        verbose_name_plural = 'Car Models'
        ordering = ['brand__name', 'model_name']

    def clean(self):
        """Issue #86: Additional validation logic"""
        super().clean()
        
        # Validar seats si se proporciona
        if self.seats is not None:
            if self.seats < 1:
                raise ValidationError({'seats': _('Seats must be at least 1')})
            if self.seats > 50:
                raise ValidationError({'seats': _('Seats cannot exceed 50')})
        
        # Validar daily_price
        if self.daily_price is not None and self.daily_price <= 0:
            raise ValidationError({'daily_price': _('Daily price must be greater than 0')})

    def __str__(self):
        return f"{self.model_name} ({self.brand.name})"


class Car(models.Model):
    """
    Individual car instance with validated fields
    Issue #86: Enforce valid mileage (non-negative)
    """
    car_model     = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='cars')
    license_plate = models.CharField(max_length=20, unique=True)
    color         = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Issue #86: Validated mileage (cannot be negative)
    mileage       = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Current mileage (cannot be negative)"
    )

    class Meta:
        db_table = 'car'
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'
        ordering = ['license_plate']

    def clean(self):
        """Issue #86: Additional validation logic"""
        super().clean()
        
        if self.mileage is not None and self.mileage < 0:
            raise ValidationError({'mileage': _('Mileage cannot be negative')})

    def __str__(self):
        return f"{self.license_plate} - {self.car_model}"


# ============================================
# Reservations
# ============================================

class Reservation(models.Model):
    """
    Reservation model with automatic price calculation and date validation
    Issue #86: Ensure end_date >= start_date and total_price > 0
    """
    start_date   = models.DateField()
    end_date     = models.DateField()
    coverage     = models.CharField(max_length=100, blank=True)
    rate         = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    
    # Issue #86: Total price must be positive
    total_price  = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total reservation price (calculated automatically)"
    )
    
    user         = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='reservations')
    car          = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reservations')

    class Meta:
        db_table = 'reservation'
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        ordering = ['-start_date']

    def clean(self):
        """Validation: dates and overlaps"""
        super().clean()
        
        # Issue #86: Validate end_date >= start_date
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({
                "end_date": _("End date must be equal to or later than start date")
            })

        # Validate no overlaps for the same car
        if self.start_date and self.end_date and self.car_id:
            overlapping = Reservation.objects.filter(
                car=self.car,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )

            # Exclude self when updating
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(
                    _("Selected dates overlap with another reservation for this vehicle")
                )
        
        # Issue #86: Validate total_price if manually set
        if self.total_price is not None and self.total_price <= 0:
            raise ValidationError({'total_price': _('Total price must be greater than 0')})
            
    def calculate_details(self):
        """Auto-calculate coverage, rate, and total_price based on user age"""
        from datetime import date
        
        # Calculate age
        today = date.today()
        birth = self.user.birth_date
        
        if not birth:
            # Default values if birth_date not available
            self.coverage = "Standard"
            self.rate = Decimal('1.00')
        else:
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

            # Determine coverage and rate based on age
            if age < 25:
                self.coverage = "Young Driver"
                self.rate = Decimal('1.50')
            elif age <= 65:
                self.coverage = "Standard"
                self.rate = Decimal('1.00')
            else:
                self.coverage = "Senior/Premium"
                self.rate = Decimal('1.20')

        # Calculate duration and total price
        duration = (self.end_date - self.start_date).days + 1
        daily_price = self.car.car_model.daily_price
        self.total_price = Decimal(duration) * daily_price * self.rate

    def save(self, *args, **kwargs):
        """Auto-calculate details before saving"""
        self.calculate_details()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.id} - {self.user.email} ({self.start_date} to {self.end_date})"