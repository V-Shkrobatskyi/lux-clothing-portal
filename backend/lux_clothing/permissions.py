from rest_framework.permissions import SAFE_METHODS, BasePermission

from lux_clothing.models import Profile


class IsOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_staff or obj.user == request.user)


class IsAddressOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_staff or obj in request.user.profile.addresses.all()
        )


class IsAdminALLOrOwnerCanPostAndGet(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_staff
            or (obj.user == request.user and request.method in ["POST", "GET"])
        )


class IsAdminALLOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_staff or request.method in SAFE_METHODS)


class IsAdminALLOrHasProfile(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_staff or Profile.objects.filter(user=request.user))


class HasProfile(BasePermission):
    def has_permission(self, request, view):
        return bool(Profile.objects.filter(user=request.user))


class IsAuthenticatedAndHasProfile(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and Profile.objects.filter(user=request.user)
        )
