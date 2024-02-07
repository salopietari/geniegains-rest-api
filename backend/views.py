import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from backend.models import *
from django.contrib.auth.hashers import *
from backend.checks import *
from backend.exceptions import *

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            check_registration(data)
            user = User.objects.create(
                username = data.get('username'),
                password = make_password(data.get('password')),
                unit = data.get('unit'),
                experience = data.get('experience'),
                email = data.get('email')
            )

            return JsonResponse({}, status=200)

        except ValidationError as e:
            return JsonResponse({}, status=404)

        except Exception as e:
            return JsonResponse({}, status=404)

    else:
        return JsonResponse({}, status=400)

@csrf_exempt
def login(request):
    pass