import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import *
from backend.models import *
from backend.checks import *
from backend.exceptions import *
from backend.loghandler import *
from backend.forms import *

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = UserForm(data)
            if form.is_valid():
                form.save()
                return JsonResponse({}, status=200) # registration successful
            return JsonResponse({"error": form.errors}, status=400) # form is invalid
        
        except PasswordTooShortError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=404)

        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    else:
        return JsonResponse({}, status=400) # invalid request method

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            check_login(data)
            return JsonResponse({}, status=200) # login successful
        
        except ObjectDoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    else:
        return JsonResponse({}, status=400) # invalid request method
    
@csrf_exempt
def tracking(request):
    # create tracking
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tracking_name = data.get("tracking_name")
            user_id = data.get("user_id")
            check_add_tracking(tracking_name, user_id)
            user = User.objects.get(id=user_id)
            # create tracking
            tracking = Tracking.objects.create(
                name = tracking_name,
                user = user
            )
            return JsonResponse({}, status=200) # created tracking successfully

        except ObjectDoesNotExist as e:
            logger.error(str(e))
            logger.debug(f"data: {data if 'data' in locals() else 'Not available'}")
            return JsonResponse({}, status=404)

        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    else:
        return JsonResponse({}, status=400) # invalid request method