# Generated by Django 5.0.3 on 2024-03-31 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_conversation_qa'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='favorite',
            field=models.BooleanField(default=False),
        ),
    ]
