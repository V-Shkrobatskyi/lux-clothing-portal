from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_staff or obj.user == request.user)


class IsAdminALLOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_staff or request.method in SAFE_METHODS)
