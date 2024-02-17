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
def check_login(data, token):
    try:
        user = User.objects.get(token=token)
        username = data.get("username")
        password = data.get("password")

        # check if empty
        if not username:
            raise ValidationError("Username is required")
        if not password:
            raise ValidationError("Password is required")
        
        # check that the token matching username is the same as in the given data
        if str(username) != str(user.username):
            logger.error(f"token: {token if 'token' in locals() else 'Not Available'}")
            logger.error(f"username: {username if 'username' in locals() else 'Not Available'}")
            raise ValidationError("Token doesn't match the username that was given in data")

        # if the user was not found in the db or password is incorrect raise ValidationError
        if user is None or not check_password(password, user.password):
            raise ValidationError("Invalid username and or password")  
    
    except TokenError as e:
        raise TokenError(e)
    
    except User.DoesNotExist as e:
        raise User.DoesNotExist(e)
        
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(e)
        
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e) 
    
# used when creating a tracking
@csrf_exempt
def check_add_tracking(tracking_name):
    try:

        # check if empty
        if not tracking_name:
            raise ValidationError("Tracking_name is required")
            
        # check max length
        if len(tracking_name) > Tracking._meta.get_field('name').max_length:
            raise ValidationError(f"Tracking_name exceeds maximum length of: {Tracking._meta.get_field('name').max_length}")
        
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(e)
            
    except ValidationError as e:
        raise ValidationError(e)
    
    except Exception as e:
        raise Exception(e)
    
# check that the user trying to access tracking actually is the owner
@csrf_exempt
def check_user_tracking(user, tracking_id):
    try:
        tracking = Tracking.objects.get(id=tracking_id)

        if tracking.user != user:
            raise PermissionError("User is not allowed to access the tracking")

    except PermissionError as e:
        raise PermissionError(e)
    
    except Tracking.DoesNotExist as e:
        raise Tracking.DoesNotExist(e)

    except Exception as e:
        raise Exception(e)