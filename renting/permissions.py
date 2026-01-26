# renting/permissions.py
from rest_framework import permissions


class IsReservationOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission for reservations (Issue #24).
    Staff: full access. Regular users: own reservations only.
    """
    
    def has_permission(self, request, view):
        return True  # Allow list/create (queryset filtered)
    
    def has_object_permission(self, request, view, obj):
        # Staff has full access
        if request.user.is_staff:
            return True
        # Regular users: own reservations only
        return obj.user == request.user


class IsStaffPermission(permissions.BasePermission):
    """Staff-only permission for vehicle management and user viewing (Issue #61)"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_staff


class IsStaffOrReadOnlyPermission(permissions.BasePermission):
    """Staff: full CRUD. Public: read-only access (Issue #61)"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user.is_staff
