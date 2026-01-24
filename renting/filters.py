from django_filters import rest_framework as filters
from .models import Car, Reservation, AppUser
from django.db.models import Q


# ▶︎ Filters para Reservation
class ReservationFilter(filters.FilterSet):
	user = filters.ModelChoiceFilter(queryset=AppUser.objects.all())
	start_date = filters.DateFilter(field_name='start_date', lookup_expr='gte')
	end_date = filters.DateFilter(field_name='end_date', lookup_expr='lte')

	class Meta:
		model = Reservation
		fields = ['user', 'start_date', 'end_date']

class CarFilter(filters.FilterSet):
    # 가격 범위 필터
    min_price = filters.NumberFilter(field_name="car_model__daily_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="car_model__daily_price", lookup_expr='lte')
    
    # 상세 스펙 필터
    seats = filters.NumberFilter(field_name="car_model__seats")
    transmission = filters.CharFilter(field_name="car_model__transmission__name")
    fuel = filters.CharFilter(field_name="car_model__fuel_type__name")
    
    # ⚠️ 핵심: 날짜 기반 가용성 필터 (시작일/종료일)
    available_from = filters.DateFilter(method='filter_availability')
    available_to = filters.DateFilter(method='filter_availability')

    class Meta:
        model = Car
        fields = {
			'car_model__brand': ['exact'],           # /cars/?brand=1
			'car_model__vehicle_type': ['exact'],    # /cars/?vehicle_type=1
			'color': ['exact'],                      # /cars/?color=1
			# añade otros campos que quieras filtrar
		}
        
    def filter_availability(self, queryset, name, value):
        """
        사용자가 선택한 기간에 이미 예약이 있는 차량을 제외합니다.
        """
        start_date = self.data.get('available_from')
        end_date = self.data.get('available_to')

        if start_date and end_date:
            # 해당 기간에 겹치는 예약이 있는 차량 ID들을 찾음
            # Logic: (R.start <= User.end) AND (R.end >= User.start)
            overlapping_reservations = Car.objects.filter(
                reservation__start_date__lte=end_date,
                reservation__end_date__gte=start_date
            ).values_list('id', flat=True)
            
            # 겹치는 차들을 제외(exclude)한 나머지만 반환
            return queryset.exclude(id__in=overlapping_reservations)
        
        return queryset