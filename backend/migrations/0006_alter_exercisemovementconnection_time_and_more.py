# Generated by Django 4.2.6 on 2024-02-22 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_remove_exercisemovementconnection_sets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercisemovementconnection',
            name='time',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exercisemovementconnection',
            name='video',
            field=models.URLField(blank=True, null=True),
        ),
    ]