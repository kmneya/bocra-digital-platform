from rest_framework import permissions

class IsOfficerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['officer', 'admin']