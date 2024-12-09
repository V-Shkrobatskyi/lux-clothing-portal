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
        )
        read_only_fields = (
            "id",
            "profile",
        )

    def update(self, instance, validated_data):
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
            "default_address",
        ]
        read_only_fields = ("id", "user", "addresses")

    def validate(self, attrs):
        data = super(ProfileSerializer, self).validate(attrs=attrs)

        user = self.context["request"].user
        profile_exist = Profile.objects.filter(user=user).first()
        if profile_exist and self.instance != profile_exist:
            raise ValidationError({"error": "You already have your own profile."})

        return data

    def update(self, instance, validated_data):
        fields_to_update = ["phone_number", "default_address"]

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
            "default_address",
        )
