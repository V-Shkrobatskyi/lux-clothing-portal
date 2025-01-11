import stripe
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

# from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from lux_clothing.models import Order
from lux_clothing.serializers import OrderSerializer

from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentSuccessSerializer,
)
from payment.stripe_payment import create_stripe_session


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("order")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        if not self.request.user.is_staff:
            return self.queryset.filter(order__user=user)

        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        if self.action == "success":
            return PaymentSuccessSerializer

        return PaymentSerializer

    # @extend_schema(
    #     description="List of user's payments. Admin have access to all users payments.",
    # )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # @extend_schema(
    #     description="Check stripe payment session status. "
    #     "If status is ok, then update payment instance "
    #     "and send notification message to telegram chat bot.",
    # )
    @action(methods=["GET"], url_path="success", detail=False)
    def success(self, request, session_id=None):
        session_id = request.query_params.get("session_id", None)
        if not session_id:
            return Response(
                {"message": "Payment parameter not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment = get_object_or_404(
            Payment,
            session_id=request.GET.get("session_id"),
            status=Payment.StatusChoices.PENDING,
        )
        session = stripe.checkout.Session.retrieve(session_id)

        if session.get("payment_status") == "paid":
            data = {
                "status": Payment.StatusChoices.PAID,
            }
            serializer = self.get_serializer(payment, data=data)

            if serializer.is_valid():
                serializer.save()

                payment.order.status = Order.StatusChoices.PAID
                payment.order.save()

                return HttpResponseRedirect(
                    reverse("lux_clothing:order-detail", args=[payment.order.id])
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_404_NOT_FOUND)

    # @extend_schema(
    #     description="If user cancel payment during payment session, "
    #     "show message about available payment session "
    #     "for only 24h.",
    # )
    @action(methods=["GET"], url_path="cancel", detail=False)
    def cancel(self, request):
        raise ValidationError(
            "Payment can be paid a bit later, but the session is available for only 24h."
        )

    # @extend_schema(
    #     description="If the payment session is expired user can renew it. "
    #     "System update fields in payment instance: session_id, session_url and status.",
    # )
    @action(
        detail=False,
        methods=["GET"],
        url_path="renew",
    )
    @atomic
    def renew_session(self, request, pk=None):
        user = request.user
        payment = Payment.objects.filter(
            status=Payment.StatusChoices.EXPIRED, order__user=user
        ).first()

        if payment:
            new_session = create_stripe_session(
                payment.order,
                request,
                payment.money_to_pay,
            )
            payment.session_url = new_session.url
            payment.session_id = new_session.id
            payment.status = Payment.StatusChoices.PENDING
            payment.save()

            order_data = OrderSerializer(payment.order).data
            return Response(
                {
                    "detail:": "Payment session renewed.",
                    "id": payment.id,
                    "new status": payment.status,
                    "money to pay": payment.money_to_pay,
                    "new session id": payment.session_id,
                    "new session url": payment.session_url,
                    "order": order_data,
                }
            )
        return Response(
            {"detail": "There is no expired payment session."},
            status=status.HTTP_404_NOT_FOUND,
        )
