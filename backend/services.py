from django.contrib.auth.hashers import make_password
from .models import CustomUser

def create_user_from_data(data):
    unit = str(data.get("unit"))
    experience = str(data.get("experience"))
    # Check registration data if necessary
    # check_registration(data)
    user = CustomUser(
        username=data.get("username"),
        password=make_password(data.get("password")),
        unit=unit.lower(),
        experience=experience.lower(),
        email=data.get("email")
    )
    # Validate user fields
    user.full_clean()
    # Save user to the database
    user.save()
