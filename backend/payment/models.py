from django.db import models

from lux_clothing.models import Order


class Payment(models.Model):
    objects = models.Manager()

    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"
        EXPIRED = "Expired"

    status = models.CharField(max_length=15, choices=StatusChoices.choices)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Payment id {self.pk}, status {self.status} by user {self.order.user}"
