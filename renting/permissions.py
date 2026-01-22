# renting/permissions.py
from rest_framework import permissions

class IsReservationOwnerOrStaff(permissions.BasePermission):
    """
    Issue #24 - User Ownership:
    - Staff: acceso total
    - Non-staff: solo sus propias reservas
    """
    
    def has_permission(self, request, view):
        return True  # list/create OK (queryset filtrado)
    
    def has_object_permission(self, request, view, obj):
        # Staff: todo OK
        if request.user.is_staff:
            return True
        # Non-staff: solo suya
        return obj.user == request.user
