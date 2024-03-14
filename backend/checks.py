from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from backend.models import *
from backend.exceptions import *
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from backend.loghandler import *
from django.contrib.auth.hashers import check_password
    
@csrf_exempt
def check_username(username: CustomUser.username) -> None:
    '''
    Check if username is valid and available
    '''
    try:
        # Check if username is empty
        if not username:
            raise Exception("Username is required")
        
        # Check if username contains only letters and numbers
        if not username.isalnum():
            raise Exception("Username must contain only letters and numbers.")
        
        user = CustomUser.objects.filter(username=username)

        # Check if username is available
        if user.exists():
            raise UsernameAlreadyExistsError("Username already exists")
        
    except UsernameAlreadyExistsError as e:
        raise UsernameAlreadyExistsError(e)
        
    except Exception as e:
        raise Exception(e)
    
@csrf_exempt
def check_email(email: CustomUser.username) -> None:
    '''
    Check if email is valid and available
    '''
    try:
        if not email:
            raise Exception("Email is required")
        
        user = CustomUser.objects.filter(email=email)

        if user.exists():
            raise EmailAlreadyExistsError("Email already exists")
        
    except EmailAlreadyExistsError as e:
        raise EmailAlreadyExistsError(e)
        
    except Exception as e:
        raise Exception(e)
    
def check_field_length(field_name: models.Model.__name__, field_value: str, model_class: models.Model) -> None:
    '''
    Check the length of field_value to make sure it doesn't exceed 
    the max_length of the field_name in model_class
    '''
    try:
        # Check if field_value is empty
        if not field_value:
            raise Exception(f"{field_name} is required")
        
        # Get max_length of field_name in model_class
        max_length = model_class._meta.get_field(field_name).max_length

        # Check if field_value exceeds max_length
        if len(field_value) > max_length:
            raise Exception(f"{field_name} exceeds maximum length of: {max_length}")
        
    except Exception as e:
        raise Exception(e)

@csrf_exempt
def check_user_permission(user: CustomUser, model_class: models.Model, item_id: int) -> None:
    '''
    Check that user has permission to access the item of type model_class with id item_id
    '''
    try:
        # Get the item of model_class with item_id
        item = model_class.objects.get(id=item_id)

        # Check if user is allowed to access the item
        if item.user is not None and item.user != user:
            raise Exception(f"User is not allowed to access the {model_class.__name__.lower()}")

    except Exception as e:
        raise Exception(e)