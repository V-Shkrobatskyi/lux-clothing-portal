from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
from lux_clothing.permissions import (
    IsOwnerOrIsAdmin,
    IsAdminALLOrReadOnly,
    IsAddressOwnerOrIsAdmin,
    IsAdminALLOrOwnerCanPostAndGet,
    IsAdminALLOrHasProfile,
    IsAuthenticatedAndHasProfile,
)
from lux_clothing.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    AddressSerializer,
    CategorySerializer,
    BrandSerializer,
    SizeSerializer,
    ProductHeadSerializer,
    ColorSerializer,
    ProductPhotoSerializer,
    ProductSerializer,
    OrderItemSerializer,
    OrderItemListSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrIsAdmin,
    )

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
    queryset = Address.objects.filter(inactive=False)
    serializer_class = AddressSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminALLOrHasProfile,
        IsAddressOwnerOrIsAdmin,
    )

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(profile__user=self.request.user)

        return queryset.distinct()

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(profile=[profile])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        used_address = Order.objects.filter(order_address=instance)

        if instance.default:
            raise ValidationError(
                {"detail": "You can only delete addresses without 'default' option."}
            )

        if used_address:
            instance.inactive = True
            instance.save()
        else:
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class ProductHeadViewSet(viewsets.ModelViewSet):
    queryset = ProductHead.objects.all()
    serializer_class = ProductHeadSerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class ProductPhotoViewSet(viewsets.ModelViewSet):
    queryset = ProductPhoto.objects.all()
    serializer_class = ProductPhotoSerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.filter(active=True).select_related("user")
    """
    After user in Order, element of OrderItem will be seeing only for history (active=False).
    """
    serializer_class = OrderItemSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminALLOrHasProfile,
        IsOwnerOrIsAdmin,
    )

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return OrderItemListSerializer
        return OrderItemSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.active = False
        instance.save()

        return Response(
            {"detail": "Item deactivated successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminALLOrHasProfile,
        IsAdminALLOrOwnerCanPostAndGet,
    )

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        detail_serializer = OrderDetailSerializer(
            serializer.instance, context={"request": request}
        )
        headers = self.get_success_headers(detail_serializer.data)

        return Response(
            detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
