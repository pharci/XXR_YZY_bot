# Generated by Django 5.1.6 on 2025-02-25 19:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alipayaccounts_alter_transactionsending_payment_card'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactionsending',
            name='payment_card',
        ),
        migrations.AddField(
            model_name='transactionsending',
            name='alipay_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='orders.alipayaccounts', verbose_name='Банковская карта'),
        ),
        migrations.AlterField(
            model_name='transactionreceiving',
            name='payment_card',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='orders.paymentcard', verbose_name='Банковская карта'),
        ),
    ]
