from decimal import Decimal

import stripe
from django.urls import reverse
from rest_framework.request import Request

from lux_clothing.models import Order
from lux_clothing_service import settings
from payment.models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(
    order: Order,
    request: Request,
    price: Decimal,
) -> stripe.checkout.Session:
    success_url = request.build_absolute_uri(reverse("payment:payment-success"))
    cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Payment for order number: '{order.pk}'",
                        "description": f"User '{order.user.email}' ",
                    },
                    "unit_amount": int(price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
    )

    Payment.objects.update_or_create(
        order=order,
        defaults={
            "session_url": session.url,
            "session_id": session.id,
            "money_to_pay": price,
            "status": "Pending",
        },
    )

    return session
