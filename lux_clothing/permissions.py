from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (request.user and request.user.is_staff and request.user.is_authenticated)
            or (obj.user == request.user)
        )
