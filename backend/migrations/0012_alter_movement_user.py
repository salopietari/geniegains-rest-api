# Generated by Django 4.2.6 on 2024-03-07 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0011_movement_experience_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movement',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.user'),
        ),
    ]