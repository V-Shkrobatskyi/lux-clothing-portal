from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
from payment.stripe_payment import create_stripe_session
from user.serializers import UserUpdateProfileSerializer


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "profile",
            "country",
            "region",
            "city",
            "street",
            "zip_code",
            "default",
        )
        read_only_fields = (
            "id",
            "profile",
        )

    def validate(self, attrs):
        data = super(AddressSerializer, self).validate(attrs=attrs)
        user = self.context["request"].user
        default_address_exist = Address.objects.filter(
            profile=user.profile,
            default=True,
        ).first()

        if attrs["default"] and default_address_exist:
            default_address_exist.default = False
            default_address_exist.save()

        return data

    def update(self, instance, validated_data):
        fields_to_update = [
            "country",
            "region",
            "city",
            "street",
            "zip_code",
            "default",
        ]

        for field in fields_to_update:
            value = validated_data.get(field, getattr(instance, field))
            setattr(instance, field, value)

        instance.save()

        return instance


class ProfileSerializer(serializers.ModelSerializer):
    user = UserUpdateProfileSerializer(many=False, partial=True)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "phone_number",
            "addresses",
        ]
        read_only_fields = (
            "id",
            "user",
            "addresses",
        )

    def validate(self, attrs):
        data = super(ProfileSerializer, self).validate(attrs=attrs)

        user = self.context["request"].user
        profile_exist = Profile.objects.filter(user=user).first()
        if profile_exist and self.instance != profile_exist:
            raise ValidationError({"error": "You already have your own profile."})

        return data

    def update(self, instance, validated_data):
        fields_to_update = [
            "phone_number",
        ]

        for field in fields_to_update:
            value = validated_data.get(field, getattr(instance, field))
            setattr(instance, field, value)

        instance.save()

        user = instance.user
        user_data = self.validated_data.get("user")
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]

        user.save()

        return instance


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "full_name",
            "phone_number",
            "addresses",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            "id",
            "name",
        )


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = (
            "id",
            "name",
        )


class ProductHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHead
        fields = (
            "id",
            "title",
            "description",
            "category",
            "brand",
            "details",
        )


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = (
            "id",
            "image",
            "order",
            "main",
        )


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = (
            "id",
            "name",
            "color_hex",
            "photos",
        )


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "color",
            "size",
            "price",
            "discount",
            "product_head",
            "inventory",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "user",
            "product",
            "quantity",
            "price",
        )
        read_only_fields = ("id", "user", "price")

    def validate(self, attrs):
        data = super(OrderItemSerializer, self).validate(attrs=attrs)

        return data

    def update(self, instance, validated_data):
        fields_to_update = [
            "product",
            "quantity",
            "price",
        ]

        for field in fields_to_update:
            value = validated_data.get(field, getattr(instance, field))
            setattr(instance, field, value)

        instance.save()

        return instance


class OrderItemListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email", read_only=True)
    product = serializers.CharField(source="product.__str__", read_only=False)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "user",
            "product",
            "quantity",
            "price",
        )


class OrderItemLimitedSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.__str__", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "product",
            "quantity",
            "price",
        )
        read_only_fields = ("__all__",)


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email", read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.context["request"].user
        active_order_items = OrderItem.objects.filter(user=user, active=True)

        self.fields["order_items"] = serializers.PrimaryKeyRelatedField(
            queryset=active_order_items,
            many=True,
        )
        self.fields["order_address"].queryset = Address.objects.filter(
            profile=user.profile, inactive=False
        ).order_by("-default")

    class Meta:
        model = Order
        fields = (
            "id",
            "created",
            "user",
            "order_address",
            "order_items",
            "order_phone_number",
            "price",
            "status",
        )
        read_only_fields = (
            "id",
            "created",
            "user",
            "order_items",
            "order_phone_number",
            "price",
            "status",
        )

    def validate(self, attrs):
        data = super(OrderSerializer, self).validate(attrs=attrs)

        user = self.context["request"].user
        attrs["order_phone_number"] = user.profile.phone_number

        price = 0
        order_items = attrs["order_items"]

        if not order_items:
            raise ValidationError(
                {"error": "Choose order items. Can't create order without products."}
            )

        for order_item in order_items:
            OrderItem.update_price(OrderItem.objects.get(id=order_item.id))
            price += order_item.price * order_item.quantity

            Product.validate_inventory(
                order_item.product.inventory,
                order_item.quantity,
                serializers.ValidationError,
            )

        attrs["price"] = price
        attrs["status"] = Order.StatusChoices.PENDING

        return data

    @atomic
    def create(self, validated_data):
        order_items = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)

        order_items_id = []
        for order_item in order_items:
            Product.sale(order_item.product, order_item.quantity)
            OrderItem.deactivate(order_item)

            order_items_id.append(order_item.id)

        order.order_items.set(order_items_id)

        request = self.context.get("request")
        create_stripe_session(
            order,
            request,
            order.price,
        )

        return order


class OrderListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email", read_only=True)
    order_items = OrderItemLimitedSerializer(many=True, read_only=True)
    order_address = serializers.CharField(
        source="order_address.__str__", read_only=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "created",
            "user",
            "order_address",
            "order_items",
            "order_phone_number",
            "price",
            "status",
        )
        read_only_fields = ("__all__",)
