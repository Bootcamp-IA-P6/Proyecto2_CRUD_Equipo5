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

class IsStaffPermission(permissions.BasePermission):
    """#61 Staff: manage vehicles + view all users"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_staff

class IsStaffOrReadOnlyPermission(permissions.BasePermission):
    """#61 Staff=CRUD, Public=ReadOnly"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user.is_staff