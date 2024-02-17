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
            check_registration(data)
            User.objects.create(
                username=data.get("username"),
                password=make_password(data.get("password")),
                unit=data.get("unit"),
                experience=data.get("experience"),
                email=data.get("email")
            )
            return JsonResponse({}, status=200)
        
        except PasswordTooShortError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=404)
        
        except PasswordsDoNotMatchError as e:
            logger.error(str(e))
            return JsonResponse({"error": str(e)}, status=404)

        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    else:
        logger.error("Invalid request method")
        return JsonResponse({}, status=400) # invalid request method

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_login(data, token)
            return JsonResponse({}, status=200) # login successful
        
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
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

    # get all trackings for a user
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            trackings = Tracking.objects.filter(user=user)
            tracking_list = [
                {"id": str(tracking.id), "name": tracking.name, "updated": tracking.updated}
                for tracking in trackings
            ]

            return JsonResponse({"tracking_list": tracking_list}, status=200)

        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

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

    # create tracking
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            data = json.loads(request.body)
            tracking_name = data.get("tracking_name")
            check_tracking_name(tracking_name)
            user = User.objects.get(token=token)
            
            # create tracking
            tracking = Tracking.objects.create(
                name = tracking_name,
                user = user
            )
            return JsonResponse({}, status=200) # created tracking successfully
        
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

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
    
@csrf_exempt
def tracking_id(request, id):

    # get every addition related to one tracking (?)
    if request.method == 'GET':
        pass
    # add an addition to tracking (?)
    if request.method == 'POST':
        pass
    # delete tracking by id
    if request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_tracking(user, id)

            # get & delete tracking
            tracking_to_be_deleted = Tracking.objects.get(id=id)
            tracking_to_be_deleted.delete()

            return JsonResponse({}, status=200) # tracking deleted successfully

        except PermissionError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except Tracking.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
            
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
    else:
        return JsonResponse({}, status=404) # invalid request method
    
@csrf_exempt
def addition(request):

    # create addition
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            data = json.loads(request.body)

            # get json data
            tracking_id = data.get('tracking_id')
            number = data.get('number')
            unit = data.get('unit')
            note = data.get('note')

            # if tracking_id in json data is not null get the tracking object
            # else tracking will be null
            if tracking_id:
                tracking = Tracking.objects.get(id=tracking_id)
            else:
                tracking = None

            # create addition
            addition = Addition.objects.create(
                tracking=tracking,
                number=number,
                unit=unit,
                note=note,
                created=timezone.now(),
                updated=timezone.now()
            )

            return JsonResponse({}, status=200) # addition created successfully
            
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)


    else:
        return JsonResponse({}, status=404) # invalid request method
    
@csrf_exempt
def exercise(request):
    # get all exercises
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            
            exercises = Exercise.objects.filter(user=user)
            exercise_list = [
                {"id": str(exercise.id), "name": exercise.name, "updated": exercise.updated}
                for exercise in exercises
            ]

            return JsonResponse({"exercise_list": exercise_list}, status=200)

        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
    # create exercise
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            data = json.loads(request.body)
            check_exercise_name(data.get('name'))

            # create exercise
            exercise = Exercise.objects.create(
                user=user,
                name=data.get('name'),
                note=data.get('note'),
                type=data.get('type')
            )

            return JsonResponse({}, status=200) # created exercise successfully
         
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except ValidationError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    else:
        return JsonResponse({}, status=404) # invalid request method
    
@csrf_exempt
def exercise_id(request, id):
    # get details of an exercise by id
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            check_user_exercise(user, id)

            exercise = Exercise.objects.get(id=id)

            return JsonResponse({"id": exercise.id,
                                 "name": exercise.name,
                                 "updated": exercise.updated
                                 }, status=200) # got details of an exercise successfully
        
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except PermissionError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # jotain
    if request.method == 'POST':
        pass
    # delete exercise by id
    if request.method == 'DELETE':
        pass
    else:
        return JsonResponse({}, status=404) # invalid request method