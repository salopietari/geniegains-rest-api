from rest_framework import serializers
from .models import TrainingPlan, TrainingPlanMovement, Movement

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
