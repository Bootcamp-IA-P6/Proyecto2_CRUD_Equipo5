import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import AppUser, CarModel, Car, Reservation

# Define a reusable admin action to export records to CSV
@admin.action(description="Export selected items to CSV")
def export_as_csv(modeladmin, request, queryset):
    """
    Generic action to export selected model instances to a UTF-8 encoded CSV file.
    Includes BOM for Excel compatibility and dynamic headers based on model fields.
    """
    meta = modeladmin.model._meta
    # Get all field names for the CSV header row
    field_names = [field.name for field in meta.fields]

    # Create the HTTP response with CSV content type and UTF-8 encoding
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
    
    # Write UTF-8 BOM to ensure special characters display correctly in Excel
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response)
    writer.writerow(field_names)  # Write header row

    # Write data rows for the selected objects
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    search_fields = ['email', 'first_name']
    actions = [export_as_csv]  # Enable CSV export

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'daily_price']
    actions = [export_as_csv]

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'car_model']
    actions = [export_as_csv]  # Enable CSV export

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'start_date', 'total_price']
    list_filter = ['start_date', 'coverage']
    actions = [export_as_csv]  # Enable CSV export