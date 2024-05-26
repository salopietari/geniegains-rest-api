from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Movement, TrainingPlan, TrainingPlanMovement, CustomUser
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password', 'unit', 'experience']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")

        validate_password(data['password'])
        return data

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            unit=validated_data['unit'],
            experience=validated_data['experience']
        )
        return user

# This stuff is for converting instances of our models to JSON (don't touch)
class MovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movement
        fields = '__all__'

class TrainingPlanMovementSerializer(serializers.ModelSerializer):
    movement = MovementSerializer()

    class Meta:
        model = TrainingPlanMovement
        fields = '__all__'

class TrainingPlanSerializer(serializers.ModelSerializer):
    movements = TrainingPlanMovementSerializer(many=True)

    class Meta:
        model = TrainingPlan
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
