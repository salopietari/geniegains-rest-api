from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    username = models.CharField(max_length=100, blank=False, null=False)
    password = models.CharField(max_length=100, blank=False, null=False)
    unit = models.CharField(max_length=10, choices=[('metric', 'Metric'), ('imperial', 'Imperial')], blank=False, null=False)
    experience = models.CharField(max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')])
    email = models.EmailField(blank=False, null=False)

class Tracking(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Addition(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    tracking = models.ForeignKey(Tracking, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    number = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10)
    note = models.TextField(blank=True)

class Movement(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

class Exercise(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True)
    type = models.CharField(max_length=100, blank=True)
    movement = models.ManyToManyField(Movement, through='ExerciseMovementConnection')

class ExerciseMovementConnection(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    movement = models.ForeignKey(Movement, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    video = models.URLField(blank=True)
    time = models.DurationField(blank=True)

class TrainingPlan(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    movements = models.ManyToManyField(Movement)

class Goal(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    number = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    unit = models.CharField(max_length=10, choices=[('metric', 'Metric'), ('imperial', 'Imperial')])