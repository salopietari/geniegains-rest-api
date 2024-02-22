import json
import time
from datetime import datetime
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
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400) # invalid request method

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            check_login(data)

            user = User.objects.get(username=data.get("username"))
            return JsonResponse({"token": user.token}, status=200) # login successful
        
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
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400) # invalid request method
    
@csrf_exempt
def token_login(request):
    if request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            return JsonResponse({}, status=200) # login successful
        
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
        logger.debug(f"invalid request method: {request.method}")
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
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            data = json.loads(request.body)
            tracking_name = data.get("tracking_name")
            check_field_length('name', tracking_name, Tracking)
            user = User.objects.get(token=token)
            
            # create tracking
            tracking = Tracking.objects.create(
                name = tracking_name,
                user = user
            )
            return JsonResponse({"id": tracking.id}, status=200) # created tracking successfully
        
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
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=400) # invalid request method
    
@csrf_exempt
def tracking_id(request, id):

    # get every addition related to one tracking (?)
    if request.method == 'GET':
        pass
    # add an addition to tracking (?)
    elif request.method == 'POST':
        pass
    # delete tracking by id
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, Tracking, id)

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
        logger.debug(f"invalid request method: {request.method}")
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
        logger.debug(f"invalid request method: {request.method}")
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
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            data = json.loads(request.body)
            check_field_length('name', data.get('name'), Exercise)

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
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404) # invalid request method
    
@csrf_exempt
def exercise_id(request, id):
    # get details of an exercise by id
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            check_user_permission(user, Exercise, id)

            exercise = Exercise.objects.get(id=id)

            return JsonResponse({"id": exercise.id,
                                 "name": exercise.name,
                                 "updated": exercise.updated}, status=200) # got details of an exercise successfully
        
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
    elif request.method == 'POST':
        pass
    # delete exercise by id
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            check_user_permission(user, Exercise, id)

            # get & delete exercise
            exercise_to_be_deleted = Exercise.objects.get(id=id)
            exercise_to_be_deleted.delete()

            return JsonResponse({}, status=200) # exercise deleted successfully

        except PermissionError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except Exercise.DoesNotExist as e:
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
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404) # invalid request method
    
@csrf_exempt
def goal(request):
    # get all goals
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)

            goals = Goal.objects.filter(user=user)
            goal_list = [
                {"id": str(goal.id), "name": goal.name}
                for goal in goals
            ]

            return JsonResponse({"goal_list": goal_list}, status=200) # got all goals successfully
        
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)


    # create goal
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)
            data = json.loads(request.body)

            check_field_length('name', data.get("name"), Goal)

            normal_timestamp = convert_unix_timestamp(data.get("end"))

            goal = Goal.objects.create(
                user=user,
                name=data.get('name'),
                number=data.get('number'),
                end=normal_timestamp,
                unit=data.get('unit')
            )

            return JsonResponse({}, status=200) # goal created successfully
        
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
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404) # invalid request method
    
@csrf_exempt
def goal_id(request, id):
    # get details of a goal by id
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            goal = Goal.objects.get(id=id, user=user)

            # convert end timestamp to unix timestamp (milliseconds since the epoch)
            end_timestamp = int(time.mktime(goal.end.timetuple())) * 1000

            return JsonResponse({"id": goal.id,
                                "name": goal.name,
                                "end": end_timestamp,
                                "number": goal.number}, status=200)
        
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except ObjectDoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # jotain
    elif request.method == 'POST':
        pass
    # delete goal by id
    elif request.method == 'DELETE':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            check_user_permission(user, Goal, id)

            goal = Goal.objects.get(user=user)
            goal.delete()
            
            return JsonResponse({}, status=200) # goal deleted successfully
        
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except PermissionError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except ObjectDoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)



    else:
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404) # invalid request method
    
@csrf_exempt
def movement(request):
    # get all movement(s) ONKS TÄÄ TURHA
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            movements = Movement.objects.filter(user_id=user.id)

            movement_list = [
                {"name": movement.name}
                for movement in movements
            ]

            return JsonResponse({"movement_list": movement_list}, status=200) # got all movements successfully

        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

    # create movement
    elif request.method == 'POST':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)
            user = User.objects.get(token=token)

            data = json.loads(request.body)
            movement_name = data.get("name")
            check_field_length('name', movement_name, Movement)

            movement = Movement.objects.create(
                user=user,
                name=movement_name
            )

            return JsonResponse({}, status=200) # movement created successfully

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
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404) # invalid request method

    
@csrf_exempt
def user(request):
    # get user details
    if request.method == 'GET':
        try:
            token = request.META.get('HTTP_AUTH_TOKEN')
            check_token(token)

            user = User.objects.get(token=token)
            return JsonResponse({"username": user.username, "email": user.email, "unit": user.unit, "experience": user.experience}, status=200)

        except TokenError as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
        except User.DoesNotExist as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)

        except Exception as e:
            logger.error(str(e))
            return JsonResponse({}, status=404)
        
    # update user details
    elif request.method == 'POST':
        pass
    # delete user
    elif request.method == 'DELETE':
        pass

    else:
        logger.debug(f"invalid request method: {request.method}")
        return JsonResponse({}, status=404)

@csrf_exempt
def convert_unix_timestamp(timestamp):
    try:
        # divided unix timestamp by 1000
        timestamp /= 1000
        # convert unix time stamp to datetime object
        normal_date = datetime.fromtimestamp(timestamp)
        return normal_date
    
    except Exception as e:
        raise Exception(e)