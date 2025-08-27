from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return obj.created_by == request.user

class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

class HasGroupPermission(BasePermission):
    required_groups = []

    def has_permission(self, request, view):
        if not request.user  or not request.user.is_authenticated:
            return False

        if not self.required_groups:
            return True

        user_groups = request.user.groups.values_list('name', flat=True)
        return any(group in user_groups for group in self.required_groups)

class IsRRHH(HasGroupPermission):
    required_groups = ['RRHH', 'Administrator']

class IsAdminUser(HasGroupPermission):
    required_groups = ['Administrador']