# Generated by Django 5.1.3 on 2025-01-05 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lux_clothing", "0019_remove_profile_addresses_profile_addresses"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="inactive",
            field=models.BooleanField(default=False),
        ),
    ]
