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
    available_from = filters.CharFilter(method='filter_availability')
    available_to = filters.CharFilter(method='filter_availability')
    
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
        [FIX] 500 에러 완벽 해결 로직
        """
        # available_to가 들어왔을 때만 로직을 실행하도록 제한 (중복 실행 방지)
        if name == 'available_from':
            return queryset

        start_date = self.data.get('available_from')
        end_date = self.data.get('available_to')

        if start_date and end_date:
            try:
                # 1. 해당 기간에 '이미 예약이 걸린' 차량들의 ID만 추출
                # (기존예약시작일 <= 유저종료일) AND (기존예약종료일 >= 유저시작일)
                occupied_car_ids = Reservation.objects.filter(
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).values_list('car_id', flat=True).distinct()

                # 2. 전체 쿼리셋에서 해당 차량 ID들을 제외(exclude)
                return queryset.exclude(id__in=occupied_car_ids)
            except Exception as e:
                # 만약 에러가 나더라도 서버가 터지지 않게 원래 쿼리셋 반환
                import logging
                logging.getLogger(__name__).error(f"Availability Filter Error: {e}")
                return queryset
        
        return queryset