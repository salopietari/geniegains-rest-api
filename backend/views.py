import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import *
from backend.models import *
from backend.checks import *
from backend.exceptions import *
from backend.loghandler import *

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            check_registration(data=data)
            user = User.objects.create(
                username = data.get('username'),
                password = make_password(data.get('password')),
                unit = data.get('unit'),
                experience = data.get('experience'),
                email = data.get('email')
            )
            return JsonResponse({}, status=200) # registration successful

        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    else:
        return JsonResponse({}, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            check_login(username=username, password=password)
            return JsonResponse({}, status=200) # login successful

        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    else:
        return JsonResponse({}, status=400)