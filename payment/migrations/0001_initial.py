# Generated by Django 5.1.3 on 2025-01-08 20:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("lux_clothing", "0020_address_inactive"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Paid", "Paid"),
                            ("Expired", "Expired"),
                        ],
                        max_length=15,
                    ),
                ),
                ("session_url", models.URLField(max_length=500)),
                ("session_id", models.CharField(max_length=255)),
                ("money_to_pay", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="lux_clothing.order",
                    ),
                ),
            ],
        ),
    ]