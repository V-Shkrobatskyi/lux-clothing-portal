# Generated by Django 5.1.3 on 2024-12-10 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lux_clothing", "0012_rename_address_profile_addresses"),
    ]

    operations = [
        migrations.AddField(
            model_name="productphoto",
            name="main",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="productphoto",
            name="order",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
