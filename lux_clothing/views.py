from rest_framework import viewsets

from lux_clothing.models import (
    Profile,
    Address,
    Category,
    Brand,
    ProductHead,
    ProductPhoto,
    Color,
    Size,
    Product,
    OrderItem,
    Order,
)
from lux_clothing.permissions import IsOwnerOrIsAdmin
from lux_clothing.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    AddressSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrIsAdmin,)

    def get_queryset(self):
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        phone_number = self.request.query_params.get("phone_number")
        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(user__first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(user__last_name__icontains=last_name)
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        return ProfileSerializer

    def perform_create(self, serializer):
        user = self.request.user
        user.first_name = self.request.data.get("user.first_name")
        user.last_name = self.request.data.get("user.last_name")
        user.save()
        serializer.save(user=user)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(profile__user=self.request.user)

        return queryset.distinct()

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(profile=[profile])
