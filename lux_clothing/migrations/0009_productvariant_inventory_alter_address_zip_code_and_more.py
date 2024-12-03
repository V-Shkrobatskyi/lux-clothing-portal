# Generated by Django 5.1.3 on 2024-12-02 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lux_clothing", "0008_alter_order_order_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="inventory",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="address",
            name="zip_code",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_phone_number",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="quantity",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="profile",
            name="default_address",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="profile",
            name="phone_number",
            field=models.PositiveIntegerField(),
        ),
    ]
