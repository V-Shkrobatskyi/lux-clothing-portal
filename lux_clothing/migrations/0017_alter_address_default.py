# Generated by Django 5.1.3 on 2024-12-30 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lux_clothing", "0016_address_default_alter_order_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="default",
            field=models.BooleanField(default=False),
        ),
    ]
