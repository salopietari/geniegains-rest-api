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
                raise Exception(f"{field} is required")
            
        if len(data['password']) < 5:
            raise PasswordTooShortError("Password must be at least 5 characters long")
        
        if (data['password'] != data['confirmPassword']):
            raise PasswordsDoNotMatchError("Passwords do not match")
        
        # already exists
        if User.objects.filter(username=data.get("username")).exists():
            raise Exception("Username already exists")

        if User.objects.filter(email=data.get("email")).exists():
            raise Exception("Email already exists")
        
    except PasswordTooShortError as e:
        raise PasswordTooShortError(e)
    
    except PasswordsDoNotMatchError as e:
        raise PasswordsDoNotMatchError(e)
    
    except Exception as e: 
        raise Exception(e)
    
# used in authenticating the user
@csrf_exempt
def check_token(token):
    try:
        # check if token is empty
        if token == "":
            raise Exception("Token is empty")

        # check if token corresponds to any user
        user = User.objects.get(token=token)
    
    except Exception as e:
        raise Exception(e)
    
# used when user is logging in
@csrf_exempt
def check_login(data):
    try:
        username = data.get("username")
        password = data.get("password")

        # check if empty
        if not username:
            raise Exception("Username is required")
        if not password:
            raise Exception("Password is required")

        user = User.objects.get(username=username)
        
        if check_password(password, user.password) is not True:
            raise Exception("Wrong password")
    
    except Exception as e:
        raise Exception(e)
    
@csrf_exempt
def check_username(username):
    try:
        if not username:
            raise Exception("Username is required")
        
        if not username.isalnum():
            raise Exception("Username must contain only letters and numbers.")
        
        user = User.objects.filter(username=username)

        if user.exists():
            raise UsernameAlreadyExistsError("Username already exists")
        
    except UsernameAlreadyExistsError as e:
        raise UsernameAlreadyExistsError(e)
        
    except Exception as e:
        raise Exception(e)
    
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

@csrf_exempt
def check_user_permission(object_id: models.UUIDField, object_class: models, user: User):
    try:
        object = object_class.objects.get(uuid=object_id)

        if object.user_id_id != user.uuid:
            raise Exception(f"User is not allowed to access the object type {object_class.__name__} with id: {object_id}")
        
    except Exception as e:
        raise Exception(e)