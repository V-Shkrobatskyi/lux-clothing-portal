# Generated by Django 5.1.3 on 2024-12-02 20:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "lux_clothing",
            "0009_productvariant_inventory_alter_address_zip_code_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="product_variant",
        ),
        migrations.RemoveField(
            model_name="product",
            name="brand",
        ),
        migrations.RemoveField(
            model_name="product",
            name="category",
        ),
        migrations.RemoveField(
            model_name="product",
            name="description",
        ),
        migrations.RemoveField(
            model_name="product",
            name="details",
        ),
        migrations.RemoveField(
            model_name="product",
            name="title",
        ),
        migrations.AddField(
            model_name="color",
            name="photos",
            field=models.ManyToManyField(
                related_name="color", to="lux_clothing.productphoto"
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_item",
                to="lux_clothing.product",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="color",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product",
                to="lux_clothing.color",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="discount",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="inventory",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="size",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product",
                to="lux_clothing.size",
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="ProductHead",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=63, unique=True)),
                ("description", models.CharField(max_length=255)),
                ("details", models.TextField()),
                (
                    "brand",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_head",
                        to="lux_clothing.brand",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_head",
                        to="lux_clothing.category",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="product",
            name="product_head",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product",
                to="lux_clothing.producthead",
            ),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="ProductVariant",
        ),
    ]
