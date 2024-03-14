from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from backend.models import *
from backend.exceptions import *
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from backend.loghandler import *
from django.contrib.auth.hashers import check_password
    
@csrf_exempt
def check_username(username):
    try:
        if not username:
            raise Exception("Username is required")
        
        if not username.isalnum():
            raise Exception("Username must contain only letters and numbers.")
        
        user = CustomUser.objects.filter(username=username)

        if user.exists():
            raise UsernameAlreadyExistsError("Username already exists")
        
    except UsernameAlreadyExistsError as e:
        raise UsernameAlreadyExistsError(e)
        
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
            raise Exception(f"{field_name} is required")
        
        # Check max length
        max_length = model_class._meta.get_field(field_name).max_length
        if len(field_value) > max_length:
            raise Exception(f"{field_name} exceeds maximum length of: {max_length}")
        
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

        if item.user is not None and item.user != user:
            raise Exception(f"User is not allowed to access the {model_class.__name__.lower()}")

    except Exception as e:
        raise Exception(e)