# Generated by Django 5.1.3 on 2024-11-30 20:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "lux_clothing",
            "0004_remove_orderitem_product_remove_product_variant_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="productvariant",
            old_name="variant",
            new_name="product",
        ),
    ]
