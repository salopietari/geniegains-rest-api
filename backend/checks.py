from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from backend.models import *
from backend.exceptions import *
from django.core.exceptions import ValidationError
from backend.loghandler import *
from django.contrib.auth.hashers import check_password

@csrf_exempt
def check_registration(data):
    try:
        username = data.get('username')
        password = data.get('password')
        unit = data.get('unit')
        experience = data.get('experience')
        email = data.get('email')

        # empty
        if not username:
            raise ValidationError("Username is required")
        if not password:
            raise ValidationError("Password is required")
        if not unit:
            raise ValidationError("Unit is required")
        if not experience:
            raise ValidationError("Experience is required")
        if not email:
            raise ValidationError("Email is required")
        
        # already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e)
    
@csrf_exempt
def check_login(username, password):
    try:
        # empty
        if not username:

            raise ValidationError("Username is required")
        if not password:
            raise ValidationError("Password is required")
        
        user = User.objects.get(username=username)

        # if the username or password are incorrect raise ValidationError
        if user is None or not check_password(password, user.password):
            logger.debug(f"Username: {username} \nPassword: {password}")
            raise ValidationError("Invalid username and or password")
        
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e) 