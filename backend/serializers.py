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

#class LoginSerializer(serializers.Serializer):
#    email = serializers.EmailField()
#    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
#
#    def validate(self, attrs):
#        email = attrs.get('email').lower()
#        password = attrs.get('password')
#
#        if not email or not password:
#            raise serializers.ValidationError("Please give both email and password.")
#
#        if not CustomUser.objects.filter(email=email).exists():
#            raise serializers.ValidationError('Invalid Credentials.')
#
#        user = authenticate(request=self.context.get('request'), email=email,
#                            password=password)
#        if not user:
#            raise serializers.ValidationError("Invalid Credentials.")
#
#        attrs['user'] = user
#        return attrs