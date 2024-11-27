from django.conf import settings
from django.db import models


class Address(models.Model):
    country = models.CharField(max_length=63)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=63)
    street = models.CharField(max_length=255)
    zip_code = models.IntegerField()


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.IntegerField(max_length=12, null=True, blank=True)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="profile"
    )
    default_address = models.OneToOneField(
        Address,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    @property
    def full_name(self) -> str:
        return str(self.user.full_name)

    def __str__(self):
        return str(self.user.full_name)


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        CART = "Cart"
        PENDING = "Pending"
        PAID = "Paid"
        EXPIRED = "Expired"
        CANCELED = "Canceled"
        PROCESSING = "Processing"
        COMPLETED = "Completed"

    created = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="order")
    order_address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="profile"
    )
    # order_items =
    order_phone_number = models.IntegerField(max_length=12, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=StatusChoices.choices)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return str(self.created)
