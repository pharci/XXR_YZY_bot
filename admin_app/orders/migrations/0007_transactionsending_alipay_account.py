# Generated by Django 5.1.6 on 2025-02-25 20:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_remove_transactionsending_alipay_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionsending',
            name='alipay_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='orders.alipayaccounts', verbose_name='Аккаунт Alipay'),
        ),
    ]
