from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Movement, TrainingPlan, TrainingPlanMovement, CustomUser

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
        fields = ('email', 'organization', 'query_quota', 'expires')
