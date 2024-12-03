import os
import uuid

from django.utils.text import slugify
from colorfield.fields import ColorField
from django.conf import settings
from django.db import models


def image_file_path(instance, filename):
    extension = os.path.splitext(filename)
    filename = f"{uuid.uuid4()}{extension}"

    return os.path.join(f"uploads/{instance.__class__.__name__.lower()}/", filename)


class Address(models.Model):
    country = models.CharField(max_length=63)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=63)
    street = models.CharField(max_length=255)
    zip_code = models.PositiveIntegerField()


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.PositiveIntegerField()
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="profile"
    )
    default_address = models.PositiveIntegerField()  # one of profile Address id

    @property
    def full_name(self) -> str:
        return str(self.user.full_name)

    def __str__(self):
        return self.full_name


class Category(models.Model):
    name = models.CharField(max_length=63, unique=True)


class Brand(models.Model):
    name = models.CharField(max_length=63, unique=True)

class ProductHead(models.Model):
    title = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="product_head"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="product_head"
    )
    details = models.TextField()


class ProductPhoto(models.Model):
    image = models.ImageField(null=True, upload_to=image_file_path, blank=True)


class Color(models.Model):
    name = models.CharField(max_length=63, unique=True)
    color_hex = ColorField(default="#FF0000")
    photos = models.ManyToManyField(
        ProductPhoto, related_name="color", symmetrical=False
    )


class Size(models.Model):
    name = models.CharField(max_length=63, unique=True)


class ProductPhoto(models.Model):
    image = models.ImageField(null=True, upload_to=image_file_path, blank=True)

class Product(models.Model):
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="product")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="product")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    product_head = models.ForeignKey(
        ProductHead, on_delete=models.CASCADE, related_name="product"
    )
    inventory = models.PositiveIntegerField(default=0)


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
    quantity = models.PositiveIntegerField()
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
    order_items = models.ManyToManyField(
        OrderItem, related_name="order", symmetrical=False
    )
    order_phone_number = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=StatusChoices.choices, default=StatusChoices.CART
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return str(self.created)
