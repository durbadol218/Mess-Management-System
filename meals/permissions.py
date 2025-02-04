from rest_framework.permissions import BasePermission

class IsAdminUserType(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == "Admin"
