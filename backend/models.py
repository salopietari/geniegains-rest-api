import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, UserManager,BaseUserManager, PermissionsMixin, Group, Permission

class AlphanumericUsernameValidator(RegexValidator):
    regex = r'^[a-zA-Z0-9]+$'
    message = 'Username must contain only letters and numbers.'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = CustomUser.objects.create(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff = True")

        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser = True")
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True, validators=[AlphanumericUsernameValidator()])
    password = models.CharField(max_length=100, blank=False, null=False)
    unit = models.CharField(default="metric", max_length=10, choices=[('metric', 'Metric'), ('imperial', 'Imperial')], blank=False, null=False)
    experience = models.CharField(default="beginner", max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')], blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    is_superuser = models.BooleanField(default=False, editable=False)
    is_staff = models.BooleanField(default=False, editable=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now, editable=True)
    query_quota = models.IntegerField(default=10, blank=False, null=False, validators=[MaxValueValidator(10)])
    last_query = models.DateTimeField(default=timezone.now, editable=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        permissions = (("can_approve_posts", "Can approve posts"),)

    groups = models.ManyToManyField(Group, blank=True, related_name='user_groups')
    
    # specify a unique related_name for the user_permissions field
    # in order to prevent clash with the auth.User model
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='user_permissions_customuser'
    )

    def __str__(self):
        return self.email

class Tracking(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now, editable=True)

class Movement(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id", null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id", null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
    name = models.CharField(max_length=100, blank=False, null=False)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    note = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    movement = models.ManyToManyField(Movement, through='ExerciseMovementConnection')

class ExerciseMovementConnection(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
    name = models.CharField(max_length=100, blank=False, null=False)
    number = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    end = models.DateField(default=timezone.now, editable=True)
    unit = models.CharField(max_length=10)
    finished = models.BooleanField(default=False)

class Addition(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
    tracking = models.ForeignKey(Tracking, on_delete=models.CASCADE, blank=True, null=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    number = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    note = models.TextField(blank=True, null=True)

class Conversation(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    title = models.CharField(max_length=100, blank=False, null=False)

class QA(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
    created = models.DateField(default=timezone.now, editable=False)
    updated = models.DateField(default=timezone.now, editable=True)
    question = models.TextField(max_length=100,blank=False, null=False)
    answer = models.TextField(max_length=1000, blank=True, null=True)