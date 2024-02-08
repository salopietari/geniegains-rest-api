from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from backend.models import *
from backend.exceptions import *
from django.core.exceptions import ValidationError, ObjectDoesNotExist
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
def check_login(data):
    try:
        username = data.get("username")
        password = data.get("password")

        # check if empty
        if not username:
            raise ValidationError("Username is required")
        if not password:
            raise ValidationError("Password is required")
        
        user = User.objects.get(username=username)

        # if the username or password are incorrect raise ValidationError
        if user is None or not check_password(password, user.password):
            raise ValidationError("Invalid username and or password")
        
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e) 
    
@csrf_exempt
def check_add_tracking(tracking_name, user_id):
    try:

        # check if empty
        if not tracking_name:
            raise ValidationError("Tracking_name is required")
        if not user_id:
            raise ValidationError("User_id is required")
            
        # check max length
        if len(tracking_name) > 100:
            raise ValidationError(f"Tracking_name exceeds maximum length of: {Tracking._meta.get_field('name').max_length}")

        # check if user_id is in db
        if not User.objects.filter(id=user_id).exists():
            raise ObjectDoesNotExist("User_id not found in database")
        
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(e)
            
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e)