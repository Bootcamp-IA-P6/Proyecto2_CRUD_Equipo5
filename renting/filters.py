from django_filters import rest_framework as filters
from .models import Car, Reservation, AppUser


# ▶︎ Filters para Car
class CarFilter(filters.FilterSet):
	class Meta:
		model = Car
		fields = {
			'car_model__brand': ['exact'],           # /cars/?brand=1
			'car_model__vehicle_type': ['exact'],    # /cars/?vehicle_type=1
			'color': ['exact'],                      # /cars/?color=1
			# añade otros campos que quieras filtrar
		}


# ▶︎ Filters para Reservation
class ReservationFilter(filters.FilterSet):
	user = filters.ModelChoiceFilter(queryset=AppUser.objects.all())
	start_date = filters.DateFilter(field_name='start_date', lookup_expr='gte')
	end_date = filters.DateFilter(field_name='end_date', lookup_expr='lte')

	class Meta:
		model = Reservation
		fields = ['user', 'start_date', 'end_date']
