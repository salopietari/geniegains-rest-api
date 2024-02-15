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
        required_fields = ['username', 'password', 'confirmPassword', 'unit', 'experience', 'email']
        for field in required_fields:
            if not data.get(field): # check that no required field is empty
                raise ValidationError(f"{field} is required")
            
        if len(data['password']) < 5:
            raise PasswordTooShortError("Password must be at least 5 characters long")
        
        if (data['password'] != data['confirmPassword']):
            raise PasswordsDoNotMatchError("Passwords do not match")
        
        # already exists
        if User.objects.filter(username=data.get("username")).exists():
            raise ValidationError("Username already exists")

        if User.objects.filter(email=data.get("email")).exists():
            raise ValidationError("Email already exists")
        
    except PasswordTooShortError as e:
        raise PasswordTooShortError(e)
    
    except PasswordsDoNotMatchError as e:
        raise PasswordsDoNotMatchError(e)
        
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

        # if the user was not found in the db or password is incorrect raise ValidationError
        if user is None or not check_password(password, user.password):
            raise ValidationError("Invalid username and or password")
        
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(e)
        
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