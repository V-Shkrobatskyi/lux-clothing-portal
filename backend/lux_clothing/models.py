import os
import uuid
from decimal import Decimal

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property


def image_file_path(instance, filename):
    extension = os.path.splitext(filename)
    filename = f"{uuid.uuid4()}{extension}"

    return os.path.join(f"uploads/{instance.__class__.__name__.lower()}/", filename)


class Address(models.Model):
    objects = models.Manager()
    country = models.CharField(max_length=63)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=63)
    street = models.CharField(max_length=255)
    zip_code = models.PositiveIntegerField()
    default = models.BooleanField(default=False)
    inactive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.zip_code}, {self.country}, {self.region}, {self.city}, {self.street}"


class Category(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class ForWhom(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class Style(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class ProductHead(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="product_heads"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="product_heads"
    )
    for_whom = models.ForeignKey(
        ForWhom, on_delete=models.CASCADE, related_name="product_heads"
    )
    style = models.ForeignKey(
        Style, on_delete=models.CASCADE, related_name="product_heads"
    )
    details = models.TextField()

    @cached_property
    def cached_str(self):
        return f"{self.category}, {self.brand}, {self.title}"

    def __str__(self):
        return self.cached_str


class ProductPhoto(models.Model):
    objects = models.Manager()
    image = models.ImageField(null=True, upload_to=image_file_path, blank=True)
    order = models.PositiveIntegerField(default=0)
    main = models.BooleanField(default=False)


class Color(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=63, unique=True)
    color_hex = ColorField(default="#FF0000")
    photos = models.ManyToManyField(
        ProductPhoto, related_name="color", symmetrical=False
    )

    def __str__(self):
        return self.name


class Size(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    objects = models.Manager()
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="products")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    product_head = models.ForeignKey(
        ProductHead, on_delete=models.CASCADE, related_name="products"
    )
    inventory = models.PositiveIntegerField(default=0)

    @cached_property
    def cached_str(self):
        return (
            f"{self.product_head}, {self.color}, {self.size}, "
            f"price: {self.price}, discount: {self.discount}, inventory: {self.inventory}"
        )

    def __str__(self):
        return self.cached_str

    @staticmethod
    def validate_new_product(instance, error_to_raise) -> None:
        product_exist = (
            Product.objects.filter(
                product_head=instance.product_head,
                size=instance.size,
                color=instance.color,
            )
            .exclude(pk=instance.pk)
            .first()
        )
        if product_exist:
            raise error_to_raise(
                {
                    "product": f"You can't add new product, it already exist with parameters: "
                    f"product_head = '{instance.product_head.title}', size = '{instance.size}' "
                    f"and color = '{instance.color}'."
                }
            )

    @staticmethod
    def validate_inventory(inventory, quantity, error_to_raise) -> None:
        if inventory == 0:
            raise error_to_raise(
                {"product": "You can't buy this product, its inventory is zero."}
            )

        if inventory < quantity:
            raise error_to_raise(
                {
                    "product": f"You can't buying this product in quantity '{quantity}', "
                    f"its inventory will run out of zero. Inventory is '{inventory}'."
                }
            )

    @staticmethod
    def sale(instance, quantity) -> None:
        instance.inventory -= quantity
        instance.save()

    def clean(self) -> None:
        if self.pk is None:
            Product.validate_new_product(self, ValueError)

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)


class OrderItem(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    @cached_property
    def cached_str(self):
        return (
            f"id: {self.pk}, product: {self.product.product_head.title}, brand: {self.product.product_head.brand}, "
            f"color: {self.product.color}, size: {self.product.size}, "
            f"quantity: {self.quantity}, price: {self.item_price}"
        )

    def __str__(self):
        return self.cached_str

    @property
    def item_price(self) -> Decimal:
        return Decimal(
            (
                self.product.price
                - self.product.price * Decimal(self.product.discount / 100)
            )
            * self.quantity
        )

    @staticmethod
    def deactivate(instance) -> None:
        instance.active = False
        instance.save()

    def save(self, *args, **kwargs) -> None:
        return super().save(*args, **kwargs)


class Order(models.Model):
    objects = models.Manager()

    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"
        EXPIRED = "Expired"
        CANCELED = "Canceled"
        PROCESSING = "Processing"
        COMPLETED = "Completed"

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="orders"
    )
    order_address = models.ForeignKey(
        Address, on_delete=models.DO_NOTHING, related_name="orders"
    )
    order_items = models.ManyToManyField(
        OrderItem, related_name="orders", symmetrical=False
    )
    order_phone_number = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.pk}, {self.created.__format__('%Y-%m-%d %H:%M:%S')}, {self.user}, {self.status}, {self.price}"


class Profile(models.Model):
    objects = models.Manager()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.CharField(max_length=12, unique=True)
    addresses = models.ManyToManyField(
        Address, related_name="profiles", symmetrical=False
    )
    favorite_products = models.ManyToManyField(
        Product, related_name="profiles", symmetrical=False, blank=True
    )

    @property
    def full_name(self) -> str:
        return str(self.user.full_name)

    def __str__(self):
        return self.full_name
