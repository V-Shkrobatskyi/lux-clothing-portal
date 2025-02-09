from rest_framework import serializers

from lux_clothing.serializers import OrderDetailSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="order.user", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "order",
            "session_url",
            "session_id",
            "money_to_pay",
            "user",
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    order = OrderDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "order",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentSuccessSerializer(serializers.ModelSerializer):
    order = OrderDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "order",
            "session_url",
            "session_id",
            "money_to_pay",
        )
        read_only_fields = (
            "order",
            "session_url",
            "session_id",
            "money_to_pay",
        )
