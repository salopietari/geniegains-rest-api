import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator

class AlphanumericUsernameValidator(RegexValidator):
    regex = r'^[a-zA-Z0-9]+$'
    message = 'Username must contain only letters and numbers.'

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=True, null=True)
    username = models.CharField(max_length=100, blank=False, null=False, unique=True, validators=[AlphanumericUsernameValidator()])
    password = models.CharField(max_length=100, blank=False, null=False)
    unit = models.CharField(max_length=10, choices=[('metric', 'Metric'), ('imperial', 'Imperial')], blank=False, null=False)
    experience = models.CharField(max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')])
    email = models.EmailField(blank=False, null=False, unique=True)

class Tracking(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now, editable=True)

class Movement(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id", null=True)
    name = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ], null=True)

class TrainingPlan(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id", null=True)
    name = models.CharField(max_length=100)
    movements = models.ManyToManyField(Movement)
    experience_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ], null=True)

class TrainingPlanMovement(models.Model):
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    
class Exercise(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    name = models.CharField(max_length=100)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    note = models.TextField(blank=True)
    type = models.CharField(max_length=100, blank=True)
    movement = models.ManyToManyField(Movement, through='ExerciseMovementConnection')

class ExerciseMovementConnection(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    reps = models.IntegerField(blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    video = models.URLField(null=True, blank=True)
    time = models.DurationField(null=True, blank=True)

class Goal(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    name = models.CharField(max_length=100)
    number = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    end = models.DateField(default=timezone.now, editable=True)
    unit = models.CharField(max_length=10)
    finished = models.BooleanField(default=False)

class Addition(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    tracking = models.ForeignKey(Tracking, on_delete=models.CASCADE, null=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    number = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10)
    note = models.TextField(blank=True)