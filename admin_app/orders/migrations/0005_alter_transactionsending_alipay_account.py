# Generated by Django 5.1.6 on 2025-02-25 19:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_transactionsending_payment_card_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionsending',
            name='alipay_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='orders.alipayaccounts', verbose_name='Аккаунт Alipay'),
        ),
    ]
