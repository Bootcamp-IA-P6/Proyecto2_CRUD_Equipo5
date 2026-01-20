from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
from decimal import Decimal 


class AppUser(models.Model):
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    email           = models.EmailField(max_length=150, unique=True)
    password        = models.CharField(max_length=128)
    # Changed to mandatory for age calculation
    birth_date      = models.DateField(null=False, blank=False) 
    license_number  = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'app_user'

    def calculate_age(self):
        """Calculates current age based on birth_date"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'vehicle_type'

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'brand'

    def __str__(self):
        return self.name


class FuelType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'fuel_type'

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'color'

    def __str__(self):
        return self.name


class Transmission(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'transmission'

    def __str__(self):
        return self.name


class CarModel(models.Model):
    model_name      = models.CharField(max_length=100)
    brand           = models.ForeignKey(Brand, on_delete=models.PROTECT)
    vehicle_type    = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)
    seats           = models.IntegerField(null=True, blank=True)
    fuel_type       = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True)
    transmission    = models.ForeignKey(Transmission, on_delete=models.SET_NULL, null=True, blank=True)
    daily_price     = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'car_model'

    def __str__(self):
        return f"{self.model_name} ({self.brand.name})"


class Car(models.Model):
    car_model     = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=20, unique=True)
    color         = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    mileage       = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'car'

    def __str__(self):
        return f"{self.license_plate} - {self.car_model}"


class Reservation(models.Model):
    start_date   = models.DateField()
    end_date     = models.DateField()
    coverage     = models.CharField(max_length=100, blank=True, editable=False)
    rate         = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, editable=False)
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    user         = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    car          = models.ForeignKey(Car, on_delete=models.CASCADE)

    class Meta:
        db_table = 'reservation'

    def calculate_reservation_details(self):
        """
        Business Logic Fix: Use Decimal for rate to avoid TypeError
        """
        age = self.user.calculate_age()

        # Wrap numbers with Decimal()
        if age < 25:
            self.coverage = "Young Driver"
            self.rate = Decimal('1.50')
        elif age <= 65:
            self.coverage = "Standard"
            self.rate = Decimal('1.00')
        else:
            self.coverage = "Senior/Premium"
            self.rate = Decimal('1.20')

        # Calculate Duration (int)
        duration_days = (self.end_date - self.start_date).days + 1
        
        # Now multiplication will work: (int * Decimal * Decimal)
        daily_price = self.car.car_model.daily_price
        self.total_price = duration_days * daily_price * self.rate
        
    def clean(self):
        # Basic date validation
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": _("End date must be after start date.")})

        # Overlap check
        if self.start_date and self.end_date and self.car_id:
            overlapping = Reservation.objects.filter(
                car=self.car,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            ).exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(_("Selected dates overlap with another reservation."))

    def save(self, *args, **kwargs):
        # Trigger calculation logic before saving
        self.calculate_reservation_details()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva {self.id} - {self.user}"
