# Generated by Django 5.1.6 on 2025-02-23 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0033_alter_paymentcard_options_alter_transaction_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.BigIntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='Номер ордера'),
        ),
    ]
