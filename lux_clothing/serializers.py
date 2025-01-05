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
        fields = ("id", "name", "color_hex", "photos")


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
