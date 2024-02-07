from django.views.decorators.csrf import csrf_exempt
from backend.models import *
from backend.exceptions import *
from django.core.exceptions import ValidationError

@csrf_exempt
def check_registration(data):
    try:
        username = data.get('username')
        password = data.get('password')
        unit = data.get('unit')
        experience = data.get('experience')
        email = data.get('email')

        if not username or not password or not unit or not experience or not email:
            raise ValidationError("All fields are required")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e)