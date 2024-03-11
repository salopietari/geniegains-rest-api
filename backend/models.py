import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser

class AlphanumericUsernameValidator(RegexValidator):
    regex = r'^[a-zA-Z0-9]+$'
    message = 'Username must contain only letters and numbers.'

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #token = models.CharField(max_length=255, default=uuid.uuid4, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True, validators=[AlphanumericUsernameValidator()])
    password = models.CharField(max_length=100, blank=False, null=False)
    unit = models.CharField(max_length=10, choices=[('metric', 'Metric'), ('imperial', 'Imperial')], blank=False, null=False)
    experience = models.CharField(max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')], blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    USERNAME_FIELD = 'username' # use email for authentication
    REQUIRED_FIELDS = ['username', 'email', 'password', 'unit', 'experience']

class Tracking(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now, editable=True)

class Movement(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id", null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    experience_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ], blank=True, null=True)
    category = models.CharField(choices=[
        ('triceps', 'Triceps'),
        ('biceps', 'Biceps'),
        ('shoulders', 'Shoulders'),
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('legs', 'Legs'),
        ('core', 'Core'),
        ('other', 'Other')
    ], default="other")

class TrainingPlan(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id", null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    movements = models.ManyToManyField(Movement)
    experience_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ], blank=True, null=True)

class TrainingPlanMovement(models.Model):
    training_plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    
class Exercise(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    name = models.CharField(max_length=100, blank=False, null=False)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    note = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    movement = models.ManyToManyField(Movement, through='ExerciseMovementConnection')

class ExerciseMovementConnection(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    reps = models.IntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    video = models.URLField(null=True, blank=True)
    time = models.DurationField(null=True, blank=True)

class Goal(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    name = models.CharField(max_length=100, blank=False, null=False)
    number = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    end = models.DateField(default=timezone.now, editable=True)
    unit = models.CharField(max_length=10)
    finished = models.BooleanField(default=False)

class Addition(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="id")
    tracking = models.ForeignKey(Tracking, on_delete=models.CASCADE, blank=True, null=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    number = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    unit = models.CharField(max_length=10)
    note = models.TextField(blank=True, null=True)