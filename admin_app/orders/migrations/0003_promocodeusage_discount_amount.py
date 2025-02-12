# Generated by Django 5.1.6 on 2025-02-10 17:19

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_promocodeusage_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocodeusage',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Сумма скидки'),
        ),
    ]
