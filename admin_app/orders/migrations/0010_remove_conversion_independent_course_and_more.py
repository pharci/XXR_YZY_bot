# Generated by Django 5.1.6 on 2025-03-01 20:12

import django_jsonform.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_alter_conversion_independent_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversion',
            name='independent_course',
        ),
        migrations.AddField(
            model_name='conversion',
            name='independent_grades',
            field=django_jsonform.models.fields.JSONField(default=0, verbose_name='Градация самостоятельного обмена'),
            preserve_default=False,
        ),
    ]
