from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from backend.models import *
from backend.exceptions import *
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from backend.loghandler import *
from django.contrib.auth.hashers import check_password

# used in registration
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
    
# used in authenticating the user
@csrf_exempt
def check_token(token):
    try:
        # check if token is empty
        if token == "":
            raise TokenError("Token is empty")

        # check if token corresponds to any user
        user = User.objects.get(token=token)

    except TokenError as e:
        raise TokenError(e)

    except User.DoesNotExist as e:
        raise User.DoesNotExist(e)
    
    except Exception as e:
        raise Exception(f"check_token(token) failed: {e}")
    
# used when user is logging in
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
        
        if check_password(password, user.password) is not True:
            raise ValidationError("Wrong password")
        
    except User.DoesNotExist as e:
        raise User.DoesNotExist(e)
        
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(e)
        
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e) 
    
# used to check field lengths
# example usage:
# check_field_length('name', tracking_name, Tracking)
# 1. Tracking class' field name: 'name'
# 2. Variable name: 'tracking_name'
# 3. Models.py class: 'Tracking'
def check_field_length(field_name, field_value, model_class):
    try:
        # Check if field is empty
        if not field_value:
            raise ValidationError(f"{field_name} is required")
        
        # Check max length
        max_length = model_class._meta.get_field(field_name).max_length
        if len(field_value) > max_length:
            raise ValidationError(f"{field_name} exceeds maximum length of: {max_length}")
    
    except ValidationError as e:
        raise ValidationError(e)
        
    except Exception as e:
        raise Exception(e)

# check that user is the owner of whatever they are trying to access
# example usage:
# check_user_permission(user, Tracking, item_id)
# 1. user = User object
# 2. Tracking = The class item_id corresponds to
# 3. item_id = id that corresponds to a Tracking object for example
@csrf_exempt
def check_user_permission(user, model_class, item_id):
    try:
        item = model_class.objects.get(id=item_id)

        if item.user != user:
            raise PermissionError(f"User is not allowed to access the {model_class.__name__.lower()}")

    except PermissionError as e:
        raise PermissionError(e)
    
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(f"{model_class.__name__} does not exist with id: {item_id}")

    except Exception as e:
        raise Exception(e)