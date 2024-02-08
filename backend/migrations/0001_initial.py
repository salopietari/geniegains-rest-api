# Generated by Django 5.0.2 on 2024-02-08 08:02

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now_add=True)),
                ('note', models.TextField(blank=True)),
                ('type', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Movement',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Tracking',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('unit', models.CharField(choices=[('metric', 'Metric'), ('imperial', 'Imperial')], max_length=10)),
                ('experience', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')], max_length=20)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseMovementConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sets', models.IntegerField()),
                ('reps', models.IntegerField()),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('video', models.URLField(blank=True)),
                ('time', models.DurationField(blank=True)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.exercise')),
                ('movement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.movement')),
            ],
        ),
        migrations.AddField(
            model_name='exercise',
            name='movement',
            field=models.ManyToManyField(through='backend.ExerciseMovementConnection', to='backend.movement'),
        ),
        migrations.CreateModel(
            name='Addition',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('number', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.CharField(max_length=10)),
                ('note', models.TextField(blank=True)),
                ('tracking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.tracking')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingPlan',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('movements', models.ManyToManyField(to='backend.movement')),
            ],
        ),
        migrations.AddField(
            model_name='tracking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.user'),
        ),
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('number', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('unit', models.CharField(choices=[('metric', 'Metric'), ('imperial', 'Imperial')], max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.user')),
            ],
        ),
        migrations.AddField(
            model_name='exercise',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.user'),
        ),
    ]
