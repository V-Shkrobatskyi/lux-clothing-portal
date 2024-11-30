import os
import uuid

from django.utils.text import slugify
from colorfield.fields import ColorField
from django.conf import settings
from django.db import models


def image_file_path(instance, filename):
    extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user)}-{uuid.uuid4()}{extension}"

    return os.path.join(f"uploads/{instance.__class__.__name__.lower()}/", filename)


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
        return self.full_name


class Category(models.Model):
    name = models.CharField(max_length=63, unique=True)


class Brand(models.Model):
    name = models.CharField(max_length=63, unique=True)


class Color(models.Model):
    name = models.CharField(max_length=63, unique=True)
    color_hex = ColorField(default="#FF0000")


class Size(models.Model):
    name = models.CharField(max_length=63, unique=True)


class ProductPhoto(models.Model):
    image = models.ImageField(null=True, upload_to=image_file_path, blank=True)


class ProductVariant(models.Model):
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, related_name="product_variant"
    )
    size = models.ForeignKey(
        Size, on_delete=models.CASCADE, related_name="product_variant"
    )
    photos = models.ManyToManyField(
        ProductPhoto, blank=True, related_name="product_variant"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )


class Product(models.Model):
    title = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="product"
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="product")
    details = models.TextField()
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="product"
    )


class OrderItem(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="order_item"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_item"
    )
    quantity = models.IntegerField(max_length=12)
    price = models.DecimalField(max_digits=10, decimal_places=2)


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
    order_items = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="order"
    )
    order_phone_number = models.IntegerField(max_length=12, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=StatusChoices.choices)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return str(self.created)
