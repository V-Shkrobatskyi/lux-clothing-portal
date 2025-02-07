from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
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
    ForWhom,
    Style,
)
from lux_clothing.permissions import (
    IsOwnerOrIsAdmin,
    IsAdminALLOrReadOnly,
    IsAddressOwnerOrIsAdmin,
    IsAdminALLOrOwnerCanPostAndGet,
    HasProfile,
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
    ForWhomSerializer,
    StyleSerializer,
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

    @extend_schema(
        description="Create new profile.",
    )
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
        HasProfile,
        IsAddressOwnerOrIsAdmin,
    )

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(profile__user=self.request.user)

        return queryset.distinct()

    @extend_schema(
        description="Add many addresses to profile."
        "Mark only one with 'default' option.",
    )
    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(profile=[profile])

    @extend_schema(
        description="Delete only addresses without 'default' option.",
    )
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


class ForWhomViewSet(viewsets.ModelViewSet):
    queryset = ForWhom.objects.all()
    serializer_class = ForWhomSerializer
    permission_classes = (IsAdminALLOrReadOnly,)


class StyleViewSet(viewsets.ModelViewSet):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer
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

    def get_queryset(self):
        for_whom = self.request.query_params.get("for_whom")
        category = self.request.query_params.get("category")
        brand = self.request.query_params.get("brand")
        style = self.request.query_params.get("style")
        size = self.request.query_params.get("size")
        color = self.request.query_params.get("color")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        queryset = self.queryset

        if for_whom:
            queryset = queryset.filter(product_head__for_whom__name__iexact=for_whom)
        if category:
            queryset = queryset.filter(product_head__category__name__iexact=category)
        if brand:
            queryset = queryset.filter(product_head__brand__name__iexact=brand)
        if style:
            queryset = queryset.filter(product_head__style__name__iexact=style)
        if size:
            queryset = queryset.filter(size__name__iexact=size)
        if color:
            queryset = queryset.filter(color__name__iexact=color)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset.distinct()

    @extend_schema(
        description="Add/Remove product from favorites.",
    )
    @action(
        methods=["GET"], detail=True, permission_classes=[IsAuthenticated, HasProfile]
    )
    def favorite(self, request, pk=None):
        product = self.get_object()
        profile = Profile.objects.get(user=request.user)

        favorite_exists = Profile.objects.filter(
            user=request.user, favorite_products__id=pk
        ).exists()

        if favorite_exists:
            profile.favorite_products.remove(product)
            profile.save()

            return Response(
                {
                    "detail": f"Product '{product}' successfully removed from user profile '{profile}' favorite list."
                },
                status=status.HTTP_200_OK,
            )

        profile.favorite_products.add(product)
        profile.save()

        return Response(
            {
                "detail": f"Product '{product}' successfully added to user profile '{profile}' favorite list."
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                description="Filter by title field of 'product head' (ex. ?name=suit).",
                required=False,
            ),
            OpenApiParameter(
                name="for_whom",
                type=OpenApiTypes.STR,
                description="Filter by for_whom field of 'product head' (ex. ?for_whom=men).",
                required=False,
            ),
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                description="Filter by category field of 'product head' (ex. ?category=Hoodies).",
                required=False,
            ),
            OpenApiParameter(
                name="brand",
                type=OpenApiTypes.STR,
                description="Filter by brand field of 'product head' (ex. ?brand=Lacoste).",
                required=False,
            ),
            OpenApiParameter(
                name="style",
                type=OpenApiTypes.STR,
                description="Filter by style field of 'product head' (ex. ?style=Urban).",
                required=False,
            ),
            OpenApiParameter(
                name="size",
                type=OpenApiTypes.STR,
                description="Filter by product size (ex. ?size=L).",
                required=False,
            ),
            OpenApiParameter(
                name="color",
                type=OpenApiTypes.STR,
                description="Filter by product color (ex. ?color=black).",
                required=False,
            ),
            OpenApiParameter(
                name="min_price",
                type=OpenApiTypes.STR,
                description="Filter by product minimum price (ex. ?min_price=50).",
                required=False,
            ),
            OpenApiParameter(
                name="max_price",
                type=OpenApiTypes.STR,
                description="Filter by product maximum price (ex. ?max_price=100).",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    After user make Order, element of OrderItem will be seeing only for Order history (active=False).
    """

    queryset = OrderItem.objects.filter(active=True).select_related("user")
    """
    After user in Order, element of OrderItem will be seeing only for history (active=False).
    """
    serializer_class = OrderItemSerializer
    permission_classes = (
        IsAuthenticated,
        HasProfile,
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

    @extend_schema(
        description="Add quantity of some product to one record of OrderItem.",
    )
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    @extend_schema(
        description="Remove OrderItem.",
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.active = False
        instance.save()

        return Response(
            {"detail": "Item deactivated successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @extend_schema(
        description="List of user OrderItem, like his cart.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (
        IsAuthenticated,
        HasProfile,
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

    @extend_schema(
        description="Create an order from list of OrderItem."
        "User can choose what OrderItems he wants in order.",
    )
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @extend_schema(
        description="Product price and amount will be validate and update.",
    )
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
