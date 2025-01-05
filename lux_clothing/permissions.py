from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_staff or obj.user == request.user)


class IsAddressOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_staff or obj in request.user.profile.addresses.all()
        )


class IsAdminALLOrIsOnlyPostOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_staff
            or (obj.user == request.user and request.method == "POST")
        )


class IsAdminALLOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_staff or request.method in SAFE_METHODS)
