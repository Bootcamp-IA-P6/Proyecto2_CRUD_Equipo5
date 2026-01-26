from django_filters import rest_framework as filters
from .models import Car, Reservation, AppUser
from django.db.models import Q


# Reservation Filters
class ReservationFilter(filters.FilterSet):
    user = filters.ModelChoiceFilter(queryset=AppUser.objects.all())
    start_date = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = Reservation
        fields = ['user', 'start_date', 'end_date']


class CarFilter(filters.FilterSet):
    # Price range filters
    min_price = filters.NumberFilter(field_name="car_model__daily_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="car_model__daily_price", lookup_expr='lte')
    
    # Detailed spec filters
    seats = filters.NumberFilter(field_name="car_model__seats")
    transmission = filters.CharFilter(field_name="car_model__transmission__name")
    fuel = filters.CharFilter(field_name="car_model__fuel_type__name")
    
    # Core: Date-based availability filter (start_date/end_date)
    available_from = filters.CharFilter(method='filter_availability')
    available_to = filters.CharFilter(method='filter_availability')
    
    class Meta:
        model = Car
        fields = {
            'car_model__brand': ['exact'],          # /cars/?brand=1
            'car_model__vehicle_type': ['exact'],   # /cars/?vehicle_type=1
            'color': ['exact'],                     # /cars/?color=1
        }
        
    def filter_availability(self, queryset, name, value):
        """
        Filter cars available for specific date range.
        Excludes cars with overlapping reservations.
        """
        # Skip processing for available_from parameter (avoid duplicate calls)
        if name == 'available_from':
            return queryset

        start_date = self.data.get('available_from')
        end_date = self.data.get('available_to')

        if start_date and end_date:
            try:
                # 1. Get IDs of cars with overlapping reservations
                # (existing_start <= user_end) AND (existing_end >= user_start)
                occupied_car_ids = Reservation.objects.filter(
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).values_list('car_id', flat=True).distinct()

                # 2. Exclude occupied cars from queryset
                return queryset.exclude(id__in=occupied_car_ids)
            except Exception as e:
                # Return original queryset on error to prevent server crash
                import logging
                logging.getLogger(__name__).error(f"Availability filter error: {e}")
                return queryset
                
        return queryset
