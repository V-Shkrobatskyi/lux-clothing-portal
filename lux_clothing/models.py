import os
import uuid

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models


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


class Profile(models.Model):
    objects = models.Manager()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.PositiveIntegerField()
    addresses = models.ManyToManyField(
        Address, related_name="profile", symmetrical=False
    )

    @property
    def full_name(self) -> str:
        return str(self.user.full_name)

    def __str__(self):
        return self.full_name


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


class ProductHead(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="product_head"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="product_head"
    )
    details = models.TextField()

    def __str__(self):
        return f"{self.category}, {self.brand}, {self.title}"


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

    def __str__(self):
        return f"{self.product_head}, {self.color}, {self.size}, {self.price}, {self.discount}"

    @staticmethod
    def validate_new_product(instance, error_to_raise) -> None:
        if (
            Product.objects.filter(
                product_head=instance.product_head,
                size=instance.size,
                color=instance.color,
            ).count()
            != 0
        ):
            raise error_to_raise(
                {
                    "info": f"You can't add new product, it already exist with parameters: "
                    f"product_head = '{instance.product_head.title}', size = '{instance.size}' "
                    f"and color = '{instance.color}'."
                }
            )

    def clean(self) -> None:
        Product.validate_new_product(self, ValueError)

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)


class OrderItem(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_item"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_item"
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"product: '{self.product}', quantity: {self.quantity}, total price: {self.quantity * self.product.price}"

    @staticmethod
    def update_actual_price(instance) -> None:
        updated_total_price = instance.product.price * instance.quantity
        if updated_total_price != instance.price:
            instance.price = updated_total_price

    def clean(self) -> None:
        OrderItem.update_actual_price(self)

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)


class Order(models.Model):
    objects = models.Manager()

    class StatusChoices(models.TextChoices):
        CART = "Cart"
        PENDING = "Pending"
        PAID = "Paid"
        EXPIRED = "Expired"
        CANCELED = "Canceled"
        PROCESSING = "Processing"
        COMPLETED = "Completed"

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order"
    )
    order_address = models.ForeignKey(
        Address, on_delete=models.DO_NOTHING, related_name="order"
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
        return f"{self.created.__format__('%Y-%m-%d %H:%M:%S')}, {self.profile}, {self.status}, {self.price}"
