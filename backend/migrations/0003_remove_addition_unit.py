# Generated by Django 5.0.3 on 2024-03-14 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_customuser_managers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addition',
            name='unit',
        ),
    ]
