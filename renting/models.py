from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password

# for superuser creation
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
        extra_fields.setdefault('is_staff', True) # 슈퍼유저는 스태프 권한 가짐
        return self.create_user(email, first_name, last_name, password, **extra_fields)
    
class AppUser(AbstractBaseUser):
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    email           = models.EmailField(max_length=150, unique=True)
    password        = models.CharField(max_length=128)
    birth_date      = models.DateField(null=True, blank=True)
    license_number  = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'app_user'

    def set_password(self, raw_password):
        """Hash password antes de guardar"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verificar password"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # JWT/Django 인증 호환을 위한 필수 속성
    @property
    def is_authenticated(self): return True
    @property
    def is_active(self): return True
    @property
    def is_anonymous(self): return False

    # [추가] Admin 접속을 위해 필요한 속성
    @property
    def is_staff(self):
        # 모든 유저에게 어드민 접속 권한을 주려면 True
        # 특정 유저만 주고 싶다면 DB에 필드를 추가해야 하지만, 지금은 테스트를 위해 True로 설정합니다.
        return True

    # admin auth check
    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff
    
    # SimpleJWT는 'id' 필드명을 기준으로 토큰을 만듭니다
    @property
    def id(self): return self.pk

    is_staff        = models.BooleanField(default=False) # 기본값은 False (일반유저)
    last_login      = models.DateTimeField(null=True, blank=True)

    objects = AppUserManager()
    
    # Django 인증 시스템이 요구하는 식별자
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['first_name', 'last_name']


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
    rate         = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user         = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    car          = models.ForeignKey(Car, on_delete=models.CASCADE)

    class Meta:
        db_table = 'reservation'

    def __str__(self):
        return f"Reserva {self.id} - {self.user}"

    def clean(self):
        # 1) start_date <= end_date
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({
                "end_date": _("La fecha de fin debe ser igual o posterior a la fecha de inicio.")
            })

        # 2) evitar solapes para el mismo coche
        if self.start_date and self.end_date and self.car_id:
            overlapping = Reservation.objects.filter(
                car=self.car,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )

            # excluirse a sí misma en updates
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(
                    _("Las fechas seleccionadas se solapan con otra reserva para este vehículo.")
                )
            
    # 1. 자동 계산 메서드
    def calculate_details(self):
        from datetime import date
        from decimal import Decimal
        
        # 나이 계산
        today = date.today()
        birth = self.user.birth_date
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

        # 커버리지 및 계수 결정
        if age < 25:
            self.coverage = "Young Driver"
            self.rate = Decimal('1.50')
        elif age <= 65:
            self.coverage = "Standard"
            self.rate = Decimal('1.00')
        else:
            self.coverage = "Senior/Premium"
            self.rate = Decimal('1.20')

        # 기간 및 총액 계산
        duration = (self.end_date - self.start_date).days + 1
        daily_price = self.car.car_model.daily_price
        self.total_price = Decimal(duration) * daily_price * self.rate

    # 2. 저장 시 자동 실행
    def save(self, *args, **kwargs):
        self.calculate_details()
        super().save(*args, **kwargs)

# temp change to trigger git