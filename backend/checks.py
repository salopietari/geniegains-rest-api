from django.views.decorators.csrf import csrf_exempt
from backend.models import CustomUser, models
from backend.exceptions import UsernameAlreadyExistsError, EmailAlreadyExistsError, QueryQuotaExceededError, PasswordsDoNotMatchError

@csrf_exempt
def check_register(data: dict) -> None:
    try:
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')
        unit = data.get('unit')
        experience = data.get('experience')

        # Check if all fields are present
        if not username or not email or not password or not confirm_password or not unit or not experience:
            raise Exception("All fields are required")
        
        # Check if password and confirm password match
        if password != confirm_password:
            raise PasswordsDoNotMatchError("Passwords do not match")
        
        # Check if username and email are valid and available
        check_username(username)
        check_email(email)
    except Exception as e:
        raise Exception(e)

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

@csrf_exempt
def check_user_permission(user: CustomUser, model_class: models.Model, object_id: int) -> None:
    '''
    Check that user has permission to access the item of type model_class with id object_id
    '''
    try:
        # Get the item of model_class with item_id
        object = model_class.objects.get(id=object_id)

        # Check if user is allowed to access the item
        if object.user is not None and object.user != user:
            raise Exception(f"User is not allowed to access the {model_class.__name__.lower()}")

    except Exception as e:
        raise Exception(e)
    
@csrf_exempt
def check_user_query_quota(user: CustomUser) -> None:
    from backend.services import reset_query_quota
    '''
    Check if user has queries left for today.
    If no queries left, raise QueryQuotaExceededError
    '''
    try:
        reset_query_quota(user)
        if user.query_quota < 1:
            raise QueryQuotaExceededError("Query quota exceeded")
        
    except QueryQuotaExceededError as e:
        raise QueryQuotaExceededError(e)
    
    except Exception as e:
        raise Exception(e)