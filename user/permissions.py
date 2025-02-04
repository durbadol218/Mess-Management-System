from rest_framework.permissions import BasePermission

class IsAdminUserType(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.account_type == 'admin':
            return True
        return False

