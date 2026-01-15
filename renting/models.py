from django.db import models

class AppUser(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField(max_length=150, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'app_user'

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
    coverage     = models.CharField(max_length=100, blank=True)
    fuel_policy  = models.CharField(max_length=50, blank=True)
    rate         = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user         = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    car          = models.ForeignKey(Car, on_delete=models.CASCADE)

    class Meta:
        db_table = 'reservation'

    def __str__(self):
        return f"Reserva {self.id} - {self.user}"
