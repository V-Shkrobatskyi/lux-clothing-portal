from django.contrib import admin

from .models import (
    Address,
    Profile,
    Order,
    OrderItem,
    Product,
    ProductHead,
    Category,
    Brand,
    ForWhom,
    Style,
    Color,
    Size,
    ProductPhoto,
)

admin.site.register(Address)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(ProductHead)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ForWhom)
admin.site.register(Style)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(ProductPhoto)
