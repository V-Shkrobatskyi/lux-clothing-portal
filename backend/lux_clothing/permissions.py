from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user


class IsAddressOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff
            or obj.profiles.filter(id=request.user.profile.id).exists()
        )


class IsAdminALLOrOwnerCanPostAndGet(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (
            obj.user == request.user and request.method in ["POST", "GET"]
        )


class IsAdminALLOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS


class IsAdminALLOrHasProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or hasattr(request.user, "profile")


class HasProfile(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "profile")


class IsAuthenticatedAndHasProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "profile")
