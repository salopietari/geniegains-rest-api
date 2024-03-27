# Generated by Django 5.0.3 on 2024-03-26 14:35

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_query',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='query_quota',
            field=models.IntegerField(default=10, validators=[django.core.validators.MaxValueValidator(10)]),
        ),
    ]